import os
import threading
import json
from concurrent.futures import ThreadPoolExecutor
from typing import  List, Dict, Any, Tuple, Union

from llm_client import LLMClient, LLMResponse
from data_type import DistillResponse
from logger import ThreadSafeLogger
from prompt import PromptTemplates
from file_manager import FileManager

from dotenv import load_dotenv


# 配置和初始化
load_dotenv()

class QuestionGenerator:
    def __init__(self, md_dir: str, max_retries: int = 2, 
                 func_name: str = None):
      
        self.max_retries = max_retries
        
        # 创建线程专用日志器
        self.logger = ThreadSafeLogger.get_logger(func_name or f"gen_question_{threading.get_ident()}")
        
        self.llm_client = LLMClient(logger=self.logger)
        self.file_manager = FileManager(logger=self.logger)
        self.templates = PromptTemplates()
        self.conversation_history = []
        self.index = 0;
        self.md_dir = md_dir
    
    def _prepare_conversation_for_func(self, func: str) -> None:
        """准备函数的对话历史"""
        matching_md_files = self.file_manager.find_clean_doc(self.md_dir, func)
        
        if matching_md_files:
            self.logger.info(f"开始读取 {matching_md_files}")
            md_content = self.file_manager.read_with_limit(f"{matching_md_files}", 4)
            self.conversation_history.append({
                "role": "system",
                "content": md_content
            })
        else:
            raise Exception("not found")

    def gen_question(self, func: str): 
        self.conversation_history = [{
            "role": "system", 
            "content": self.templates.gen_question()
        }]

        self._prepare_conversation_for_func(func)
        llm_response = self.llm_client.generate_response(self.conversation_history)
                
                
        print(llm_response)

        if self.logger:
            self.logger.log(llm_response)

    

class DistillationOrchestrator:
    """蒸馏任务编排器"""
    
    @staticmethod
    def _process_in_thread(func: str, config: Dict[str, Any], md_dir: str) -> Tuple[str, bool]:
        """在单独的线程中处理一个函数
        
        Args:
            func: 要处理的函数名
            config: 包含连接信息的字典
            md_dir: Markdown文档目录
            
        Returns:
            Tuple[str, bool]: 函数名和处理结果
        """
        # 为此函数创建专用的日志器
        logger = ThreadSafeLogger.get_logger(func)
        logger.info(f"开始处理函数: {func}")
        
        distiller = QuestionGenerator(
            max_retries=config.get('max_retries', 2),
            func_name=func,
            md_dir = md_dir
        )
        
        try:
            result = distiller.gen_question(func)
            logger.info(f"函数 {func} 处理{'成功' if result else '失败'}")
            return func, result
        except Exception as e:
            logger.error(f"函数 {func} 处理时出现异常: {str(e)}", exc_info=True)
            return func, False

    @classmethod
    def process_functions(cls, funcs: List[str], config: Dict[str, Any], 
                          md_dir: str, max_workers: int = None) -> List[Tuple[str, bool]]:
        """使用多线程处理多个函数
        
        Args:
            funcs: 要处理的函数名列表
            config: 包含连接信息的字典
            md_dir: Markdown文档目录
            max_workers: 最大线程数，默认为None（由ThreadPoolExecutor决定）
            
        Returns:
            List[Tuple[str, bool]]: 处理结果的列表
        """
        # 创建目录（如果不存在）
        os.makedirs("./data", exist_ok=True)
        os.makedirs("./logs", exist_ok=True)
        
        # 创建主日志器
        main_logger = ThreadSafeLogger.get_logger("main")
        main_logger.info(f"开始处理 {len(funcs)} 个函数")
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_func = {
                executor.submit(cls._process_in_thread, func, config, md_dir): func 
                for func in funcs
            }
            
            # 收集结果
            for future in future_to_func:
                try:
                    func, result = future.result()
                    results.append((func, result))
                except Exception as exc:
                    func = future_to_func[future]
                    main_logger.error(f"函数 {func} 处理出现异常: {exc}")
                    results.append((func, False))
        
        # 汇总结果
        success_count = sum(1 for _, result in results if result)
        main_logger.info(f"处理完成: 共 {len(funcs)} 个函数，成功 {success_count} 个，失败 {len(funcs) - success_count} 个")
        
        return results


def main():
    """主函数"""
    # 加载环境变量
    load_dotenv()
    
    # 设置主日志器
    main_logger = ThreadSafeLogger.get_logger("main")
    main_logger.info("开始执行主程序")
    
    # 准备配置
    config = {
        'host': os.getenv("DDB_HOST"),
        'port': os.getenv("DDB_PORT"),
        'user': os.getenv("DDB_USER"),
        'passwd': os.getenv("DDB_PASSWD"),
        'max_retries': 2
    }

    # SQL相关函数
    functions = [ "ns", "condValueAtRisk", "nsspredict", "valueAtRisk"  ]
    
    clean_doc_dir = "./cleandocs"
    main_logger.info(f"开始处理 SQL 函数: {functions}")
    sql_results = DistillationOrchestrator.process_functions(
        functions, config, clean_doc_dir, max_workers=1
    )


    success_count = sum(1 for _, result in sql_results if result)
    main_logger.info(
        f"SQL函数处理完成: 共 {len(functions)} 个函数，"
        f"成功 {success_count} 个，失败 {len(functions) - success_count} 个"
    )
    
    main_logger.info("主程序执行完毕")


if __name__ == "__main__":
    main()

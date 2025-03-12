import os
import threading
import json
from concurrent.futures import ThreadPoolExecutor
from typing import  List, Dict, Any, Tuple, Union

from llm_client import LLMClient, LLMResponse
from data_type import DistillResponse
from logger import ThreadSafeLogger
from ddb import DatabaseSession
from prompt import PromptTemplates
from file_manager import FileManager

from dotenv import load_dotenv

# 配置和初始化
load_dotenv()


class FunctionDistiller:
    """函数蒸馏器，用于生成函数的示例和文档"""
    
    def __init__(self, host: str, port: int, user: str, passwd: str, 
                 md_dir: str, unittest_dir: str = None, max_retries: int = 2, 
                 func_name: str = None):
        """初始化函数蒸馏器
        
        Args:
            host: 数据库主机
            port: 数据库端口
            user: 数据库用户名
            passwd: 数据库密码
            md_dir: Markdown文档目录
            unittest_dir: 单元测试目录
            max_retries: 最大重试次数
            func_name: 函数名称，用于日志标识
        """
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.max_retries = max_retries
        self.md_dir = md_dir
        self.unittest_dir = unittest_dir or "/home/jzchen/zhiyu/dolphindb_test/testing/unit_testing/"
        
        # 创建线程专用日志器
        self.logger = ThreadSafeLogger.get_logger(func_name or f"distiller_{threading.get_ident()}")
        
        self.llm_client = LLMClient(logger=self.logger)
        self.file_manager = FileManager(logger=self.logger)
        self.templates = PromptTemplates()
        self.conversation_history = []
    
    def _parse_llm_response(self, llm_response: LLMResponse) -> Union[DistillResponse, str]:
        """解析LLM响应为DistillResponse对象
        
        Args:
            llm_response: LLM的原始响应
            
        Returns:
            Union[DistillResponse, str]: 解析后的对象或错误消息
        """
        if not llm_response.success:
            return f"API错误: {llm_response.error_message}"
        
        try:
            parsed_content = json.loads(llm_response.content)
            return DistillResponse(**parsed_content)
        except json.JSONDecodeError as e:
            error_msg = f"JSON解析错误: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"响应对象创建错误: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return error_msg
    
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


    def _generate_output_file(self, distill_resp: DistillResponse) -> None:
        """生成函数的输出文件"""
        combined_content = "\n".join([
            self.templates.doc_question_prompt(distill_resp.question)
        ] + [entry["content"] for entry in self.conversation_history[1:-1]])

        template_content = f"""\
Prompt: 
{distill_resp.question}

Input: 
```DolphinDB
{distill_resp.input}
```

Answer: 
```DolphinDB
{distill_resp.answer}
```

R1 CoT: 
{distill_resp.cot}

Correct CoT: 
{distill_resp.cot}

Function Name: 
{distill_resp.function}
"""
        output_file = f"./data/jinzhi_{distill_resp.function}.txt"
        
        with open(output_file, "w") as file:
            file.write(template_content)
        
        self.logger.info(f"已生成输出文件: {output_file}")
    

    def _mock_distill_process(self, func: str) -> Union[DistillResponse, bool]:
        """模拟蒸馏过程，用于预实验"""
        if os.path.exists(f"./data/jinzhi_{func}.txt"): 
            self.logger.info(f"{func}已生成，无需再处理")
            return True

        self.conversation_history = [{"role": "system", "content": self.templates.mock_distill()}]
        self._prepare_conversation_for_func(func)

        try_count = 0
        success = False

        with DatabaseSession(self.host, self.port, self.user, self.passwd, logger=self.logger) as db:
            while try_count < self.max_retries and not success:
                try_count += 1
                self.logger.info(f"开始第{try_count}次尝试")
                
                 # 获取LLM响应
                llm_response = self.llm_client.generate_response(self.conversation_history)
                
                # 解析响应
                response_data = self._parse_llm_response(llm_response)
                
                # 处理解析结果
                if isinstance(response_data, str):  # 错误情况
                    self.logger.error(f"LLM响应解析失败: {response_data}")
                    self.conversation_history.append({
                        "role": "user",
                        "content": "请重新按要求生成有效的JSON格式响应"
                    })
                    continue
                
                # 如果成功解析为DistillResponse对象
                input_ok = False 
                answer_ok = False

                if hasattr(response_data, "input") and hasattr(response_data, "answer"):
                    self.logger.info("准备测试生成脚本正确性")
                    
                    input_ok, rsp = db.execute(response_data.input)
                    if not input_ok:
                        self.logger.error(f"数据脚本错误：{rsp}")
                        self.conversation_history.append({
                            "role": "user",
                            "content": f"重新思考下，上面input有这个报错:{rsp}"
                        })
                    
                    answer_ok, rsp = db.execute(response_data.answer)
                    if not answer_ok:
                        self.logger.error(f"解答脚本错误：{rsp}")
                        self.conversation_history.append({
                            "role": "user",
                            "content": f"重新思考下，上面answer有这个报错:{rsp}"
                        })
                else:
                    self.conversation_history.append({
                        "role": "user",
                        "content": f"请重新按要求生成"
                    })

                if input_ok and answer_ok:
                    self.logger.info("脚本正常，准备生成文件")
                    response_data.cot = llm_response.reasoning_content
                    self._generate_output_file(response_data)
                    return response_data
        
        return False

    def _distill_via_llm(self, func: str, resp: DistillResponse) -> bool:
        """通过LLM进行蒸馏"""
        if os.path.exists(f"./data/jinzhi_{func}.txt"): 
            self.logger.info(f"{func}已生成，无需再处理")
            return True
            
        self.conversation_history = [{
            "role": "system", 
            "content": self.templates.question_prompt(resp.question)
        }]
        
        self._prepare_conversation_for_func(func)

        try_count = 0
        success = False

        with DatabaseSession(self.host, self.port, self.user, self.passwd, logger=self.logger) as db:
            while try_count < self.max_retries and not success:
                try_count += 1
                self.logger.info(f"开始第{try_count}次尝试")
                
                 # 获取LLM响应
                llm_response = self.llm_client.generate_response(self.conversation_history)
                
                # 解析响应
                response_data = self._parse_llm_response(llm_response)
                
                # 处理解析结果
                if isinstance(response_data, str):  # 错误情况
                    self.logger.error(f"LLM响应解析失败: {response_data}")
                    self.conversation_history.append({
                        "role": "user",
                        "content": "请重新按要求生成有效的JSON格式响应"
                    })
                    continue
                
                # 如果成功解析为DistillResponse对象
                input_ok = False 
                answer_ok = False

                if hasattr(response_data, "input") and hasattr(response_data, "answer"):
                    self.logger.info("准备测试生成脚本正确性")
                    
                    input_ok, rsp = db.execute(response_data.input)
                    if not input_ok:
                        self.logger.error(f"数据脚本错误：{rsp}")
                        self.conversation_history.append({
                            "role": "user",
                            "content": f"重新思考下，上面input有这个报错:{rsp}"
                        })
                    
                    answer_ok, rsp = db.execute(response_data.answer)
                    if not answer_ok:
                        self.logger.error(f"解答脚本错误：{rsp}")
                        self.conversation_history.append({
                            "role": "user",
                            "content": f"重新思考下，上面answer有这个报错:{rsp}"
                        })
                else:
                    self.conversation_history.append({
                        "role": "user",
                        "content": f"请重新按要求生成"
                    })

                if input_ok and answer_ok:
                    self.logger.info("脚本正常，准备生成文件")
                    response_data.cot = llm_response.reasoning_content
                    self._generate_output_file(response_data)
                    return True
        
        return False

    def distill_function(self, func: str) -> bool:
        """蒸馏函数，生成示例和文档
        
        Args:
            func: 函数名
            
        Returns:
            bool: 是否成功
        """
        mock_response_data = self._mock_distill_process(func)
        
        if isinstance(mock_response_data, bool):
            return mock_response_data
            
        self.logger.info("模型预实验成功，开始生成标注数据")
        #return self._distill_via_llm(func, mock_response_data)


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
        
        distiller = FunctionDistiller(
            host=config['host'], 
            port=config['port'], 
            user=config['user'], 
            passwd=config['passwd'],
            md_dir=md_dir,
            max_retries=config.get('max_retries', 2),
            func_name=func
        )
        
        try:
            result = distiller.distill_function(func)
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
    functions = [
        "bondAccrInt", "bondConvexity", "bondDirtyPrice", "bondDuration", "nss", 
        "ns", "condValueAtRisk", "nsspredict", "trueRange", "valueAtRisk",
        "irs", "varma", "bondCashflow", "bondYield", "createPricingEngine", 
        "treasuryConversionFactor", "crmwCBond", "cds", "vanillaOption", 
        "maxDrawdown", "mdd", "cummdd", "createYieldCurveEngine", "appendForPrediction"
    ]
    clean_doc_dir = "./cleandocs"
    main_logger.info(f"开始处理 SQL 函数: {functions}")
    sql_results = DistillationOrchestrator.process_functions(
        functions, config, clean_doc_dir, max_workers=10
    )


    success_count = sum(1 for _, result in sql_results if result)
    main_logger.info(
        f"SQL函数处理完成: 共 {len(functions)} 个函数，"
        f"成功 {success_count} 个，失败 {len(functions) - success_count} 个"
    )
    
    main_logger.info("主程序执行完毕")


if __name__ == "__main__":
    main()

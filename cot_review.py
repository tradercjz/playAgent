
from llm_client import LLMClient, LLMResponse
from dotenv import load_dotenv
from file_manager import FileManager
import html2text
from prompt import PromptTemplates
import os
import threading
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils import parse_markdown_to_json, json_to_markdown_file

# 配置和初始化
load_dotenv()


def process_file(file_path):
    """
    处理单个文件的函数：读取文件内容并打印
    
    Args:
        file_path: 文件的完整路径
    """
    try:
        # 获取线程ID，用于演示
        thread_id = threading.get_ident()
        print(f"线程 {thread_id} 开始处理文件: {file_path}")

        result =  parse_markdown_to_json(file_path)

        llm_client = LLMClient()
        llm_result = llm_client.generate_response([
            {
                "role": "system",
                "content": PromptTemplates.cot_reviwer()
            }, {
                "role": "user",
                "content": result["R1 CoT"]
            }
        ])

        if llm_result.success:
            result["R1 CoT"] = llm_result.content
            result["Correct CoT"] = llm_result.content
            json_to_markdown_file(result, f"trans/{file_path}")
            print(f"Successfully processed {file_path}")
          
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {str(e)}")
        return None

def main():
    dir="./data"
    max_workers = 10
   
    # 检查目录是否存在
    if not os.path.isdir(dir):
        print(f"错误: '{dir}' 不是一个有效的目录")
        return
    
    # 获取目录下所有文件
    all_files = []
    for root, _, files in os.walk(dir):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                all_files.append(file_path)
    
    if not all_files:
        print(f"目录 '{dir}' 中没有找到文件")
        return
    
    print(f"找到 {len(all_files)} 个文件，使用 {max_workers} 个线程进行处理")
    
    # 使用线程池处理所有文件
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务到执行器
        future_to_file = {executor.submit(process_file, file_path): file_path for file_path in all_files}
        
        # 处理完成的结果
        completed = 0
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                result = future.result()
                if result:
                    completed += 1
            except Exception as exc:
                print(f"文件 {file_path} 生成了异常: {exc}")
    
    end_time = time.time()
    
    print(f"\n处理完成: 成功处理 {completed}/{len(all_files)} 个文件")
    print(f"总耗时: {end_time - start_time:.2f} 秒")

if __name__ == "__main__":
    main()
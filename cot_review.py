
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

# 配置和初始化
load_dotenv()

def parse_markdown_to_json(markdown_file_path):
    """
    解析 Markdown 文件，提取 Prompt, Answer 等内容，返回包含内容的字典
    （改进正则表达式，修复空内容导致的匹配错误）
    """
    try:
        with open(markdown_file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    except FileNotFoundError:
        print(f"错误：文件未找到：{markdown_file_path}")
        return None

    data = {}
    sections = ["Prompt", "Input", "Answer", "R1 CoT", "Correct CoT", "Function Name"]
    next_sections = {
        "Prompt": "Input",
        "Input": "Answer",
        "Answer": "R1 CoT",
        "R1 CoT": "Correct CoT",
        "Correct CoT": "Function Name",
        "Function Name": None
    }

    for section in sections:
        next_section_tag = next_sections[section]
        
        # 构建匹配模式
        if next_section_tag:
            # 匹配从当前section到下一个section标签行之间的内容
            pattern = re.compile(
                rf'^{section}:\s*$\n(.*?)(?=^\s*{next_section_tag}:\s*$|\Z)',
                re.DOTALL | re.MULTILINE
            )
        else:
            # 最后一个section匹配到文件末尾
            pattern = re.compile(
                rf'^{section}:\s*$\n(.*)',
                re.DOTALL | re.MULTILINE
            )

        match = pattern.search(markdown_content)
        if match:
            # 提取内容并去除首尾空白
            content = match.group(1).strip()
            data[section] = content
        else:
            data[section] = ""

    return data


def json_to_markdown_file(json_data, output_file_path):
    """
    将JSON数据转换为Markdown格式并写入文件
    
    参数:
        json_data (dict): 包含各部分内容的字典，应有以下键：
                         "Prompt", "Input", "Answer", "R1 CoT", "Correct CoT", "Function Name"
        output_file_path (str): 输出Markdown文件的路径
    
    返回:
        bool: 操作是否成功
    """
    try:
        # 定义各部分的顺序
        sections = ["Prompt", "Input", "Answer", "R1 CoT", "Correct CoT", "Function Name"]
        
        # 构建Markdown内容
        markdown_content = ""
        
        for section in sections:
            # 检查字典中是否存在该部分内容
            if section in json_data:
                content = json_data[section]
                # 添加部分标题和内容
                markdown_content += f"{section}:\n{content}\n\n"
            else:
                # 如果字典中没有该部分，添加空内容
                markdown_content += f"{section}:\n\n"
        
        # 写入文件
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content.rstrip())  # 移除最后多余的换行符
        
        print(f"成功将JSON数据写入到文件: {output_file_path}")
        return True
        
    except Exception as e:
        print(f"写入Markdown文件时出错: {str(e)}")
        return False


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
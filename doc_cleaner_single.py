
from typing import List, Any,Callable, Dict
from dataclasses import dataclass
import concurrent.futures
import os
from pathlib import Path



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


@dataclass
class Document:
    """文档数据类，存储文件内容和元数据"""
    filepath: str
    filename: str
    extension: str
    content: str
    metadata: Dict[str, Any] = None
    encoding: str = "utf-8"
    size: int = 0

EmptyAnswerDocs = []

def clean_dict(data):
    """
    清洗数据字典，对于每个 section，保留第一个非空的值。
    
    :param data: 解析后的数据字典，包含各个 section 的内容。
    :return: 清洗后的数据字典，每个 section 保留第一个非空的值。
    """

    keep = True
    for section, values in data.items():
        # 对每个 section 的内容进行处理，找到第一个非空值
        flag = True
        for idx, value in enumerate(values):
            if value.strip():  # 如果该值不是空字符串
                data[section] = value.strip()  # 保留第一个非空值
                flag = False
                break  # 找到非空值后，跳出循环，避免继续查找
        
        # 如果所有值都为空，设置为空列表或None
        if flag:
            data[section] = ''
            # Answer为空不保留
            if section == "Answer":
                keep = False
    
    return keep, data



def parse_markdown_to_json_all(markdown_content):
    """
    解析 Markdown 文件，提取各个 section（如 Prompt, Answer 等）内容，返回包含内容的字典
    支持乱序、重复的 section。
    """
    sections = ["Prompt", "Input", "Answer", "R1 CoT", "Correct CoT", "Function Name"]

    data = {section: [] for section in sections}

    lines = markdown_content.splitlines()  # 按行分割字符串内容

    current_section = None
    current_content = []

    for line in lines:
        line = line.strip()  # 去除首尾空白

        # 检查该行是否是某个 section 的开头
        if any(line.startswith(f"{section}:") for section in sections):
            # 如果有正在收集的内容，保存当前内容
            if current_section:
                data[current_section].append("\n".join(current_content).strip())
            
            # 找到新的 section，初始化
            for section in sections:
                if line.startswith(f"{section}:"):
                    current_section = section
                    break
            
            # 初始化当前内容收集
            current_content = [line[len(f"{current_section}:"):].strip()]
        elif current_section:
            # 如果当前正在收集内容，继续收集
            current_content.append(line)

    # 最后一次的内容保存
    if current_section:
        data[current_section].append("\n".join(current_content).strip())

    return data



def get_file_contents(directory: str, extensions: List[str] = None, encoding: str = "utf-8") -> List[Document]:
    """
    遍历目录获取所有子文件内容
    
    Args:
        directory: 要遍历的目录路径
        extensions: 可选，指定要读取的文件扩展名列表(如 ['.txt', '.csv'])
        
    Returns:
        包含文件信息的
    """
    file_contents = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            filename, extension = os.path.splitext(file)

            # 如果指定了扩展名过滤且当前文件扩展名不在列表中，则跳过
            if extensions and extension.lower() not in [ext.lower() for ext in extensions]:
                continue
                
            try:
                # 使用pathlib获取更准确的文件信息
                file_obj = Path(filepath)
                size = file_obj.stat().st_size

                with open(filepath, 'r', encoding=encoding) as f:
                    content = f.read()
                    file_contents.append(Document(
                        filepath=filepath,
                        filename=filename,
                        extension=extension,
                        content=content,
                        metadata={
                            'size': size,
                            'modified_time': file_obj.stat().st_mtime
                        },
                        encoding=encoding,
                        size=size
                    ))
            except Exception as e:
                print(f"读取文件 {filepath} 失败: {e}")
                continue
                
    return file_contents
    
def process_file_content(doc: Document, clean_dir: str="./cleanDocX/") -> Any:
    """
    处理单个分组的数据
    
    Args:
        doc: 文档内容
        
    Returns:
        处理结果
    """

    parsedObj = parse_markdown_to_json_all(doc.content)

    keep, cleanObj = clean_dict(parsedObj)
    if keep:
        json_to_markdown_file(cleanObj,f"{clean_dir}{doc.filename}")
        return {"doc": doc.filename, "status": "processed"}
    else:
        EmptyAnswerDocs.append(doc.filename)
        return {"doc": doc.filename, "status": "Answer is empty, skip"}

def parallel_process_files(
    file_contents: List[Document],
    process_func: Callable[[Document], Any],
    max_workers: int = None
) -> List[Any]:
    """
    并行处理文件内容
    
    Args:
        file_contents: 文件内容列表
        process_func: 处理单个文件的函数
        max_workers: 最大并行工作线程数
        
    Returns:
        所有文件处理结果的列表
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_func, file_info) for file_info in file_contents]
        
        results = []
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                print(f"处理文件时发生错误: {exc}")
                
    return results

if __name__ == "__main__":
    # 示例用法
    target_directory = "./0/"  # 替换为您的目录路径
    
    # 1. 获取所有文件内容
    all_files = get_file_contents(target_directory, extensions=['.md'])
    print(f"找到 {len(all_files)} 个文件准备处理")

    # 2. 并行处理文件
    results = parallel_process_files(
        file_contents=all_files,
        process_func=process_file_content,
        max_workers=10
    )
    
    # 显示处理结果
    print("\n处理结果:")
    for result in results:
        print(f"文件 '{result['doc']}' 处理状态: {result['status']}")
    
    print(f"Anwser为空的文件: {EmptyAnswerDocs}")

from typing import List, Any,Callable, Dict
from llm_prompt import llm, LLMResponse
from dataclasses import dataclass
import concurrent.futures
from dotenv import load_dotenv
import os
from pathlib import Path


load_dotenv()

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

@llm.prompt()
def clean_doc(docStr: str) -> LLMResponse:
    """
    根据如下的要求，来清洗文档。要求只是做格式上的删除或者调整处理，内容意思不变。
    规则为：
    1. Answer里面有额外字段，如Input, Function Name, Prompt。这种情况，删除额外字段即可。
    2. Answer里面没有实际回答。这种情况，删除整个文件即可。
    3. Function Name后还有一些额外的文字，如Prompt。这种情况，删除额外字段即可。
    4. 问题/回答是英文的。这种情况，删除整个文件即可。

    要求：最后的文件里，只有一个Prompt:段，一个Input:段，一个Answer: 段，一个Function Name: 段。
    且每一段都有内容，内容与原来的相同。只是把重复的去掉

    文档内容为：
    {{ docStr }}
    """

    return {"docStr": docStr}

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

def write_str_to_file(filepath: str, content: str, encoding: str = 'utf-8') -> bool:
    """
    将字符串写入文件（覆盖模式）
    
    Args:
        filepath: 文件路径
        content: 要写入的字符串内容
        encoding: 文件编码（默认utf-8）
        
    Returns:
        bool: 是否写入成功
    """
    try:
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except IOError as e:
        print(f"写入文件失败: {e}")
        return False
    
def process_file_content(doc: Document, clean_dir: str="./cleanDocX/") -> Any:
    """
    处理单个分组的数据
    
    Args:
        doc: 文档内容
        
    Returns:
        处理结果
    """
    result = clean_doc(doc.content)
    if result.success:
        write_str_to_file(f"{clean_dir}{doc.filename}", result.content)
    
    else:
        print(f"Handle {doc.filename} error, {result.error_m}")
    
    return {"doc": doc.filename, "status": "processed"}

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

import re

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

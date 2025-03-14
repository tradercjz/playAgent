from typing import Dict, Any
import requests

from llm_prompt import llm

@llm.prompt()
def test(text: str) -> str:
    """
    {{ text }}
    """
   

# 定义一个简单的摘要生成函数
@llm.prompt()
def generate_summary(text: str, max_words: int = 100) -> Dict[str, Any]:
    """
    请为以下文本生成一个简洁的摘要:
    
    {{ text }}
    
    摘要要求:
    1. 不超过{{ max_words }}个词
    2. 保留原文的关键信息
    3. 使用简明清晰的语言
    """
    return {
        "text": text,
        "max_words": max_words
    }

# 定义一个函数来获取网页内容
def get_webpage_content(url: str) -> str:
    """获取网页内容"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        # 这里简化处理，实际应用可能需要更复杂的HTML解析
        return response.text[:1000] + "..." # 简化，只取前1000个字符
    except Exception as e:
        return f"获取网页内容失败: {str(e)}"

# 主函数
def main():
    # 1. 获取要摘要的网页
    #url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
    #print(f"获取网页内容: {url}")
    #content = get_webpage_content(url)
    
    # 2. 生成摘要
    #print("正在生成摘要...")
    #summary = generate_summary("this is a test", max_words=50)
    
    # # 3. 显示结果
    # print("\n=== 生成的摘要 ===")
    # print(summary)
    
    # # 4. 查看原始提示模板（用于调试）
    # print("\n=== 使用的提示模板 ===")
    # print(generate_summary.prompt_template)
    result = test("你是谁")
    print(result)

if __name__ == "__main__":
    main()

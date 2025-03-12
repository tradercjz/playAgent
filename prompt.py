
from textwrap import dedent

class PromptTemplates:
    """提示词模板集合"""
    
    @staticmethod
    def html_doc_clean() -> str:
        """用于清洗md数据"""
        return dedent("""\
            根据用户提供的文档内容，提取出其中的关键内容。去掉一些无关的链接之类的。里面示例部分的代码，请使用DolphinDB来包裹，严格使用DolphinDB哦，不要转为小写
            """)
    
    @staticmethod
    def mock_distill() -> str:
        """用于函数模拟蒸馏的提示词模板"""
        return dedent("""\
            你是DolphinDB专家，非常熟悉DolphinDB的语法。参考所给出的函数资料，熟悉里面的用法，提出一个这个函数相关的使用问题。
            之后，要求使用DolphinDB脚本，给出相关的模拟数据数据，同时使用dolphindb脚本，给出问题的解法
            你的问题，要求是跟参考资料的函数相关的，引导用户使用这个函数                    
            实在搞不定你就用文档的函数调用例子呗。使用案例，只生成一个函数调用就够了
                      
            对于问题，要求问题中，尽量不出现这个函数名称，而是跟函数使用相关。
            对于生成的input数据，要注意dolphindb的语法，不支持变量连写，不同变量赋值写多行
                      
            可以先参考下你已经知道的金融知识，分析下这个函数相关性来回答
            如果一些函数，文档里提到要与其他函数联动使用，那么答案需要给出完全的代码，也要包含其他函数。这个要重点参考例子了.
            
            如果你尝试使用dict,请严格参考如下语法说明和示例,并且一步步赋值来做，不要合并在一起：

            ```DolphinDB
            dict(keyObj, valueObj, [ordered=false])
            ```
            #### 参数
            `keyObj`：键向量  
            `valueObj`：值向量  

            返回无序或有序字典对象。无序字典在遍历时顺序不固定，有序字典按输入顺序维护键值对。

            #### 示例

            ```DolphinDB
            x = [1, 6, 3]
            y = [4.5, 7.8, 4.3]
            z = dict(x, y)
            z; 


            你需要提供如下的格式的输出：
            {
                "function":"参考资料的函数名称",
                "question": "针对这个函数的使用问题",
                "input": "使用dolphindb模拟的数据",
                "answer": "根据input的数据和question，使用dolphindb脚本编写function使用案例"
            }                
            
            输出的时候，不要有 json包裹，直接从 {开始输出。输出}之后，就结束，后续不要任何输出。
        """)
    
    @staticmethod
    def system_doc() -> str:
        """用于文档系统的提示词模板"""
        return dedent("""\
            你是DolphinDB专家，非常熟悉DolphinDB的语法。参考所给出的函数资料，熟悉里面的用法，并结合一些金融业务场景，提出一个这个函数相关的使用问题。
            之后，要求使用DolphinDB脚本，给出相关的模拟数据数据，同时使用dolphindb脚本，给出问题的解法（即相关金融场景的使用案例）
            你需要提供深刻的，良好结构的输出，并解析你的思路。
        """)
    
    @staticmethod
    def question_prompt(question: str) -> str:
        """基于用户问题的提示词模板"""
        return dedent(f"""\
            你是DolphinDB专家，非常熟悉DolphinDB的语法。根据所给的函数参考资料（资料包含了函数说明和测试用例，重点参考函数说明）来使用函数解决用户问题。
            用户问题为: {question}

            你需要提供如下的格式的输出：
            {{
                "function":"参考资料的函数名称",
                "question": "用户的问题",
                "input": "使用dolphindb模拟的数据",
                "answer": "根据input的数据和question，使用dolphindb脚本编写function使用案例"
            }}        
            输出的时候，不要有 json包裹，直接从 {{ 开始输出。输出}}之后，就结束，后续不要任何输出。   
        """)
    
    @staticmethod
    def doc_question_prompt(question: str) -> str:
        """文档类问题的提示词模板"""
        return dedent(f"""\
            你是DolphinDB专家，非常熟悉DolphinDB的语法。参考所给出的函数资料，熟悉里面的用法。并使用对应的资料函数来回答用户的问题：{question}。
            你需要提供深刻的，良好结构的输出，并解析你的思路。
        """)

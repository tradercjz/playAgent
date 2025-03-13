
from textwrap import dedent
from typing import  List

class PromptTemplates:
    """提示词模板集合"""

    @staticmethod
    def cot_reviwer() -> str:
        """ 用来清洗整理cot """
        return dedent("""\
            请修改下面的思维链，首先要保证意思不变，尽量不要改动。主要是讲可能表现出用户提示的意思修改掉，尽量改为完整的思考链路，没有用户提示的那种。
            """)
    
    @staticmethod
    def html_doc_clean() -> str:
        """用于清洗md数据"""
        return dedent("""\
            根据用户提供的文档内容，提取出其中的关键内容。去掉一些无关的链接之类的。里面示例部分的代码，请使用DolphinDB来包裹，严格使用DolphinDB哦，不要转为小写
            """)
    
    @staticmethod
    def gen_question() -> str:
        """ 生成问题 """
        return dedent("""\
            你是DolphinDB专家，非常熟悉DolphinDB的语法。参考所给出的函数资料，熟悉里面的用法，提出20个这个函数相关的使用问题。
            要求这5个问题尽量不同，尽量覆盖各个参数的使用，但是问题里面不能直接包含这个函数。而是需要跟金融或者实际的业务场景有关。
            同时针对每个问题，设计一些输入数据放到input，并且把问题的计算脚本（使用dolphindb)，放到answer
            

            你需要提供如下的格式的输出：
            {
                "function":"参考资料的函数名称",
                "question": ["针对这个函数的使用问题的数组，每个问题一项"],
                "input": ["使用dolphindb模拟的数据,每个问题一项"],
                "answer": ["每一项的问题的答案"]
                    
            }                
            
            输出的时候，不要有 json包裹，直接从 {开始输出。输出}之后，就结束，后续不要任何输出。
            """)

    @staticmethod
    def mock_distill_unique(inputs: List[str], answers: List[str]) -> str:
         return dedent(f"""\
            你是DolphinDB专家，非常熟悉DolphinDB的语法。参考所给出的函数资料，熟悉里面的用法，提出一个这个函数相关的使用问题。
            之后，要求使用DolphinDB脚本，给出相关的模拟数据数据，同时使用dolphindb脚本，给出问题的解法
            你的问题，要求是跟参考资料的函数相关的，引导用户使用这个函数                    
             
                      
            对于问题，要求问题中，尽量不出现这个函数名称，而是跟函数使用相关。
            对于生成的input数据，要注意dolphindb的语法，不支持变量连写，不同变量赋值写多行
                       
            需要注意的是，生成的问题和对应的解决方案，不能和以下的已有问题和答案相同，要提出不同的问题来使用测试这个函数的不同参数。

            已有问题：{','.join( inputs)}
            已有答案：{','.join( answers)}
                      
            可以先参考下你已经知道的金融知识，分析下这个函数相关性来回答
            如果一些函数，文档里提到要与其他函数联动使用，那么答案需要给出完全的代码，也要包含其他函数。这个要重点参考例子了.
                      
            如果涉及到一些交易日历的参数的选择，请不要随意发挥，因为ddb的有点不一样，就从以下参数选：
             SSE SZSE 
            
            如果你尝试使用dict,请严格参考如下语法说明和示例,并且一步步赋值来做，不要合并在一起：

            如果你需要调用matrix函数生成矩阵，请参考下面用法：
   
            #### 语法
            ```dolphindb
            matrix(X1, [X2], ...)
            ```
            #### 参数说明
            - **X1, X2, ...**：支持向量、矩阵、表（不含SYMBOL字段）、元组或它们的组合

          
            matrix(1 2 3 4, 5 6 7 9, 11 12 13 14);
            一定要注意，matrix的每一个参数都是一个向量，各个参数向量要等长要等长啊啊
                      
            另外一个注意点，参数如果是有'c'这样的字符串，请改为"c"，即使用双引号。这个是dolphindb参数注意点哦

            另外，对于使用ns或者nss的函数的，你得仔细参考文档参数说明，发掘各个参数的联系，不要用错参数。

            你需要提供如下的格式的输出：
            {{
                "function":"参考资料的函数名称",
                "question": "针对这个函数的使用问题",
                "input": "使用dolphindb模拟的数据",
                "answer": "根据input的数据和question，使用dolphindb脚本编写function使用案例"
            }}              
            
            输出的时候，不要有 json包裹，直接从 {{开始输出。输出}}之后，就结束，后续不要任何输出。
        """)
    
    @staticmethod
    def mock_distill() -> str:
        """用于函数模拟蒸馏的提示词模板"""
        return dedent("""\
            你是DolphinDB专家，非常熟悉DolphinDB的语法。参考所给出的函数资料，熟悉里面的用法，提出一个这个函数相关的使用问题。
            之后，要求使用DolphinDB脚本，给出相关的模拟数据数据，同时使用dolphindb脚本，给出问题的解法
            你的问题，要求是跟参考资料的函数相关的，引导用户使用这个函数                    
             
                      
            对于问题，要求问题中，尽量不出现这个函数名称，而是跟函数使用相关。
            对于生成的input数据，要注意dolphindb的语法，不支持变量连写，不同变量赋值写多行
                      
            可以先参考下你已经知道的金融知识，分析下这个函数相关性来回答
            如果一些函数，文档里提到要与其他函数联动使用，那么答案需要给出完全的代码，也要包含其他函数。这个要重点参考例子了.
                      
            如果涉及到一些交易日历的参数的选择，请不要随意发挥，因为ddb的有点不一样，就从以下参数选：
             SSE SZSE 
            
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
            
            如果你需要调用matrix函数生成矩阵，请参考下面用法：
   
            #### 语法
            ```dolphindb
            matrix(X1, [X2], ...)
            ```
            #### 参数说明
            - **X1, X2, ...**：支持向量、矩阵、表（不含SYMBOL字段）、元组或它们的组合

          
            matrix(1 2 3 4, 5 6 7 9, 11 12 13 14);
            一定要注意，matrix的每一个参数都是一个向量，各个参数向量要等长要等长啊啊
                      
            另外一个注意点，参数如果是有'c'这样的字符串，请改为"c"，即使用双引号。这个是dolphindb参数注意点哦

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
    def question_prompt_distinct(question: str, input: List[str], answer: List[str]) -> str:
        """基于用户问题的提示词模板"""
        return dedent(f"""\
            你是DolphinDB专家，非常熟悉DolphinDB的语法。根据所给的函数参考资料（资料包含了函数说明和测试用例，重点参考函数说明）来使用函数解决用户问题。
            用户问题为: {question}

            需要注意的是，生成的问题和对应的解决方案，不能和以下的已有问题和答案相同，要提出不同的问题来使用测试这个函数的不同参数。

            已有问题：{','.join( input)}
            已有答案：{','.join( answer)}

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

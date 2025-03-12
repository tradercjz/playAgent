
from pydantic import BaseModel
from typing import Optional

class DistillResponse(BaseModel):
    """模型生成的蒸馏响应数据结构"""
    function: str
    question: str 
    input: str 
    answer: str
    cot: Optional[str] = None

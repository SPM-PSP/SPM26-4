from pydantic import BaseModel, Field
from typing import List, Optional

class QuestionData(BaseModel):
    """
    单个面试题目数据模型。
    用于封装单个面试题目的详细信息，支持从ORM对象直接映射。
    """
    ID: int
    degree: str
    question: str
    answer: str

    class Config:
        from_attributes = True # 允许从 ORM 对象创建 Pydantic 模型

class QuestionListResponse(BaseModel):
    """
    获取面试题目列表的响应模型。
    统一封装面试题目列表查询请求的返回结果结构。
    """
    code: int = Field(..., description="响应状态码")
    message: str = Field(..., description="响应消息")
    # 面试题目列表，当请求成功时返回，包含多个QuestionData对象
    data: Optional[List[QuestionData]] = Field(None, description="面试题目列表")


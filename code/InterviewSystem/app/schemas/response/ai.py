from pydantic import BaseModel, Field
from typing import Optional

class AIAssistantResponseData(BaseModel):
    """
    AI 助手回答数据模型。
    """
    answer: str = Field(..., description="回答内容")
    datetime: str = Field(..., description="回答时间 (YYYY-MM-DD HH:MM:SS)")

class AIAssistantResponse(BaseModel):
    """
    AI 助手接口的最终响应模型。
    """
    code: int = Field(..., description="响应状态码")
    message: str = Field(..., description="响应消息")
    data: Optional[AIAssistantResponseData] = Field(None, description="AI 助手回答数据")


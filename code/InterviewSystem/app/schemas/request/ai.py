from pydantic import BaseModel, Field

class AIAssistantRequest(BaseModel):
    """
    AI 助手提问请求模型。
    """
    question: str = Field(..., min_length=1, description="用户提问内容")


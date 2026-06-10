from pydantic import BaseModel, Field
from typing import Optional

# 在这里定义了检查简历存在性后像前端返回的规范化的数据结构
class ResumeCheckResponse(BaseModel):
    user_id: str = Field(..., description="用户账号ID")
    resume_path: Optional[str] = Field(None, description="简历文件路径，如果不存在则为 null")
    message: str = Field(None, description="操作结果消息")
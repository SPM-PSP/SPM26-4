from pydantic import BaseModel, Field

# 在这里定义了检查简历存在性的前端请求的标准结构，就只是一个user_id:str
class ResumeCheckRequest(BaseModel):
    """
    请求模型，用于规范/interview/check_resume接口的查询参数。
    """
    user_id: str = Field(..., description="要检查简历的用户账号ID")

from pydantic import BaseModel, Field
from typing import Optional

class LoginSuccessData(BaseModel):
    """登录成功后返回的用户数据模型"""
    accountID: str
    nickName: str
    # 认证令牌，用于后续API请求的身份验证
    token: str = Field(..., description="JWT或其他认证token")

class LoginResponse(BaseModel):
    """登录响应模型"""
    code: int = Field(..., description="响应状态码")
    message: str = Field(..., description="响应消息")
    # 可选数据字段，仅在登录成功(code=200)时返回
    data: Optional[LoginSuccessData] = Field(None, description="登录成功时返回的数据")


from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserRegisterRequest(BaseModel):
    """
    用户注册请求模型，用于接收用户注册时提交的数据。
    继承自BaseModel，使用pydantic进行数据验证和序列化。
    """
    accountID: str = Field(..., min_length=3, max_length=25, description="用户账号ID")
    password: str = Field(..., min_length=6, description="用户密码")
    nickName: str = Field(..., max_length=50, description="用户昵称")
    schoolName: str = Field(..., max_length=50, description="学校名称")
    major: str = Field(..., max_length=50, description="专业")
    qualification: str = Field(..., pattern="^(高职|本科|研究生|博士)$", description="学历")
    grade: str = Field(..., max_length=15, description="年级")
    birthday: Optional[datetime] = Field(None, description="生日 (YYYY-MM-DD HH:MM:SS)")

class UserUpdateRequest(BaseModel):
    """
    用户信息更新请求模型，用于接收用户更新个人信息时提交的数据。
    继承自BaseModel，所有字段都是可选的，用户可以只更新部分信息。
    """
    nickName: Optional[str] = Field(None, max_length=50, description="用户昵称")
    password: Optional[str] = Field(None, min_length=6, description="用户密码")
    schoolName: Optional[str] = Field(None, max_length=50, description="学校名称")
    major: Optional[str] = Field(None, max_length=50, description="专业")
    qualification: Optional[str] = Field(None, pattern="^(高职|本科|研究生|博士)$", description="学历")
    grade: Optional[str] = Field(None, max_length=15, description="年级")
    birthday: Optional[datetime] = Field(None, description="生日 (YYYY-MM-DD HH:MM:SS)")


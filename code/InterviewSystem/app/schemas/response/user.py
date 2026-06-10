from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserRegistrationSuccessData(BaseModel):
    """用户注册成功返回的数据模型"""
    accountID: str
    nickName: str

class UserRegistrationResponse(BaseModel):
    """用户注册接口响应模型"""
    code: int = Field(..., description="响应状态码")
    message: str = Field(..., description="响应消息")
    data: Optional[UserRegistrationSuccessData] = Field(None, description="注册成功时返回的数据")

class UserInfoData(BaseModel):
    """用户详细信息数据模型"""
    accountID: str
    nickName: str
    schoolName: str
    major: str
    qualification: str
    grade: str
    birthday: Optional[datetime] = None
    hasAvatar: bool = Field(..., description="用户是否已上传头像")
    hasResume: bool = Field(..., description="用户是否已上传简历")
    createTime: datetime

    class Config:
        from_attributes = True

class UserInfoResponse(BaseModel):
    """获取用户信息接口响应模型"""
    code: int = Field(..., description="响应状态码")
    message: str = Field(..., description="响应消息")
    data: Optional[UserInfoData] = Field(None, description="用户信息数据")

class UserUpdateSuccessData(BaseModel):
    """用户信息更新成功返回的数据模型"""
    accountID: str
    nickName: str

class UserUpdateResponse(BaseModel):
    """用户信息更新接口响应模型"""
    code: int = Field(..., description="响应状态码")
    message: str = Field(..., description="响应消息")
    data: Optional[UserUpdateSuccessData] = Field(None, description="更新成功时返回的数据")


class ResumeCheckData(BaseModel):
    """简历检查结果数据模型"""
    accountID: str
    hasResume: bool
class ResumeCheckResponse(BaseModel):
    """简历检查接口响应模型"""
    code: int = Field(..., description="响应状态码")
    message: str = Field(..., description="响应消息")
    data: Optional[ResumeCheckData] = Field(None, description="简历检查结果")

class ResumeUploadSuccessData(BaseModel):
    """简历上传成功返回的数据模型"""
    accountID: str
    hasResume: bool

class ResumeUploadResponse(BaseModel):
    """简历上传接口响应模型"""
    code: int = Field(..., description="响应状态码")
    message: str = Field(..., description="响应消息")
    data: Optional[ResumeUploadSuccessData] = Field(None, description="简历上传成功数据")

class AvatarUploadSuccessData(BaseModel):
    """头像上传成功返回的数据模型"""
    accountID: str
    # 确认更新后的用户是否已上传头像标志
    hasAvatar: bool

class AvatarUploadResponse(BaseModel):
    """头像上传接口响应模型"""
    code: int = Field(..., description="响应状态码")
    # 描述性消息，用于提示用户操作结果
    message: str = Field(..., description="响应消息")
    data: Optional[AvatarUploadSuccessData] = Field(None, description="头像上传成功数据")


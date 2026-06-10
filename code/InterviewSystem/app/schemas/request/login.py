from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    accountID: str = Field(..., min_length=3, description="用户账号ID")
    password: str = Field(..., min_length=6, description="用户密码")


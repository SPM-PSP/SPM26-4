from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.schemas.request.login import LoginRequest
from app.schemas.request.user import UserRegisterRequest, UserUpdateRequest
from app.schemas.response.login import LoginResponse
from app.schemas.response.user import (
    UserRegistrationResponse,
    UserInfoResponse,
    UserUpdateResponse,
    ResumeCheckResponse,
    ResumeUploadResponse,
    AvatarUploadResponse
)
import json
from typing import Optional

from app.services.DataBase_connect.database import get_db

router = APIRouter()
#用于注册用户,可选择上传头像和简历
@router.post("/register", response_model=UserRegistrationResponse, summary="用户注册并可选上传头像和简历")
async def register_user(
    user_data_json: str = Form(..., description="用户注册信息的JSON字符串"),
    avatar_file: Optional[UploadFile] = File(None, description="要上传的头像文件 (JPG, PNG, GIF, WebP格式, 可选)"),
    resume_file: Optional[UploadFile] = File(None, description="要上传的简历文件 (PDF格式, 可选)"),
    db: Session = Depends(get_db)
):
    from app.services.OrdServices.user_service import register_user_service
    """
    用户通过提供账户信息注册新账号，并可选择同时上传头像和简历。
    """
    try:
        # 手动解析 JSON 字符串为 UserRegisterRequest 模型
        user_data = UserRegisterRequest.model_validate_json(user_data_json)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"user_data JSON 解析失败: {e}")

    response = await register_user_service(db, user_data, avatar_file, resume_file)
    if response.code == 201:
        return response
    elif response.code == 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response.message)
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response.message)

#用于用户登录
@router.post("/login", response_model=LoginResponse, summary="用户登录")
def login_user(login_data: LoginRequest, db: Session = Depends(get_db)):
    from app.services.OrdServices.user_service import login_service

    """用户使用账户ID和密码登录。"""
    response = login_service(db, login_data)
    if response.code == 200:
        return response
    elif response.code == 401:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=response.message)
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response.message)
#用于获得用户的信息
@router.get("/{accountID}", response_model=UserInfoResponse, summary="获取用户信息")
def get_user_info(accountID: str, db: Session = Depends(get_db)):
    from app.services.OrdServices.user_service import get_user_info_service
    """根据账户ID获取用户详细信息。"""
    response = get_user_info_service(db, accountID)
    if response.code == 200:
        return response
    elif response.code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response.message)
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response.message)

#用于更新用户信息
@router.put("/{accountID}", response_model=UserUpdateResponse, summary="更新用户信息")
def update_user_info(accountID: str, update_data: UserUpdateRequest, db: Session = Depends(get_db)):
    from app.services.OrdServices.user_service import update_user_info_service

    """更新用户个人信息。"""
    response = update_user_info_service(db, accountID, update_data)
    if response.code == 200:
        return response
    elif response.code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response.message)
    elif response.code == 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response.message)
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response.message)

#用于检查用户是否上传了简历
@router.get("/{accountID}/resume/check", response_model=ResumeCheckResponse, summary="检查用户是否已上传简历")
def check_user_resume(accountID: str, db: Session = Depends(get_db)):
    from app.services.OrdServices.user_service import check_user_resume_service
    """
    根据用户accountID检查该用户是否已上传简历。
    如果用户不存在，返回404。
    如果用户存在，返回其简历状态（是否已上传）。
    """
    response = check_user_resume_service(db, accountID)
    if response.code == 200:
        return response
    elif response.code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response.message)
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response.message)

#用于上传用户简历
@router.post("/{accountID}/resume/upload", response_model=ResumeUploadResponse, summary="上传用户简历")
async def upload_user_resume(
    accountID: str,
    resume_file: UploadFile = File(..., description="要上传的简历文件 (PDF格式)"),
    overwrite: bool = Query(False, description="如果简历已存在，是否覆盖"),
    db: Session = Depends(get_db)
):
    from app.services.OrdServices.user_service import upload_resume_service

    """
    用户上传简历文件。
    简历文件命名规则为：用户账号.pdf。
    如果简历已存在且 overwrite=False，将返回 409 Conflict 提示用户确认是否覆盖。
    """
    response = await upload_resume_service(db, accountID, resume_file, overwrite)
    if response.code == 200:
        return response
    elif response.code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response.message)
    elif response.code == 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response.message)
    elif response.code == 409:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=response.message)
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response.message)

#用于上传用户头像
@router.post("/{accountID}/avatar/upload", response_model=AvatarUploadResponse, summary="上传用户头像")
async def upload_user_avatar(
    accountID: str,
    avatar_file: UploadFile = File(..., description="要上传的头像文件 (JPG, PNG, GIF, WebP格式)"),
    db: Session = Depends(get_db)
):
    from app.services.OrdServices.user_service import upload_avatar_service

    """
    用户上传头像文件。
    头像文件命名规则为：用户账号.<ext>。
    总是覆盖现有头像。
    """
    response = await upload_avatar_service(db, accountID, avatar_file)
    if response.code == 200:
        return response
    elif response.code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response.message)
    elif response.code == 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response.message)
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response.message)

#用于获得用户头像
@router.get("/{accountID}/avatar", response_class=FileResponse, summary="获取用户头像")
def get_user_avatar(
    accountID: str,
    db: Session = Depends(get_db)
):
    from app.services.OrdServices.user_service import get_user_avatar_service

    """
    根据用户accountID获取其头像文件。
    如果用户不存在或未设置头像，返回404。
    """
    try:
        return get_user_avatar_service(db, accountID)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"获取头像时发生未知错误: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取头像失败")


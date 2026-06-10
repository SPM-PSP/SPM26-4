import os
import shutil
import anyio
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from fastapi.responses import FileResponse
from app.services.DataBase_connect import models
from app.schemas.request.login import LoginRequest
from app.schemas.request.user import UserRegisterRequest, UserUpdateRequest
from app.schemas.response.login import LoginResponse, LoginSuccessData
from app.schemas.response.user import (
    UserRegistrationResponse,
    UserRegistrationSuccessData,
    UserInfoResponse,
    UserInfoData,
    UserUpdateResponse,
    UserUpdateSuccessData,
    ResumeCheckResponse,
    ResumeCheckData,
    ResumeUploadResponse,
    ResumeUploadSuccessData,
    AvatarUploadResponse,
    AvatarUploadSuccessData
)
from app.services.OrdServices.security import verify_password, hash_password
from datetime import datetime
import mimetypes
from typing import Optional # 导入 Optional

def getDataFileRoute():
    from pathlib import Path
    current_file_path = Path(__file__).resolve()
    project_root_path = current_file_path.parent.parent.parent.parent
    FILE_STORAGE_ROOT = project_root_path / "DataFile"
    #print(f"动态计算出的文件存储根目录是: {FILE_STORAGE_ROOT}")
    return FILE_STORAGE_ROOT
if __name__ == "__main__":
    getDataFileRoute()
# 文件存储目录配置
FILE_STORAGE_ROOT = getDataFileRoute()
RESUMES_DIR = os.path.join(FILE_STORAGE_ROOT, "Resume")
AVATARS_DIR = os.path.join(FILE_STORAGE_ROOT, "Avatar")
VIDEOS_BASE_DIR = os.path.join(FILE_STORAGE_ROOT, "Video") # Base directory for videos
# 确保存储目录存在（不存在则创建）
os.makedirs(RESUMES_DIR, exist_ok=True)
os.makedirs(AVATARS_DIR, exist_ok=True)
os.makedirs(VIDEOS_BASE_DIR, exist_ok=True) # Ensure base video directory exists

async def register_user_service(db: Session, user_data: UserRegisterRequest, avatar_file: Optional[UploadFile] = None, resume_file: Optional[UploadFile] = None) -> UserRegistrationResponse:
    """
    处理用户注册业务逻辑，包括可选的头像和简历上传

    参数:
        db: 数据库会话对象
        user_data: 用户注册请求数据（Pydantic模型）
        avatar_file: 可选的头像上传文件
        resume_file: 可选的简历上传文件

    返回:
        UserRegistrationResponse: 注册结果响应对象
    """
    existing_user = db.query(models.User).filter(models.User.accountID == user_data.accountID).first()
    if existing_user:
        return UserRegistrationResponse(code=400, message="注册信息无效或账户已存在")

    hashed_password = hash_password(user_data.password)
    # 创建新用户对象
    new_user = models.User(
        accountID=user_data.accountID,
        password=hashed_password,
        nickName=user_data.nickName,
        schoolName=user_data.schoolName,
        major=user_data.major,
        qualification=user_data.qualification,
        grade=user_data.grade,
        birthday=user_data.birthday,
        avatar=False, # Initialize to False
        resume=False, # Initialize to False
        createTime=datetime.now()
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # 处理头像上传（如果提供）
        if avatar_file:
            allowed_image_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
            if avatar_file.content_type not in allowed_image_types:
                db.rollback()
                return UserRegistrationResponse(code=400, message="头像只允许上传 JPG, PNG, GIF, WebP 格式的图片")

            file_extension = mimetypes.guess_extension(avatar_file.content_type)
            if not file_extension:
                file_extension = ".png"
            target_filename = f"{user_data.accountID}{file_extension}"
            full_target_path = os.path.join(AVATARS_DIR, target_filename)

            def save_avatar_blocking():
                with open(full_target_path, "wb") as buffer:
                    shutil.copyfileobj(avatar_file.file, buffer)
            await anyio.to_thread.run_sync(save_avatar_blocking)
            new_user.avatar = True
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

        # 处理简历上传（如果提供）
        if resume_file:
            if resume_file.content_type != "application/pdf":
                db.rollback()
                return UserRegistrationResponse(code=400, message="简历只允许上传 PDF 格式的文件")

            target_filename = f"{user_data.accountID}.pdf"
            full_target_path = os.path.join(RESUMES_DIR, target_filename)

            def save_resume_blocking():
                with open(full_target_path, "wb") as buffer:
                    shutil.copyfileobj(resume_file.file, buffer)
            await anyio.to_thread.run_sync(save_resume_blocking)
            new_user.resume = True
            db.add(new_user)
            db.commit()
            db.refresh(new_user)


        return UserRegistrationResponse(
            code=201,
            message="用户注册成功",
            data=UserRegistrationSuccessData(
                accountID=new_user.accountID,
                nickName=new_user.nickName
            )
        )
    except Exception as e:
        db.rollback()
        print(f"用户注册失败: {e}")
        return UserRegistrationResponse(code=500, message="用户注册失败，请稍后再试")

def login_service(db: Session, login_data: LoginRequest) -> LoginResponse:
    """
    处理用户登录业务逻辑

    参数:
        db: 数据库会话对象
        login_data: 登录请求数据（包含账号和密码）

    返回:
        LoginResponse: 登录结果响应对象
    """
    user = db.query(models.User).filter(models.User.accountID == login_data.accountID).first()

    if not user:
        return LoginResponse(code=401, message="账户或密码不正确")

    password_valid = verify_password(login_data.password, user.password)

    if not password_valid:
        return LoginResponse(code=401, message="账户或密码不正确")

    token = f"mock_jwt_token_for_{user.accountID}"

    return LoginResponse(
        code=200,
        message="登录成功",
        data=LoginSuccessData(
            accountID=user.accountID,
            nickName=user.nickName,
            token=token
        )
    )

def get_user_info_service(db: Session, account_id: str) -> UserInfoResponse:
    """
    根据账号ID获取用户详细信息的业务逻辑

    参数:
        db: 数据库会话对象
        account_id: 用户账号ID

    返回:
        UserInfoResponse: 包含用户信息的响应对象
    """
    user = db.query(models.User).filter(models.User.accountID == account_id).first()
    if not user:
        return UserInfoResponse(code=404, message="用户不存在")

    # Populate UserInfoData with boolean fields from the User model
    user_info_data = UserInfoData(
        accountID=user.accountID,
        nickName=user.nickName,
        schoolName=user.schoolName,
        major=user.major,
        qualification=user.qualification,
        grade=user.grade,
        birthday=user.birthday,
        hasAvatar=user.avatar, # Use the new boolean field
        hasResume=user.resume, # Use the new boolean field
        createTime=user.createTime
    )
    return UserInfoResponse(
        code=200,
        message="用户信息获取成功",
        data=user_info_data
    )

def update_user_info_service(db: Session, account_id: str, update_data: UserUpdateRequest) -> UserUpdateResponse:
    """
    更新用户个人信息的业务逻辑

    参数:
        db: 数据库会话对象
        account_id: 用户账号ID
        update_data: 待更新的用户数据

    返回:
        UserUpdateResponse: 更新结果响应对象
    """
    user = db.query(models.User).filter(models.User.accountID == account_id).first()
    if not user:
        return UserUpdateResponse(code=404, message="用户不存在")

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if key == "password" and value is not None:
            setattr(user, key, hash_password(value))
        # Ensure avatar and resume are not directly updated via request data
        elif key not in ["avatar", "resume"] and value is not None:
            setattr(user, key, value)

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return UserUpdateResponse(
            code=200,
            message="用户信息更新成功",
            data=UserUpdateSuccessData(
                accountID=user.accountID,
                nickName=user.nickName
            )
        )
    except Exception as e:
        db.rollback()
        print(f"用户信息更新失败: {e}")
        return UserUpdateResponse(code=500, message="用户信息更新失败，请稍后再试")

def check_user_resume_service(db: Session, account_id: str) -> ResumeCheckResponse:
    """
    检查用户是否已上传简历的业务逻辑
    主要依赖数据库中的resume布尔字段

    参数:
        db: 数据库会话对象
        account_id: 用户账号ID

    返回:
        ResumeCheckResponse: 包含简历状态的响应对象
    """
    user = db.query(models.User).filter(models.User.accountID == account_id).first()
    if not user:
        return ResumeCheckResponse(code=404, message="用户不存在")

    # Directly use the boolean field from the database
    has_resume = user.resume

    return ResumeCheckResponse(
        code=200,
        message="简历状态获取成功",
        data=ResumeCheckData(
            accountID=account_id,
            hasResume=has_resume
        )
    )

async def upload_resume_service(db: Session, account_id: str, resume_file: UploadFile, overwrite: bool) -> ResumeUploadResponse:
    """
    处理用户简历上传业务逻辑
    更新数据库中的resume布尔字段

    参数:
        db: 数据库会话对象
        account_id: 用户账号ID
        resume_file: 简历上传文件
        overwrite: 是否覆盖已存在的简历

    返回:
        ResumeUploadResponse: 上传结果响应对象
    """
    user = db.query(models.User).filter(models.User.accountID == account_id).first()
    if not user:
        return ResumeUploadResponse(code=404, message="用户不存在")

    if resume_file.content_type != "application/pdf":
        return ResumeUploadResponse(code=400, message="只允许上传 PDF 格式的简历")

    target_filename = f"{account_id}.pdf"
    full_target_path = os.path.join(RESUMES_DIR, target_filename)

    if os.path.exists(full_target_path) and not overwrite:
        return ResumeUploadResponse(code=409, message="简历已存在，请确认是否覆盖")

    try:
        # 定义为同步函数
        def save_file_blocking():
            with open(full_target_path, "wb") as buffer:
                shutil.copyfileobj(resume_file.file, buffer)
            return True

        await anyio.to_thread.run_sync(save_file_blocking)

        # Update the database field to True
        user.resume = True
        db.add(user)
        db.commit()
        db.refresh(user)

        return ResumeUploadResponse(
            code=200,
            message="简历上传成功",
            data=ResumeUploadSuccessData(accountID=account_id, hasResume=True)
        )
    except Exception as e:
        db.rollback()
        print(f"简历上传失败: {e}")
        return ResumeUploadResponse(code=500, message=f"简历上传失败，服务器内部错误: {e}")
async def upload_avatar_service(db: Session, account_id: str, avatar_file: UploadFile) -> AvatarUploadResponse:
    """
    处理用户头像上传业务逻辑
    更新数据库中的avatar布尔字段

    参数:
        db: 数据库会话对象
        account_id: 用户账号ID
        avatar_file: 头像上传文件

    返回:
        AvatarUploadResponse: 上传结果响应对象
    """
    user = db.query(models.User).filter(models.User.accountID == account_id).first()
    if not user:
        return AvatarUploadResponse(code=404, message="用户不存在")

    allowed_image_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if avatar_file.content_type not in allowed_image_types:
        return AvatarUploadResponse(code=400, message="只允许上传 JPG, PNG, GIF, WebP 格式的图片作为头像")

    # Determine file extension based on MIME type
    file_extension = mimetypes.guess_extension(avatar_file.content_type)
    if not file_extension:
        file_extension = ".png"  # Default to .png if extension cannot be guessed

    target_filename = f"{account_id}{file_extension}"
    full_target_path = os.path.join(AVATARS_DIR, target_filename)

    try:
        # 定义为同步函数
        def save_file_blocking():
            with open(full_target_path, "wb") as buffer:
                shutil.copyfileobj(avatar_file.file, buffer)
            return True

        await anyio.to_thread.run_sync(save_file_blocking)

        # Update the database field to True
        user.avatar = True
        db.add(user)
        db.commit()
        db.refresh(user)

        return AvatarUploadResponse(
            code=200,
            message="头像上传成功",
            data=AvatarUploadSuccessData(accountID=account_id, hasAvatar=True)
        )
    except Exception as e:
        db.rollback()
        print(f"头像上传失败: {e}")
        return AvatarUploadResponse(code=500, message=f"头像上传失败，服务器内部错误: {e}")

def get_user_avatar_service(db: Session, account_id: str) -> FileResponse:
    """
    根据账号ID获取用户头像文件并返回给前端

    参数:
        db: 数据库会话对象
        account_id: 用户账号ID

    返回:
        FileResponse: 包含头像文件的响应对象
    """
    user = db.query(models.User).filter(models.User.accountID == account_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    if not user.avatar: # Check the boolean field
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="该用户没有设置头像文件")

    # Try to find all possible image extensions
    possible_extensions = [".png", ".jpg", ".jpeg", ".gif", ".webp"]
    avatar_file_path = None
    for ext in possible_extensions:
        path_to_check = os.path.join(AVATARS_DIR, f"{account_id}{ext}")
        if os.path.exists(path_to_check):
            avatar_file_path = path_to_check
            break

    if not avatar_file_path:
        # Fallback check, though avatar should ideally be in sync with file system
        print(f"Warning: DB indicates avatar uploaded for {account_id}, but file not found on disk.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="头像文件不存在")

    mime_type, _ = mimetypes.guess_type(avatar_file_path)
    if not mime_type:
        mime_type = "application/octet-stream" # Default MIME type

    return FileResponse(
        path=avatar_file_path,
        media_type=mime_type,
        filename=os.path.basename(avatar_file_path) # Return original filename
    )


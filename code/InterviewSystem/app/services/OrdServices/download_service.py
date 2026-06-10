import os
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from fastapi.responses import FileResponse, Response
from app.services.DataBase_connect import models
import mimetypes

def getDataFileRoute():
    from pathlib import Path
    current_file_path = Path(__file__).resolve()
    project_root_path = current_file_path.parent.parent.parent.parent
    FILE_STORAGE_ROOT = project_root_path / "DataFile"
    print(f"动态计算出的文件存储根目录是: {FILE_STORAGE_ROOT}")
    return FILE_STORAGE_ROOT


FILE_STORAGE_ROOT = getDataFileRoute()
REPORTS_DIR = os.path.join(FILE_STORAGE_ROOT, "Reports")  # 报告目录（占位，报告内容存储在数据库中）
VIDEOS_DIR = os.path.join(FILE_STORAGE_ROOT, "Video")  # 视频目录
RESUMES_DIR = os.path.join(FILE_STORAGE_ROOT, "Resume")  # 简历目录

os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(RESUMES_DIR, exist_ok=True)


def get_file_path_and_name(file_relative_path: str) -> tuple[str, str]:
    """
    从相对路径（如'user001/1.mp4'）构建完整的文件系统路径，并提取文件名。

    参数:
        file_relative_path: 文件的相对路径

    返回:
        元组(完整文件路径, 文件名)
    """
    full_file_path = os.path.join(FILE_STORAGE_ROOT, file_relative_path)
    file_name = os.path.basename(full_file_path)
    return full_file_path, file_name


def download_report_service(db: Session, report_id: int, preview: bool) -> Response:
    """
    通过报告ID获取报告内容，并提供下载或在线预览功能。
    现在直接从数据库的rpg字段读取JSON内容。

    参数:
        db: 数据库会话
        report_id: 报告ID
        preview: 是否预览（True表示预览，False表示下载）

    返回:
        Response对象，包含报告内容
    """
    report_entry = db.query(models.Rpg).filter(models.Rpg.ID == report_id).first()

    if not report_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到评测报告")

    # 直接使用数据库中的rpg字段作为JSON内容t
    report_content = report_entry.rpg

    mime_type = "application/json"
    suggested_filename = f"report_{report_id}.json"  # Suggested filename

    headers = {}
    if preview:
        headers["Content-Disposition"] = f"inline; filename=\"{suggested_filename}\""
    else:
        headers["Content-Disposition"] = f"attachment; filename=\"{suggested_filename}\""

    try:
        return Response(content=report_content, media_type=mime_type, headers=headers)
    except Exception as e:
        print(f"Failed to read report content for ID {report_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="无法读取报告内容")


def download_video_service(db: Session, accountID: str, videoID: str, preview: bool) -> FileResponse:
    """
    根据 accountID 和 videoID 下载或预览面试视频文件。
    """
    # 确保 videoID 不包含路径分隔符，防止路径遍历攻击
    if os.path.sep in videoID or os.path.altsep in videoID:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的 videoID 格式")

    # 构建视频文件所在的目录
    video_dir = os.path.join(FILE_STORAGE_ROOT, "Video", accountID)
    # 构建完整的视频文件路径
    file_path = os.path.join(video_dir, f"{videoID}.mp4")  # 假设视频文件以 .mp4 结尾

    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"视频文件不存在: {file_path}")  # 打印日志以便调试
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"视频文件不存在: {videoID}.mp4")

    # 根据 preview 参数设置 Content-Disposition
    if preview:
        # 预览模式：浏览器尝试直接播放
        content_disposition_type = "inline"
    else:
        # 下载模式：浏览器提示下载文件
        content_disposition_type = "attachment"

    # 获取文件名，用于 Content-Disposition
    # 这里使用 videoID.mp4 作为文件名
    file_name = f"{videoID}.mp4"

    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "video/mp4"  # 默认视频类型

    # 返回文件响应
    return FileResponse(
        path=file_path,
        media_type=mime_type,
        headers={"Content-Disposition": f'{content_disposition_type}; filename="{file_name}"'}
    )


def get_user_resume_service(db: Session, account_id: str) -> FileResponse:
    """
    通过accountID获取用户的简历文件并提供下载。
    直接从文件系统中检索，不再依赖数据库中的resume字段。

    参数:
        db: 数据库会话
        account_id: 用户账号ID

    返回:
        FileResponse对象，包含简历文件
    """
    # 检查用户是否存在（即使简历字段不在数据库中，用户存在是前提条件）
    user_exists = db.query(models.User).filter(models.User.accountID == account_id).first()
    if not user_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # 构建预期的简历文件路径（假设始终为.pdf格式）
    resume_file_path = os.path.join(RESUMES_DIR, f"{account_id}.pdf")
    suggested_filename = f"{account_id}.pdf"

    if not os.path.exists(resume_file_path):
        print(f"Resume file not found: {resume_file_path}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="该用户没有上传简历")

    mime_type, _ = mimetypes.guess_type(resume_file_path)
    if not mime_type:
        mime_type = "application/octet-stream"

    return FileResponse(
        path=resume_file_path,
        media_type=mime_type,
        filename=suggested_filename,
        headers={"Content-Disposition": f"attachment; filename=\"{suggested_filename}\""}
    )


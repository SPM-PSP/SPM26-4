import os
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from fastapi.responses import FileResponse, Response
from app.services.DataBase_connect import models
import mimetypes


# Define a constant for the file storage root directory

def getDataFileRoute():
    from pathlib import Path
    current_file_path = Path(__file__).resolve()
    project_root_path = current_file_path.parent.parent.parent.parent
    FILE_STORAGE_ROOT = project_root_path / "DataFile"
    #print(f"动态计算出的文件存储根目录是: {FILE_STORAGE_ROOT}")
    return FILE_STORAGE_ROOT

FILE_STORAGE_ROOT = getDataFileRoute() # Updated as per requirement
REPORTS_DIR = os.path.join(FILE_STORAGE_ROOT, "Reports") # Placeholder, as report content is in DB
VIDEOS_DIR = os.path.join(FILE_STORAGE_ROOT, "Video") # Updated as per requirement

# Ensure directories exist
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)


def get_full_file_path(file_relative_path: str) -> str:
    """
    Constructs the full file system path from a relative path (e.g., 'Video/user001/1.mp4').
    """
    return os.path.join(FILE_STORAGE_ROOT, file_relative_path)


def preview_report_service(db: Session, report_id: int) -> Response:
    """
    Gets report content by report ID and provides it for online preview.
    Now directly reads JSON content from the database's rpg field.
    """
    report_entry = db.query(models.Rpg).filter(models.Rpg.ID == report_id).first()

    if not report_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到评测报告")

    # Directly use rpg_entry.rpg as JSON content
    report_content = report_entry.rpg

    mime_type = "application/json"
    suggested_filename = f"report_{report_id}.json" # Suggested filename

    headers = {"Content-Disposition": f"inline; filename=\"{suggested_filename}\""}

    try:
        return Response(content=report_content, media_type=mime_type, headers=headers)
    except Exception as e:
        print(f"Failed to read report content for ID {report_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="无法读取报告内容")


def preview_video_service(db: Session, video_id: int) -> FileResponse:
    """
    Gets video file by video ID and provides it for online preview.
    """
    video_entry = db.query(models.Video).filter(models.Video.ID == video_id).first()

    if not video_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到视频")

    # video_entry.video now stores 'accountID/videoID.ext'
    video_file_path = get_full_file_path(os.path.join("Video", video_entry.video)) # Prepend "Video" directory
    suggested_filename = os.path.basename(video_file_path)

    if not os.path.exists(video_file_path):
        print(f"File not found: {video_file_path}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="视频文件不存在")

    mime_type, _ = mimetypes.guess_type(video_file_path)
    if not mime_type:
        mime_type = "application/octet-stream"

    # Set Content-Disposition to inline to force browser to try previewing
    headers = {"Content-Disposition": f"inline; filename=\"{suggested_filename}\""}

    return FileResponse(
        path=video_file_path,
        media_type=mime_type,
        filename=suggested_filename,
        headers=headers
    )



if __name__ == "__main__":
    getDataFileRoute()
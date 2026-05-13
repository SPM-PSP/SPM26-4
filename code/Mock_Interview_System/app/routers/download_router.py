from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse, Response # Import Response
from fastapi import Path
from app.services.DataBase_connect.database import get_db # Import get_db dependency
from app.services.OrdServices.download_service import download_video_service

router = APIRouter()

#用于下载面试测评报告
@router.get("/report/{reportID}/download", summary="下载面试评测报告内容")
def download_report(
    reportID: int,
    preview: bool = Query(False, description="是否在线预览，默认为下载"),
    db: Session = Depends(get_db)
) -> Response:
    try:
        from app.services.OrdServices.download_service import download_report_service

        return download_report_service(db, reportID, preview)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"An unknown error occurred while downloading report: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="下载报告失败")

#用于下载面试视频
@router.get(
    "/video/{accountID}/{videoID}/download",
    summary="Download or preview interview video by Account ID and Video ID",
    response_class=FileResponse # 明确指定响应类型
)
def download_interview_video(
    accountID: str = Path(..., description="Account ID associated with the video"),
    videoID: str = Path(..., description="Video ID of the interview video"),
    preview: bool = Query(False, description="Set to true to preview the video in the browser. If false, the video will be downloaded."), # 新增 preview 参数
    db: Session = Depends(get_db) # 保持 db 依赖，以防服务层仍需数据库操作
) -> FileResponse:
    try:
        # 传递 preview 参数给服务层
        return download_video_service(db, accountID, videoID, preview)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"下载/预览视频时发生未知错误: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="下载/预览视频失败")
#用于下载简历
@router.get("/resume/{accountID}/download", response_class=FileResponse, summary="下载用户简历文件")
def download_user_resume(
    accountID: str,
    db: Session = Depends(get_db)
):
    """
    Downloads the user's resume file by accountID.
    """
    try:
        from app.services.OrdServices.download_service import get_user_resume_service

        return get_user_resume_service(db, accountID)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"An unknown error occurred while downloading resume: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="下载简历失败")


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse, Response
from app.services.DataBase_connect.database import get_db

router = APIRouter()
#用于浏览面试评测报告文件
@router.get("/report/{reportID}", summary="预览面试评测报告文件")
def preview_report(
    reportID: int,
    db: Session = Depends(get_db)
) -> Response:
    try:

        from app.services.OrdServices.preview_service import preview_report_service

        return preview_report_service(db, reportID)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"An unknown error occurred while previewing report: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="预览报告失败")

#用于浏览面试视频文件(现在使用的是下载视频的接口,将preview参数设为True)
@router.get("/video/{videoID}", response_class=FileResponse, summary="预览面试视频文件")
def preview_video(
    videoID: int,
    db: Session = Depends(get_db)
):
    try:

        from app.services.OrdServices.preview_service import preview_video_service

        return preview_video_service(db, videoID)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"An unknown error occurred while previewing video: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="预览视频失败")


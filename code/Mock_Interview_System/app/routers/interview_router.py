from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.response.interview import InterviewReportResponse, HistoryReportListResponse
from app.services.DataBase_connect.database import get_db

router = APIRouter()


# 用于获得面试报告的详情
@router.get("/report/{reportID}", response_model=InterviewReportResponse, summary="获取面试评测报告详情")
def get_interview_report(reportID: int, db: Session = Depends(get_db)):
    from app.services.OrdServices.interview_service import get_interview_report_service
    response = get_interview_report_service(db, reportID)
    if response.code == 200:
        return response
    elif response.code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response.message)
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response.message)


# 用于获得用户所有面试报告的列表
@router.get("/reports/history/{accountID}", response_model=HistoryReportListResponse,
            summary="获取用户所有面试历史报告列表")
def get_history_reports(accountID: str, db: Session = Depends(get_db)):
    from app.services.OrdServices.interview_service import get_history_reports_service
    response = get_history_reports_service(db, accountID)
    if response.code == 200:
        return response
    elif response.code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response.message)
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response.message)


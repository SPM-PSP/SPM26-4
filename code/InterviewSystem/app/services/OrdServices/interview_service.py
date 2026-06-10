import json
from typing import List
from sqlalchemy.orm import Session
from app.services.DataBase_connect import models
from app.schemas.response.interview import (
    InterviewReportResponse,
    ReportData,
    HistoryReportListResponse,
)
from pydantic import ValidationError
import os

def getDataFileRoute():
    from pathlib import Path
    current_file_path = Path(__file__).resolve()
    project_root_path = (current_file_path.parent.parent.parent)
    FILE_STORAGE_ROOT = project_root_path / "DataFile"
    print(f"动态计算出的文件存储根目录是: {FILE_STORAGE_ROOT}")
    return FILE_STORAGE_ROOT
if __name__ == "__main__":
    getDataFileRoute()

FILE_STORAGE_ROOT =getDataFileRoute()
REPORTS_DIR = os.path.join(FILE_STORAGE_ROOT, "Reports")
os.makedirs(REPORTS_DIR, exist_ok=True)
def get_interview_report_service(db: Session, report_id: int) -> InterviewReportResponse:
    rpg_entry = db.query(models.Rpg).filter(models.Rpg.ID == report_id).first()

    if not rpg_entry:
        return InterviewReportResponse(code=404, message="未找到评测报告")

    try:
        report_content_json = rpg_entry.rpg
        report_data_dict = json.loads(report_content_json)

        report_data_dict['reportID'] = rpg_entry.ID
        report_data_dict['accountID'] = rpg_entry.accountID
        report_data_dict['datetime'] = rpg_entry.datetime
        report_data_dict['reportURL'] = f"/api/download/report/{rpg_entry.ID}/download"
        report_data_dict['videoID'] = rpg_entry.videoID
        report_data_dict['job'] = rpg_entry.job
        report_data = ReportData(**report_data_dict)

        return InterviewReportResponse(
            code=200,
            message="评测报告获取成功",
            data=report_data
        )
    except json.JSONDecodeError:
        print(f"Report ID {rpg_entry.ID} content is not valid JSON.")
        return InterviewReportResponse(code=500, message="评测报告数据格式错误")
    except ValidationError as e:
        print(f"Report ID {rpg_entry.ID} data does not conform to Pydantic model: {e.errors()}")
        return InterviewReportResponse(code=500, message="评测报告数据结构不匹配")
    except Exception as e:
        print(f"An unknown error occurred while getting assessment report: {e}")
        return InterviewReportResponse(code=500, message="获取评测报告失败，请稍后再试")


def get_history_reports_service(db: Session, account_id: str) -> HistoryReportListResponse:
    print(f"[DEBUG] 查询历史报告 - account_id: '{account_id}'")
    
    # 检查用户是否存在
    user_exists = db.query(models.User).filter(models.User.accountID == account_id).first()
    print(f"[DEBUG] 用户是否存在: {user_exists is not None}")
    
    # 使用大小写不敏感查询
    reports = db.query(models.Rpg).filter(
        models.Rpg.accountID.ilike(account_id)
    ).all()
    
    print(f"[DEBUG] 查询到的报告数量: {len(reports)}")

    if not reports:
        return HistoryReportListResponse(code=404, message="用户不存在或无历史报告")

    full_history_items: List[ReportData] = []
    for report_entry in reports:
        try:
            report_content_json = report_entry.rpg
            report_content = json.loads(report_content_json)

            report_content['reportID'] = report_entry.ID
            report_content['accountID'] = report_entry.accountID
            report_content['datetime'] = report_entry.datetime
            report_content['reportURL'] = f"/api/download/report/{report_entry.ID}/download"
            report_content['videoID'] = report_entry.videoID
            report_content['job'] = report_entry.job
            full_report_data = ReportData.model_validate(report_content)
            full_history_items.append(full_report_data)
        except json.JSONDecodeError:
            print(f"History data for Report ID {report_entry.ID} is not valid JSON, skipping.")
            continue
        except ValidationError as e:
            print(f"Data for Report ID {report_entry.ID} does not conform to ReportData model, skipping: {e.errors()}")
            continue
        except Exception as e:
            print(f"An error occurred while processing Report ID {report_entry.ID}, skipping: {e}")
            continue

    if not full_history_items:
        return HistoryReportListResponse(code=404, message="用户不存在或无历史报告")

    return HistoryReportListResponse(
        code=200,
        message="历史报告获取成功",
        data=full_history_items
    )


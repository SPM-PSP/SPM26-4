from fastapi import APIRouter, Query, HTTPException, Depends
from app.schemas.request.checkResumereq import ResumeCheckRequest
from app.schemas.response.checkResumeres import ResumeCheckResponse
from pathlib import Path

router = APIRouter()

def getResumeCheckReq(
    user_id: str = Query(..., description="要检查用户的账号ID")
) -> ResumeCheckRequest:
    return ResumeCheckRequest(user_id=user_id)


@router.get("/check_resume", response_model=ResumeCheckResponse)
async def check_resume(
        request_params: ResumeCheckRequest = Depends(getResumeCheckReq),
):
    """
    检查指定用户的简历是否存在
    """
    try:
        #构件resume文件的目录路径
        current_file=Path(__file__).resolve()
        app_dir=current_file.parent.parent.parent
        resume_dir=app_dir/"DataFile"/"Resume"

        filename=f"{request_params.user_id}.pdf"
        pdffile=resume_dir/filename
        path_str=str(pdffile)

        #检查文件是否存在
        if pdffile.is_file():
            return ResumeCheckResponse(
                user_id=request_params.user_id,
                resume_path=path_str,
                message="简历存在"
            )
        else:
            return ResumeCheckResponse(
                user_id=request_params.user_id,
                resume_path=None,
                message="简历不存在"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查简历时出错：{str(e)}")




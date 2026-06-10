from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional # 导入 Optional
from app.schemas.request.question import QuestionQueryParams
from app.schemas.response.question import QuestionListResponse
from app.services.DataBase_connect.database import get_db # 导入 get_db 依赖

router = APIRouter()
# 用于获取面试题目
@router.get("/{jobRole}", response_model=QuestionListResponse, summary="根据岗位和难度获取面试题目")
def get_questions(
    jobRole: str,
    degree: Optional[str] = Query(
        None,
        description="题目难度：简单, 中等, 困难",
        pattern="^(简单|中等|困难)$"
    ),
    limit: int = Query(
        10,
        ge=1,
        description="返回题目数量，默认为10"
    ),
    db: Session = Depends(get_db)
):
    """
    获取特定岗位下的面试题目，可根据难度筛选。

    - **jobRole**: 岗位名称。预期值：`bigdata` (大数据开发工程师), `internetofthings` (物联网解决方案架构师), `ai` (机器学习工程师)。
    - **degree** (可选): 题目难度。预期值：`简单`, `中等`, `困难`。
    - **limit** (可选): 返回题目数量。默认值可设置为10。
    """
    # 将查询参数打包成 QuestionQueryParams 对象
    from app.services.OrdServices.question_service import get_questions_service

    params = QuestionQueryParams(degree=degree, limit=limit)
    if jobRole == "大数据开发工程师":
        jobRole = "bigdata"
    elif jobRole == "物联网产品经理":
        jobRole = "internetofthings"
    elif jobRole == "机器学习测试工程师":
        jobRole = "ai"

    response = get_questions_service(db, jobRole, params)

    if response.code == 200:
        return response
    elif response.code == 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response.message)
    elif response.code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response.message)
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response.message)


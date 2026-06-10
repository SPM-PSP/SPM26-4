from sqlalchemy.orm import Session
from app.services.DataBase_connect import models # Ensure models are imported
from app.schemas.response.question import QuestionListResponse, QuestionData
from app.schemas.request.question import QuestionQueryParams
from typing import Type, Optional

# 定义岗位角色到对应SQLAlchemy模型的映射关系
# 不同岗位的面试题存储在不同的数据表中
JOB_ROLE_MODEL_MAP = {
    "bigdata": models.BigDataDEQuestion, # Table name changed
    "internetofthings": models.IoTSAAQuestion, # Table name changed
    "ai": models.AIMSEQuestion, # Table name changed
}

def get_questions_service(
    db: Session,
    job_role: str,
    params: QuestionQueryParams
) -> QuestionListResponse:
    """
    根据岗位角色和难度获取面试题列表的业务逻辑

    参数:
        db: 数据库会话
        job_role: 岗位角色（如"bigdata", "internetofthings", "ai"）
        params: 问题查询参数（包含难度和数量限制）

    返回:
        QuestionListResponse: 包含问题列表的响应对象
    """
    question_model: Optional[Type[models.BigDataDEQuestion]] = JOB_ROLE_MODEL_MAP.get(job_role)
    if not question_model:
        return QuestionListResponse(code=400, message="岗位参数无效")

    query = db.query(question_model)

    # 根据难度进行筛选（如果提供了难度参数）
    if params.degree:
        query = query.filter(question_model.degree == params.degree)

    #  限制结果数量
    questions = query.limit(params.limit).all()

    if not questions:
        return QuestionListResponse(code=404, message="未找到符合条件的题目")

    question_data_list = [QuestionData.model_validate(q) for q in questions]

    return QuestionListResponse(
        code=200,
        message="题目获取成功",
        data=question_data_list
    )


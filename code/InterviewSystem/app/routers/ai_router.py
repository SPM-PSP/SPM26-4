from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


# 定义对话消息模型
class Message(BaseModel):
    role: str = Field(..., description="角色 (user 或 assistant)")
    content: str = Field(..., description="消息内容")

class AIAssistantRequest(BaseModel):
    """
    AI 助手提问请求模型，支持多轮对话。
    """
    question: str = Field(..., min_length=1, description="用户提问内容")
    history: Optional[List[Message]] = Field(None, description="之前的对话历史")

class AIAssistantResponseData(BaseModel):
    """
    AI 助手回答数据模型。
    """
    answer: str = Field(..., description="回答内容")
    datetime: str = Field(..., description="回答时间 (YYYY-MM-DD HH:MM:SS)")

class AIAssistantResponse(BaseModel):
    """
    AI 助手接口的最终响应模型。
    """
    code: int = Field(..., description="响应状态码")
    message: str = Field(..., description="响应消息")
    data: Optional[AIAssistantResponseData] = Field(None, description="AI 助手回答数据")

router = APIRouter()

@router.post("/ask", response_model=AIAssistantResponse, summary="用户提交问题，获取AI助手的回答，支持多轮对话")
def ask_ai_assistant(request: AIAssistantRequest):
    """
    用户提交问题，获取AI助手的回答。
    """
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": 400, "message": "问题内容不能为空"}
        )

    try:
        from app.services.OrdServices.ai_service import get_ai_answer_from_spark
        ai_answer = get_ai_answer_from_spark(request.question, request.history)
        if not ai_answer:
            # 如果 AI 没有返回内容，可能是服务问题或空回答
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": 500, "message": "AI 助手未能生成回答，请稍后再试或检查凭据"}
            )

        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return AIAssistantResponse(
            code=200,
            message="请求成功",
            data=AIAssistantResponseData(
                answer=ai_answer,
                datetime=current_datetime
            )
        )
    except Exception as e:
        print(f"调用AI助手时发生错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": 500, "message": f"AI 助手服务内部错误: {e}"}
        )


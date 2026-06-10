from pydantic import BaseModel, Field
from typing import Optional

class QuestionQueryParams(BaseModel):
    """
    面试题目获取的查询参数模型。
    """
    degree: Optional[str] = Field(
        None,
        pattern="^(简单|中等|困难)$",
        description="题目难度：简单, 中等, 困难"
    )
    limit: int = Field(
        10,
        ge=1,
        description="返回题目数量，默认为10"
    )


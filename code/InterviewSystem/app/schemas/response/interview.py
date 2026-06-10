# interview.py
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Dict, Any
from datetime import datetime


# --- 1. 定义 RPG JSON 内部各个部分的子模型 ---
# 这些模型精确地描述了你数据库 `rpg` 列中存储的 JSON 对象的内部结构。
# 我们保留了您原始文件中的部分类名，并为缺失的部分创建了新的类。

class PoseData(BaseModel):
    comment: str
    Normal: float
    Hand_on_waist: float = Field(..., alias='Hand on waist')
    Hands_clasped: float = Field(..., alias='Hands clasped')
    Head_looks_down: float = Field(..., alias='Head looks down')


class EmotionData(BaseModel):
    comment: str
    fear: float
    angry: float
    neutral: float
    happy: float
    sad: float
    disgust: float
    surprise: float


class EyeContactData(BaseModel):
    comment: str
    Contact: float
    Not_Contact: float = Field(..., alias='Not Contact')


class HandMovementData(BaseModel):
    comment: str
    total_movement: float
    average_movement_per_frame: float


class ObjectTrackerData(BaseModel):
    comment: str
    total_distance: float
    average_distance_per_frame: float
    assessment: str


class StutterAnalysisData(BaseModel):
    comment: str
    nonstutter: float
    repetition: float
    prolongation: float
    blocks: float


class RhythmAnalysisData(BaseModel):
    comment: str
    score: int
    description: str


class SpeedAnalysisData(BaseModel):
    comment: str
    score: float
    words_per_minute: int
    description: str


class StutterSpeedRhythmData(BaseModel):
    comment: str
    stutter_analysis: StutterAnalysisData
    rhythm_analysis: RhythmAnalysisData
    speed_analysis: SpeedAnalysisData


class LearningRecommendationItem(BaseModel):  # <-- 保留您定义的类名，并根据JSON补充字段
    type: str
    title: str
    url: str
    reason: str


class StudyRouteData(BaseModel):
    comment: str
    recommendations: List[LearningRecommendationItem]


class RadarChartData(BaseModel):  # <-- 根据数据库实际数据调整雷达图数据字段
    comment: str
    伦理安全: int
    应急响应能力: int
    数据质量分析: int
    模型测试能力: int
    自动化测试开发: int
    跨领域知识储备: int


# --- 2. 核心：定义最终返回给前端的 ReportData 模型 ---
# 这个模型是“扁平化”的，它将数据库顶级字段和rpg内的字段合并在了一起。

class ReportData(BaseModel):
    # 使用别名(alias)来匹配 'input' 字典中的键名
    ID: int = Field(..., alias='reportID')
    accountID: str
    videoID: str
    datetime: datetime
    job: str

    # rpg JSON 字段中的内容，现在作为顶级字段处理
    comment: str
    summary: str
    # 同时处理 'radarChartData' 和 'radarCharData' 的大小写问题
    radarChartData: RadarChartData = Field(..., alias='radarCharData')
    pose: PoseData
    emotion: EmotionData
    eye_contact: EyeContactData
    hand_movement: HandMovementData
    object_tracker: ObjectTrackerData
    stutter_speed_rhythm: StutterSpeedRhythmData
    study_route: StudyRouteData
    overall_score: float

    # 我们不再需要 @model_validator，因为 service 层已经做了扁平化
    # 但我们仍然需要 from_attributes=True，因为你的 service 层可能在某些情况下还是会传 ORM 对象
    class Config:
        from_attributes = True
        # 这个配置允许 Pydantic 在填充模型时使用我们定义的别名
        populate_by_name = True
# --- 3. 最终的API响应模型 (保留您原有的定义) ---

class InterviewReportResponse(BaseModel):
    code: int = Field(..., description="Response status code")
    message: str = Field(..., description="Response message")
    data: Optional[ReportData] = Field(None, description="Interview assessment report data")


class HistoryReportListResponse(BaseModel):
    """
    Response model for getting a list of all user's historical interview reports.
    Now returns a list of complete assessment report data.
    """
    code: int = Field(200, description="Response status code")
    message: str = Field("success", description="Response message")
    data: Optional[List[ReportData]] = Field(None, description="History report list (complete data)")

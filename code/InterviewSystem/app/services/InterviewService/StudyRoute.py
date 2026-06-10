# -*- coding: utf-8 -*-

"""
根据面试岗位以及核心指标的评分，使用推荐算法得到推荐学习路线
"""

import json
from typing import List, Optional
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import create_engine, Column, Integer, String, JSON, Double
from sqlalchemy.orm import sessionmaker, declarative_base

# --- Database Configuration (matches embedding_zhibiao_ios.py) ---
MYSQL_USERNAME = "root"
MYSQL_PASSWORD = "157613"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DATABASE = "interviewdata"

DATABASE_URL = f"mysql+mysqlconnector://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

Base = declarative_base()
Engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)


# resource表的ORM模型
class ResourceTable(Base):
    __tablename__ = "resource"

    resourceID = Column(Integer, primary_key=True, nullable=False)
    type = Column(String(25), nullable=False)
    url = Column(String(255), nullable=False)
    embedding = Column(JSON)  # SQLAlchemy will handle JSON deserialization
    description = Column(String(255))
    bigdata_match_score = Column(Double)
    iot_match_score = Column(Double)  # Note: 'iot' is represented by 'ios'
    ai_match_score = Column(Double)
    benefit = Column(String(255))


# 接收分析结果rpg和domain、vocation，返回带有推荐资源的 rpg。
def recommend_study_route(rpg: dict, domain: str, vocation: str) -> dict:
    from app.services.InterviewService.LLM_caulate_Embedding import get_embedding

    """
    Main function to generate study recommendations.
    """
    # 提取用户弱点文本
    user_weakness_text = extract_weakness_profile(rpg)

    # 获取用户弱点向量
    user_weakness_embedding = get_embedding(user_weakness_text)

    if not user_weakness_embedding:
        print("[ERROR] Could not generate embedding for user weakness profile. Cannot recommend resources.")
        rpg["study_route"] = {"comment": "无法生成用户报告嵌入向量，推荐失败。", "recommendations": []}
        return rpg

    # 创建数据库会话
    db = SessionLocal()
    try:
        # 计算并获取推荐资源
        recommendations = compute_top_study_recommendations(user_weakness_embedding, domain, db)
        rpg["study_route"] = recommendations
    except Exception as e:
        print(f"[ERROR] An error occurred during recommendation computation: {e}")
        rpg["study_route"] = {"comment": "计算推荐资源时发生错误。", "recommendations": []}
    finally:
        # 确保数据库会话被关闭
        db.close()

    return rpg


def extract_weakness_profile(rpg: dict) -> str:
    # This function remains unchanged.
    weaknesses = []
    radar = rpg.get("radarCharData", {})
    for key, score in radar.items():
        if key == "comment": continue
        if isinstance(score, (int, float)) and score < 80:
            weaknesses.append(f"{key}偏弱（得分{score}）")
    if rpg.get("eye_contact", {}).get("Not Contact", 0) > 50:
        weaknesses.append("缺乏有效的眼神交流,与面试官沟通缺乏")
    emotion = rpg.get("emotion", {})
    for emo in ["fear", "angry", "disgust"]:
        if emotion.get(emo, 0) > 10:
            weaknesses.append(f"存在一定的{emo}情绪")
    if rpg.get("pose", {}).get("Head looks down", 0) > 50:
        weaknesses.append("存在较多低头行为,传达了不够自信的信号")
    stutter = rpg.get("stutter_speed_rhythm", {}).get("stutter_analysis", {})
    if any(stutter.get(k, 0) > 0.01 for k in ["repetition", "prolongation", "blocks"]):
        weaknesses.append("流畅度问题：存在轻微口吃或语音阻塞现象")
    rhythm = rpg.get("stutter_speed_rhythm", {}).get("rhythm_analysis", {})
    if rhythm.get("score", 100) < 85:
        weaknesses.append(f"语调存在问题：{rhythm.get('description', '语调表现需改进')}")
    speed = rpg.get("stutter_speed_rhythm", {}).get("speed_analysis", {})
    wpm = speed.get("words_per_minute", 0)
    if wpm > 300:
        weaknesses.append(f"语速偏快（{wpm} 字/分钟）")
    elif wpm < 180:
        weaknesses.append(f"语速偏慢（{wpm} 字/分钟）")
    summary = rpg.get("summary", "").strip()
    if not weaknesses:
        return summary or "暂无明显弱点，整体表现良好"
    return "；".join(weaknesses) + "综合评语：" + summary


def compute_top_study_recommendations(user_weakness_embedding: List[float], domain: str, db):
    """
    Queries resources from DB using SQLAlchemy and computes recommendation scores.
    """
    # --- CORE REFACTOR ---
    # Query all resources using the SQLAlchemy ORM session.
    # This returns a list of ResourceTable objects.
    resources_from_db = db.query(ResourceTable).all()

    scored_resources = []
    for resource in resources_from_db:
        # --- THE CORRECT WAY (as per your example) ---
        # Directly access the 'embedding' attribute. SQLAlchemy handles the
        # JSON string -> Python list conversion automatically.
        resource_embedding = resource.embedding

        # Validate that the embedding is a valid list
        if not resource_embedding or not isinstance(resource_embedding, list):
            print(f"[WARNING] Skipping resourceID={resource.resourceID}: embedding is missing or invalid.")
            continue

        # Calculate weakness similarity
        weakness_similarity = cosine_similarity([user_weakness_embedding], [resource_embedding])[0][0]

        # Get job domain match score from the corresponding column
        if domain == "大数据":
            job_match_score = resource.bigdata_match_score or 0.0
        elif domain == "物联网":
            # The ORM model uses 'iot_match_score' for this domain
            job_match_score = resource.iot_match_score or 0.0
        elif domain == "人工智能":
            job_match_score = resource.ai_match_score or 0.0
        else:
            job_match_score = 0.0

        # Calculate final combined score
        final_score = round(weakness_similarity * 0.6 + job_match_score * 0.4, 4)

        scored_resources.append({
            "type": resource.type,
            "title": resource.description,
            "url": resource.url,
            "reason": resource.benefit,
            "match_score": final_score
        })

    # Sort by score and get the top 10
    top_resources = sorted(scored_resources, key=lambda r: r["match_score"], reverse=True)[:10]

    # Format for final output
    recommendations = [{
        "type": res["type"],
        "title": res["title"],
        "url": res["url"],
        "reason": res["reason"]
    } for res in top_resources]

    return {
        "comment": "个性化学习资源推荐",
        "recommendations": recommendations
    }


if __name__ == "__main__":
    # The RPG data remains the same for testing
    rpg = {
        "comment": "面试分析综合报告",
        "summary": "基于对您在本次面试视频中的全面分析，我们得出以下结论...",
        "radarCharData": {"专业知识水平": 80, "逻辑思维能力": 85, "沟通表达能力": 75, "项目经验匹配度": 90,
                          "技能匹配度": 78},
        "pose": {"Head looks down": 87.01, "Hand on waist": 11.90},
        "emotion": {"fear": 14.15, "angry": 13.91, "neutral": 20.86, "disgust": 14.63},
        "eye_contact": {"Contact": 0.00, "Not Contact": 100.00},
        "stutter_speed_rhythm": {
            "stutter_analysis": {"repetition": 0.0101},
            "rhythm_analysis": {"score": 95, "description": "语调自然流畅"},
            "speed_analysis": {"score": 78.5, "words_per_minute": 343}
        },
        "study_route": {"recommendations": []},
    }
    domain = "物联网"
    vocation = "物联网开发工程师"

    # You will need to mock the `get_embedding` function for this to run standalone
    # For example:
    # def get_embedding(text: str) -> List[float]:
    #     print(f"Generating mock embedding for: '{text[:50]}...'")
    #     return np.random.rand(1024).tolist() # Assuming embedding dimension is 1024

    try:
        # The main function now handles its own DB connection
        result_rpg = recommend_study_route(rpg, domain, vocation)
        print("\n--- Recommended Study Route ---")
        print(json.dumps(result_rpg, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"\nAn error occurred during execution: {e}")
        print("Please ensure the 'llm.py' module and its 'get_embedding' function are available.")
        print("Also, confirm the database is running and accessible with the provided credentials.")
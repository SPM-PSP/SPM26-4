from typing import Dict, Any
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import json

def InsertVideo(accountID: str, video_path: str, date: str) -> int:
    """
    将视频信息插入到数据库的video表中
    :param accountID: 用户账号ID
    :param video_path: 视频存储路径（相对路径，如 accountID/videoID.ext）
    :param date: 面试时间
    :return: 新插入视频的ID（主键），失败返回-1
    """
    connection = None
    cursor = None
    
    try:
        # 将date字符串转换为标准的datetime格式
        date_time = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="157613",
            database="interviewdata",
            port="3306"
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            query = """INSERT INTO video (accountID, video, datetime) VALUES (%s, %s, %s)"""
            record = (accountID, video_path, date_time)
            cursor.execute(query, record)
            connection.commit()
            
            # 获取刚插入记录的自增ID
            video_id = cursor.lastrowid
            print(f"视频信息插入成功，ID: {video_id}")
            return video_id
            
    except ValueError:
        print("日期格式错误")
        return -1
    except Error as e:
        print(f"数据库操作失败: {e}")
        if connection:
            connection.rollback()
        return -1
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("数据库连接已关闭。")

def InsertReport(job:str,accountID:str,videoID:str,date:str,report: Dict[str, Any]) -> bool:
    """
    将面试报告项插入到数据库中
    :param job: 面试者面试岗位信息
    :param accountID: 面试者用户账号ID
    :param videoID: 此次面试对应的videoID
    :param date: 面试的时间，数据库中是Datetime格式
    :param report: json格式报告
    :return: success（bool）
    """

    parts = job.split(':', 1)
    if len(parts) != 2:
        print(f"错误: 不合法的Job格式 '{job}'。应为 '领域:职业'。")
        return None

    adomain, avocation = parts[0].strip(), parts[1].strip()  # 使用strip()移除可能的前后空格
    if (adomain == "ai"):
        adomain = "人工智能"
        avocation = "机器学习测试工程师"
    elif (adomain == "bigdata"):
        adomain = "大数据"
        avocation = "大数据开发工程师"
    elif (adomain == "internetofthings"):
        adomain = "物联网"
        avocation = "物联网产品经理"

    connection=None
    cursor=None

    try:
        #先进行数据格式的转换
        report_json=json.dumps(report,ensure_ascii=False)    #中文字符直接存储，不转义

        try:
            #再将date字符串转换为标准的datetime格式YYYY-MM-DD HH:MM:SS
            date_time=datetime.strptime(date,"%Y-%m-%d %H:%M:%S")
        except ValueError:
            print("日期Date格式错误")
            return False

        #连接并操作数据库
        connection=mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="157613",
            database="interviewdata",
            port = "3306"
        )

        if connection.is_connected():
            cursor=connection.cursor()
            query="""insert into rpg (accountID,videoID,datetime,job,rpg) values (%s,%s,%s,%s,%s)"""

            # 确保 videoID 是整数类型
            try:
                videoID_int = int(videoID)
            except ValueError:
                print(f"错误: videoID '{videoID}' 无法转换为整数")
                return False
            
            record=(accountID, videoID_int, date_time, job, report_json)
            cursor.execute(query,record)
            connection.commit()
            print("报告项插入成功")
            return True

    except Error as e:
        print(f"数据库操作失败: {e}")
            # 如果发生错误，可以选择性地回滚事务
        if connection:
            connection.rollback()
        return False

    finally:
        # 清理资源
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("数据库连接已关闭。")




if __name__ == "__main__":
    #模拟的报告字典
    mock_report = {
        "comment": "面试分析综合报告",
        "summary": "",  # 初始为空，等待LLM填充
        "radarCharData": {
            "comment": "雷达图数据，包含针对岗位的五个核心指标及其得分"
            # 初始为空，等待LLM填充
        },
        "pose": {
            "comment": "身体姿态分析结果，单位为百分比",
            "Head looks down": 87.01,
            "Hand on waist": 11.90,
            "Normal": 0.15,
            "Hands clasped": 0.91
        },
        "emotion": {
            "comment": "面部情绪分析结果，单位为百分比",
            "fear": 14.15,
            "angry": 13.91,
            "neutral": 20.86,
            "happy": 27.94,
            "sad": 7.67,
            "disgust": 14.63,
            "surprise": 0.84
        },
        "eye_contact": {
            "comment": "眼神接触分析结果，单位为百分比",
            "Contact": 0.00,
            "Not Contact": 100.00
        },
        "hand_movement": {
            "comment": "手部移动量化分析",
            "total_movement": 70.68,
            "average_movement_per_frame": 0.11
        },
        "object_tracker": {
            "comment": "身体整体移动评估",
            "total_distance": 72.91,
            "average_distance_per_frame": 0.11,
            "assessment": "演讲者相对静止。考虑使用更多的手势和身体移动来吸引观众。"
        },
        "stutter_speed_rhythm": {
            "comment": "言语分析：包含流畅度、语速和语调",
            "stutter_analysis": {
                "comment": "言语流畅度分析，值为置信度",
                "nonstutter": 0.9878,
                "repetition": 0.0101,
                "prolongation": 0.0011,
                "blocks": 0.0010
            },
            "rhythm_analysis": {
                "comment": "语调分析",
                "score": 95,
                "description": "语调自然流畅"
            },
            "speed_analysis": {
                "comment": "语速分析",
                "score": 78.5,
                "words_per_minute": 343,
                "description": "语速偏快 343字/分钟"
            }
        },
        "study_route": {
            "comment": "个性化学习资源推荐",
            "recommendations": []  # 初始为空
        },
        "overall_score": 0  # 初始为0，等待LLM填充
    }

    #其他信息
    mock_job = "互联网:大数据开发工程师"
    mock_account_id = "user12345"
    mock_video_id = "vid_abcde67890"
    # 获取当前时间并格式化为MySQL接受的字符串
    mock_date_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    #调用插入函数
    success = InsertReport(
        job=mock_job,
        accountID=mock_account_id,
        videoID=mock_video_id,
        date=mock_date_string,
        report=mock_report
    )

    if success:
        print("\n函数调用成功，数据已插入。")
    else:
        print("\n函数调用失败，数据未插入。")
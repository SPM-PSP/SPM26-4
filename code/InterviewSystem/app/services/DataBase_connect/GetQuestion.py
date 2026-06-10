import random
import mysql.connector
from mysql.connector import Error


def getQuestion(profession, degree: str = "简单") -> str:
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="157613",
            database="interviewdata",
            port=3306
        )
        # 数据库连接失败返回空字符串
        if not connection.is_connected():
            print("连接失败")
            return ""

        print("数据库连接成功，开始选择问题")
        cursor = connection.cursor()
        # 执行 SQL 查询获取数据
        if profession == "大数据:大数据开发工程师":  # 大数据领域的面试岗位
            if degree == "简单":
                cursor.execute("SELECT question FROM bigdata WHERE degree='简单' ORDER BY RAND() LIMIT 1;")
            elif degree == "中等":
                cursor.execute("SELECT question FROM bigdata WHERE degree='中等' ORDER BY RAND() LIMIT 1;")
            elif degree == "困难":
                cursor.execute("SELECT question FROM bigdata WHERE degree='困难' ORDER BY RAND() LIMIT 1;")
        elif profession == "人工智能:机器学习测试工程师":  # 人工智能领域的面试岗位
            if degree == "简单":
                cursor.execute("SELECT question FROM ai WHERE degree='简单' ORDER BY RAND() LIMIT 1;")
            elif degree == "中等":
                cursor.execute("SELECT question FROM ai WHERE degree='中等' ORDER BY RAND() LIMIT 1;")
            elif degree == "困难":
                cursor.execute("SELECT question FROM ai WHERE degree='困难' ORDER BY RAND() LIMIT 1;")
        elif profession == "物联网:物联网产品经理":  # 物联网领域的面试岗位
            if degree == "简单":
                cursor.execute("SELECT question FROM internetofthings WHERE degree='简单' ORDER BY RAND() LIMIT 1;")
            elif degree == "中等":
                cursor.execute("SELECT question FROM internetofthings WHERE degree='中等' ORDER BY RAND() LIMIT 1;")
            elif degree == "困难":
                cursor.execute("SELECT question FROM internetofthings WHERE degree='困难' ORDER BY RAND() LIMIT 1;")

        # 这里可以根据需求自行添加不同的查询

        # 获取查询结果
        result = cursor.fetchone()
        if result is not None:
            return result[0]

    except Error as e:
        print(f"连接错误: {e}")

    finally:
        # 关闭数据库连接
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("数据库连接已关闭")


if __name__ == "__main__":
    degree = ""
    random_int = random.randint(1, 3)
    if random_int == 1:
        degree = "简单"
    elif random_int == 2:
        degree = "中等"
    elif random_int == 3:
        degree = "困难"
    question = getQuestion("物联网:物联网产品经理", degree)
    print(question)
    question = getQuestion("大数据:大数据开发工程师", degree)
    print(question)
    question = getQuestion("人工智能:机器学习测试工程师", degree)
    print(question)
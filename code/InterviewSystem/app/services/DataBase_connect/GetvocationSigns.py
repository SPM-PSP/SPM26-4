import mysql.connector
from mysql.connector import Error
from typing import Tuple, Optional


def getVocationSigns(job: str) -> Optional[Tuple[str, str, str, str, str, str]]:
    """
    根据 "领域:职业" 格式的字符串，从数据库查询并返回6个职业指标。

    :param job: 格式为 "领域:职业" 的字符串，例如 "互联网:后端开发"。
    :return: 一个包含6个指标字符串的元组。如果找不到或发生错误，则返回 None。
    """
    # 解析输入Job的格式，如果格式不正确，则提前返回
    parts = job.split(':', 1)
    if len(parts) != 2:
        print(f"错误: 不合法的Job格式 '{job}'。应为 '领域:职业'。")
        return None

    adomain, avocation = parts[0].strip(), parts[1].strip()  # 使用strip()移除可能的前后空格
    if(adomain == "ai"):
        adomain = "人工智能"
        avocation = "机器学习测试工程师"
    elif(adomain == "bigdata"):
        adomain = "大数据"
        avocation = "大数据开发工程师"
    elif(adomain == "internetofthings"):
        adomain = "物联网"
        avocation = "物联网产品经理"

    # 初始化数据库连接和游标变量，以便在finally块中安全地检查
    connection = None
    cursor = None

    try:
        # 连接数据库
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="157613",
            database="interviewdata",
            port="3306"
        )

        if connection.is_connected():
            cursor = connection.cursor()

            #使用%s作为占位符，进行注入
            query = "SELECT sign1, sign2, sign3, sign4, sign5, sign6 FROM vocation_signs WHERE domain = %s AND vocation = %s"

            # 将要查询的变量作为一个元组传递给 execute 方法
            cursor.execute(query, (adomain, avocation))

            # 获取查询结果
            signs = cursor.fetchone()

            if signs:
                return tuple(str(s) for s in signs)
            else:
                print(f"信息: 未在数据库中找到 domain='{adomain}', vocation='{avocation}' 的记录。")
                return None

    except Error as e:
        print(f"数据库错误: {e}")
        return None  # 发生任何数据库错误都返回 None

    finally:
        # 关闭数据库连接资源
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()



if __name__=="__main__":
    signs = getVocationSigns("大数据:大数据开发工程师")
    for sign in signs:
        print(sign)
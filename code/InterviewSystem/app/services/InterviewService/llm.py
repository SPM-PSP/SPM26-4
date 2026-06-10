"""
    llm模块负责调用大模型对话以及实现功能。包括：
    1.SparkLLMQuestion根据面试者的回答（即语音转文本之后的answer结果）进行针对性提问
    2.SparkLLMSentence能够将asr模块返回的文本进行修正，使得转录文本更加准确
    3.SparkLLMReport 根据面试者的交互内容、视频分析的结果，基于面试岗位对应的核心指标进行打分和最终评价
"""
import json
from typing import Dict, Any, List
from openai import OpenAI

# ==================== 配置信息（阿里云百炼 DashScope）====================
LLM_API_KEY = "sk-44be5cbebff74727ae8460ebc4079353"
LLM_API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_MODEL = "qwen3.5-plus"


def create_llm_client(api_key: str = LLM_API_KEY, base_url: str = LLM_API_BASE) -> OpenAI:
    """
    创建 LLM 客户端（兼容 openai >= 1.0.0 版本）
    
    Args:
        api_key: 阿里云百炼 API Key
        base_url: API 基础 URL
    
    Returns:
        OpenAI 客户端实例
    """
    return OpenAI(
        api_key=api_key,
        base_url=base_url
    )


def call_llm(messages: list, model: str = DEFAULT_MODEL, temperature: float = 0.5, max_tokens: int = 4096) -> str:
    """
    通用的 LLM 调用函数
    
    Args:
        messages: 对话消息列表，格式: [{"role": "system/user/assistant", "content": "..."}]
        model: 模型名称，默认为 qwen3.5-plus
        temperature: 温度参数，控制回答的随机性
        max_tokens: 最大生成 token 数
    
    Returns:
        AI 的响应文本
    """
    client = create_llm_client()
    
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return completion.choices[0].message.content


#在使用大模型进行提问的时候，可以选择根据回答进行提问，也可以选择根据简历进行提问，也可以选择二者一起进行提问
#问题和回答都是在InterviewService.py中追加
def _convert_history_roles(history: list) -> list:
    """
    将历史记录中的角色转换为标准角色格式
    阿里云百炼API只接受: system, assistant, user, tool, function
    需要将 'ai' 转换为 'assistant'
    
    Args:
        history: 原始历史记录列表
        
    Returns:
        转换后的历史记录列表
    """
    converted = []
    for item in history:
        role = item.get('role', '')
        content = item.get('content', '')
        
        # 将 'ai' 角色转换为 'assistant'
        if role == 'ai':
            converted.append({"role": "assistant", "content": content})
        elif role in ['system', 'assistant', 'user', 'tool', 'function']:
            converted.append({"role": role, "content": content})
        else:
            # 未知角色默认为 user
            converted.append({"role": "user", "content": content})
    
    return converted


def SparkLLMQuestion(job:str, history:list, choice:int, user_answer:str=None, resume_content:str=None)->str:
    choice = int(choice)
    
    # 转换历史记录中的角色格式
    converted_history = _convert_history_roles(history)
    
    if choice==1 and resume_content is not None and user_answer is not None:#结合简历和问题回答提问
        combined_text="回答：" + user_answer+'\n'
        combined_text+="个人简历信息："
        combined_text+=resume_content
        #设置大模型对话背景，并且对大模型所提问题进行字数限制，避免问题过长
        systemtip=f'你是一名面试官，参见面试的面试者要面试的领域和岗位是：{job}。你需要根据候选人的简历和回答的内容进行综合提问,回答的内容可能是之前的提问，也可能是自我介绍。但是只提一个问题，并且提出问题的字数不超过30字。'
        messages = [{"role": "system", "content": systemtip}]
        messages.extend(converted_history)
        messages.append({"role": "user", "content": combined_text})
        response = call_llm(messages, temperature=0.5, max_tokens=1024)
        return response

    elif choice==2 and user_answer is not None:#只针对问题的回答进行提问（追问）
        systemtip=f'你是一名面试官，参见面试的面试者要面试的领域和岗位是：{job}。你需要根据候选人对问题的回答进行针对性提出一个问题，并且提出问题的字数不超过30字。'
        messages = [{"role": "system", "content": systemtip}]
        messages.extend(converted_history)
        messages.append({"role": "user", "content": user_answer})
        response = call_llm(messages, temperature=0.5, max_tokens=1024)
        return response
    
    elif choice==3 and resume_content is not None:#只针对简历提问
        systemtip=f'你是一名面试官，参见面试的面试者要面试的领域和岗位是：{job}。你现在只需要根据候选人的简历进行提问，提出一个问题，并且不能使之前提过的问题，并且提出问题的字数不超过30字。'
        messages = [{"role": "system", "content": systemtip}]
        messages.extend(converted_history)
        messages.append({"role": "user", "content": resume_content})
        response = call_llm(messages, temperature=0.5, max_tokens=1024)
        return response
    else:
        print("choice typeError")
        return ""


#这是一个字符串处理的大模型工具，将转录之后并使用算法初步优化的文本内容给大模型进行更加精准的转录，返回最终转录的结果
def SparkLLMSentence(trans:str)->str:
    systemtip='你是一个字符串的去重复工具，我会给你一段字符串文本，你需要识别出其中哪些部分语音转文本时由于存储导致的重复，优化文本内容。'
    messages = [
        {"role": "system", "content": systemtip},
        {"role": "user", "content": trans}
    ]
    response = call_llm(messages, temperature=0.5, max_tokens=1024)
    return response


def SparkLLMReport(job: str, history: List[Dict[str, str]], report: Dict[str, Any], signs: tuple):
    """
    调用大模型进行综合评估，包含了完整的对话历史。
    :param job: 应聘岗位
    :param history: 对话历史列表，例如 [{'role': 'user', 'content': '...'}, ...]
    :param report: 行为和言语分析的报告字典
    :param signs: 岗位核心评估指标元组
    :return: 一个包含LLM评估结果的字典
    """
    # 安全地提取所有需要的数据
    pose_data = report.get("pose", {})          #姿态分析，显示低头比率等四项数据
    emotion_data = report.get("emotion", {})    #表情分析，微表情统计。涵盖七种表情，统计每种表情在面试过程中出现的比率
    eye_contact_data = report.get("eye_contact", {})    #眼神接触统计
    hand_movement_data = report.get("hand_movement", {})    #手部移动的统计，包括计算全面试过程中的手部移动总量、平均移动量
    object_tracker_data = report.get("object_tracker", {})  #身体移动分析，统计面试全流程身体移动总量和平均移动量
    speech_data = report.get("stutter_speed_rhythm", {})    #口吃分析、语速、语调分析，得到语言阻塞的置信度和语速语调的评分
    stutter_data = speech_data.get("stutter_analysis", {})
    rhythm_data = speech_data.get("rhythm_analysis", {})
    speed_data = speech_data.get("speed_analysis", {})

    # 将对话历史格式化为字符串
    formatted_history = "\n".join([f"- {item['role']}: {item['content']}" for item in history])

    # 构建一个包含所有信息的Prompt
    system_tip = f"""
    你是一位资深的AI面试官和职业发展顾问。你的任务是根据下面提供的**面试对话内容**和**全方位量化分析数据**，为一位应聘者撰写一份专业、客观、富有建设性的面试评估报告。

    ### 候选人信息
    - **应聘岗位:** {job}

    ### 核心评估维度
    请你围绕以下几个核心维度，对候选人进行综合打分（0-100分），并撰写最终的评语。你需要将候选人在对话中展现的知识能力与行为数据结合起来进行判断：
    - {', '.join(signs)}

    ---
    ### 面试对话记录 (最重要的评估依据)
    {formatted_history}
    ---

    ### 行为与言语量化分析数据 (用于辅助判断沟通状态和专业性)

    **1. 身体姿态分析 (Body Pose):**
    - 低头 (Head looks down): {pose_data.get("Head looks down", 0.0):.2f}%
    - 手叉腰 (Hand on waist): {pose_data.get("Hand on waist", 0.0):.2f}%
    - 正常姿态 (Normal): {pose_data.get("Normal", 0.0):.2f}%
    - 双手紧握/合十 (Hands clasped): {pose_data.get("Hands clasped", 0.0):.2f}%

    **2. 面部情绪分析 (Emotion):**
    - 中性 (Neutral): {emotion_data.get("neutral", 0.0):.2f}%
    - 开心 (Happy): {emotion_data.get("happy", 0.0):.2f}%
    - 悲伤 (Sad): {emotion_data.get("sad", 0.0):.2f}%
    - 生气 (Angry): {emotion_data.get("angry", 0.0):.2f}%
    - 害怕 (Fear): {emotion_data.get("fear", 0.0):.2f}%
    - 厌恶 (Disgust): {emotion_data.get("disgust", 0.0):.2f}%
    - 惊讶 (Surprise): {emotion_data.get("surprise", 0.0):.2f}%

    **3. 眼神接触分析 (Eye Contact):**
    - 建立接触 (Contact): {eye_contact_data.get("Contact", 0.0):.2f}%
    - 未建立接触 (Not Contact): {eye_contact_data.get("Not Contact", 0.0):.2f}%

    **4. 手部活动量分析 (Hand Movement):**
    - 总移动量: {hand_movement_data.get("total_movement", 0.0):.2f}
    - 平均每帧移动量: {hand_movement_data.get("average_movement_per_frame", 0.0):.2f}

    **5. 身体整体移动评估 (Body Movement):**
    - 总移动距离: {object_tracker_data.get("total_distance", 0.0):.2f}
    - 平均每帧移动距离: {object_tracker_data.get("average_distance_per_frame", 0.0):.2f}
    - 系统建议: {object_tracker_data.get("assessment", "无")}

    **6. 言语特征分析 (Speech Analysis):**
    - 流畅度 (Stutter - 置信度):
      - 不口吃 (Non-stutter): {stutter_data.get("nonstutter", 0.0):.4f}
      - 重复 (Repetition): {stutter_data.get("repetition", 0.0):.4f}
      - 延长音 (Prolongation): {stutter_data.get("prolongation", 0.0):.4f}
      - 语塞 (Blocks): {stutter_data.get("blocks", 0.0):.4f}
    - 语调 (Rhythm):
      - 得分: {rhythm_data.get("score", 0)}
      - 评价: {rhythm_data.get("description", "无")}
    - 语速 (Speed):
      - 得分: {speed_data.get("score", 0):.1f}
      - 评价: {speed_data.get("description", "无")}


    ### 你的任务

    请根据以上所有信息，特别是**面试对话记录**，完成以下任务，并以一个JSON对象的格式返回结果：

    1.  **"summary"**: 撰写一段**详细的、结构化的**综合评语，**总字数必须在500字以上**。评语必须包含以下三个明确的部分：
    - **优点总结 (Strengths):** 详细阐述候选人在专业知识、项目经验和逻辑思维方面的优点，至少列举3个具体例子。
    - **改进建议 (Areas for Improvement):** 针对行为数据（如眼神、姿态、语速）中反映出的问题，提出至少5个具体的、可操作的改进建议。
    - **综合展望 (Overall Outlook):** 结合其职业规划和整体表现，对候选人的发展潜力和岗位匹配度进行总结性评价。

    2.  **"radarCharData"**: 一个JSON对象，键是上面列出的核心评估维度，值是你对该维度的评分（0-100的整数）。
    3.  **"overall_score"**: 一个综合总分（0-100的浮点数，保留一位小数）。

    请严格按照JSON格式输出，不包含任何额外的解释性文字。**再次强调，"summary"字段的内容必须充实，达到500字以上的长度要求。
    在进行评价时必须使用您来代指面试者
    一定要严格按照Json格式输出，也不要在JSON数据前后返回多余'''符号，就提供没有美化、没有多余解释的严格的JSON格式数据**
    """

    # 构建消息并调用大模型
    messages = [
        {"role": "system", "content": system_tip},
        {"role": "user", "content": "请根据我提供的信息，开始进行评估。"}
    ]

    response = call_llm(messages, temperature=0.5, max_tokens=4096)

    # 解析返回的JSON字符串
    try:
        # 1. 获取并清理首尾的空白字符
        raw_content = response.strip()

        # 2. 找到JSON内容的起止位置，这是最稳妥的提取方法
        start_index = raw_content.find('{')
        end_index = raw_content.rfind('}')

        if start_index != -1 and end_index != -1:
            # 3. 提取出大括号内的核心内容
            json_string = raw_content[start_index: end_index + 1]

            # 4. 【核心修正】替换掉字符串中非法的换行符
            #    这会把 "提\n的" 修正为 "提的"，从而使JSON合法
            valid_json_string = json_string.replace('\n', '')

            # 5. 使用修正后的合法字符串进行解析
            llm_result_dict = json.loads(valid_json_string)
            return llm_result_dict
        else:
            # 如果连大括号都找不到，说明格式完全错误
            print("错误：大模型响应中未找到有效的JSON对象。")
            print("LLM原始输出:", response)
            return {}

    except json.JSONDecodeError as e:
        print(f"错误：JSON解析失败。错误信息: {e}")
        print("LLM原始输出:", response)
        # 在调试时，打印一下我们尝试解析的字符串会很有帮助
        # print("尝试解析的字符串:", valid_json_string)
        return {}  # 返回一个空字典，避免下游代码因返回None而出错


#使用示例
if __name__ == '__main__':
    # 模拟的一份详细面试对话历史记录
    mock_history = [
        {
            "role": "ai",
            "content": "你好，欢迎参加本次面试。请先用2-3分钟做一个自我介绍，重点突出一下你的项目经验和技术栈。"
        },
        {
            "role": "user",
            "content": "面试官您好，我叫李明。我是一名有三年工作经验的大数据开发工程师。在上一家公司，我主要负责数据仓库的构建和ETL流程的开发。我熟悉Hadoop生态系统，特别是HDFS、MapReduce、Hive和HBase。在数据处理方面，我熟练使用Spark进行大规模数据的批处理和流式处理，也了解Flink的一些基本概念。我参与过两个主要项目，一个是电商用户行为分析系统，另一个是实时风控预警平台。我希望能有机会加入贵公司，为数据平台建设贡献我的力量。"
        },
        {
            "role": "ai",
            "content": "好的，听起来你的经验很匹配。我们来聊聊你提到的实时风控项目。能详细介绍一下这个项目的数据流是怎样的吗？以及你在其中主要负责哪一部分？"
        },
        {
            "role": "user",
            "content": "嗯...好的。这个项目的数据源主要是业务数据库的binlog和前端的用户行为日志。我们使用Canal来实时捕获MySQL的增删改数据，然后将这些数据和用户行为日志一起发送到Kafka消息队列中。接着，我们有一个Spark Streaming作业会消费Kafka中的数据，进行实时的数据清洗、关联和特征计算。比如，我们会计算用户短时间内的交易频率、登录地点异常等特征。计算出的特征会写入到Redis中，供风控规则引擎快速查询。我主要负责的就是Spark Streaming这部分的开发和调优，确保数据处理的低延迟和高吞吐。"
        },
        {
            "role": "ai",
            "content": "明白了。在Spark Streaming的调优方面，你遇到过什么挑战吗？比如数据倾斜问题，你是如何解决的？"
        },
        {
            "role": "user",
            "content": "数据倾斜确实是一个常见的问题。我们遇到过几次。一种情况是某些大客户的key（比如用户ID）数据量特别大。我的解决方法是，首先对这些倾斜的key进行识别，然后给它们加上随机前缀，把一个大的key打散成多个小的key，这样数据就能均匀地分布到不同的Executor上。处理完之后，再把随机前缀去掉，还原成原始的key。呃...另外，对于一些Join操作，我们也会尽量使用广播变量（Broadcast Join）来处理小表，避免shuffle过程中的数据倾斜。"
        },
        {
            "role": "ai",
            "content": "听起来处理得不错。最后一个问题，你对未来的职业发展有什么规划吗？"
        },
        {
            "role": "user",
            "content": "我希望在未来三到五年内，能够从一个执行者成长为能独立负责一个数据模块的架构师。我希望能更深入地研究数据湖、湖仓一体这样的新技术架构，并且提升自己在系统设计和团队协作方面的能力。我对技术充满热情，也乐于分享，希望未来能有机会带领一个小团队。"
        }
    ]

    # 模拟的一份从ComprehensiveAnalyzer.format_report_to_json_structure() 函数返回的标准格式的报告字典
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

    # 模拟的一份从getVocationSigns()函数中返回的指标元组
    mock_signs = (
        "专业知识水平",
        "逻辑思维能力",
        "沟通表达能力",
        "项目经验匹配度",
        "技能匹配度",
        "临场应变能力"
    )

    result=SparkLLMReport('大数据：大数据开发工程师',mock_history,mock_report,mock_signs)  #这里返回的result已经是字典了
    print(result)

    if 'summary' in result:
        mock_report['summary'] = result['summary']
    if 'radarCharData' in result and isinstance(result['radarCharData'], dict):
        mock_report['radarCharData'].update(result['radarCharData'])
    if 'overall_score' in result:
        mock_report['overall_score'] = result['overall_score']

    print("\n" + "=" * 25 + " 最终生成的完整JSON报告 " + "=" * 25)
    # indent=2 使打印出来的JSON格式更美观
    print(json.dumps(mock_report, ensure_ascii=False, indent=2))

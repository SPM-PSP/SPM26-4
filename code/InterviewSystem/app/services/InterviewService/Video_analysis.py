"""
创建analysisAll对象，对合并后的mp4视频进行综合分析，
根据job查询数据库得到职业对应的五个核心指标，
将分析得到json数据、面试过程的全部对话（提问与用户的回答）提供给综合评测大模型
让大模型基于五大核心指标以及全部的对话数据、分析数据进行综合评测，
为核心指标打分、进行总体评分
同时调用StudyRoute方法，根据推荐算法得到推荐学习路线
"""

import json
from datetime import datetime



def my_frontend_callback(message: str):
    """示例回调函数，用于向前端发送进度。"""
    print(f"[进度更新]: {message}")


class FullReport:
    def __init__(self, video_path: str, job: str, history: list, user_id: str, date: str, videoID: str,process_tip_function=None):
        """
        初始化完整报告生成器。
        """
        self.job = job
        self.video_path = video_path
        self.history = history
        self.user_id = user_id
        self.date = date
        self.videoID = videoID
        self.process_tip_function = process_tip_function  #将视频分析进度推送到前端的函数，这个函数在InterviewService中定义

        # 实例属性，用于存储中间和最终结果
        self.report = None
        self.signs = None

    def run_pipeline(self):
        """
        执行完整的分析、评估和存储流水线。
        这是外部调用的唯一入口。
        """
        print("=" * 20 + " 开始面试综合评估流程 " + "=" * 20)

        # 运行基础的音视频分析
        if not self.getBasicReport():
            print("错误：基础分析失败，流程中止。")
            return None

        # 获取岗位评估指标
        if not self.getVocationSigns():
            print("警告：未能获取岗位指标，后续评估可能不准确。")
            # 如果获取指标失败就使用后面设置的通用指标

        # 调用大模型进行综合评估和打分
        if not self.getLLMReport():
            print("错误：大模型评估失败，流程中止。")
            return None

        # 调用推荐算法生成学习路线
        self.getStudyRoute()

        # 将最终的完整报告存入数据库
        if not self.insertRpg():
            print("错误：报告存入数据库失败。")
            return None

        print("\n" + "=" * 20 + " 面试综合评估流程全部完成！ " + "=" * 20)
        return self.report

    def getBasicReport(self):
        from app.services.Body_Emotion.analysisAll import ComprehensiveAnalyzer

        """ComprehensiveAnalyzer内部使用并行的音视频分析"""
        try:
            print("\n正在执行基础音视频分析")
            pipeline = ComprehensiveAnalyzer(self.video_path)
            partial_report = pipeline.run_full_analysis(
                analyses_per_second=2,  # 手动设置采样率，即每一秒进行多少次采样分析，为了提高效率这里选择了每秒两次采样
                progress_callback=self.process_tip_function  #这里使用推送函数，将分析的进度发送给前端显示，从而提高了用户使用的交互体验感
            )
            # self.report 现在是一个包含所有基础分析结果的字典
            self.report = ComprehensiveAnalyzer.format_report_to_json_structure(partial_report)
            print("基础音视频分析完成")
            return True
        except Exception as e:
            print(f"在基础音视频分析阶段发生错误: {e}")
            return False

    def getVocationSigns(self):
        from app.services.DataBase_connect.GetvocationSigns import getVocationSigns
        """从数据库种获取岗位核心指标。"""
        try:
            print(f"\n正在为岗位 '{self.job}' 查询核心指标")
            self.signs = getVocationSigns(job=self.job)
            if self.signs:
                print(f"成功获取指标: {self.signs}")
                return True
            else:
                # 备用方案，以防数据库查询失败
                self.signs = ("专业知识水平", "逻辑思维能力", "沟通表达能力", "项目经验匹配度", "技能匹配度",
                              "临场应变能力")
                print(f"警告: 未能从数据库获取指标，将使用默认指标: {self.signs}")
                return True  # 即使使用默认值，也认为这个步骤成功
        except Exception as e:
            print(f"在 _get_vocation_signs 阶段发生错误: {e}")
            return False

    def getLLMReport(self):
        from app.services.InterviewService.llm import SparkLLMReport
        """调用大模型，并用返回结果更新报告。"""
        try:
            print("\n正在调用大模型进行综合评估")
            llm_results = SparkLLMReport(self.job, self.history, self.report, self.signs)

            if not llm_results or not isinstance(llm_results, dict):
                print("错误：大模型没有返回有效的评估结果。")
                return False

            # 将LLM分析结果整合到self.report中
            print("正在合并LLM评估结果...")
            if 'summary' in llm_results:
                self.report['summary'] = llm_results['summary']
            if 'radarCharData' in llm_results and isinstance(llm_results['radarCharData'], dict):
                self.report['radarCharData'].update(llm_results['radarCharData'])
            if 'overall_score' in llm_results:
                self.report['overall_score'] = llm_results['overall_score']

            print("大模型评估完成并已合并报告")
            return True
        except Exception as e:
            print(f"在大模型分析阶段发生错误: {e}")
            return False

    def getStudyRoute(self):
        from app.services.InterviewService.StudyRoute import recommend_study_route
        """调用推荐算法。"""
        parts = self.job.split(':', 1)
        if len(parts) != 2:
            print(f"错误: 不合法的Job格式 '{self.job}'。应为 '领域:职业'。")
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
        print("\n正在生成学习路线")
        self.report=recommend_study_route(self.report,adomain,avocation)
        print("学习路线生成完成")

    def insertRpg(self):
        """将最终报告存入数据库，先保存视频信息再保存报告"""
        try:
            from app.services.DataBase_connect.Storereport import InsertVideo, InsertReport
            
            # 1. 先保存视频信息到 video 表
            print("\n正在将视频信息存入数据库")
            # 构造视频相对路径: accountID/videoID.ext
            video_path = f"{self.user_id}/{self.videoID}.mp4"
            video_id = InsertVideo(
                accountID=self.user_id,
                video_path=video_path,
                date=self.date
            )
            
            if video_id == -1:
                print("错误：视频信息保存失败")
                return False
            
            # 2. 再保存报告到 rpg 表，使用真实的视频ID
            print("正在将最终报告存入数据库")
            success = InsertReport(
                job=self.job,
                accountID=self.user_id,
                videoID=str(video_id),  # 传入数据库生成的真实视频ID
                date=self.date,
                report=self.report
            )
            return success
        except Exception as e:
            print(f"在存入报告阶段发生错误: {e}")
            import traceback
            traceback.print_exc()
            return False


#示例执行代码
if __name__ == '__main__':
    # 模拟的输入数据
    mock_video_path = "E:\Daily_File\RACE\第十四届中国软件杯\第十四届中国软件杯提交作品集\项目源码\服务器后端代码\InterviewSystem\InterviewSystem\DataFile\Video\\testuser001\\20250717154045.mp4"
    mock_job_title = "大数据:大数据开发工程师"
    mock_user_id = "user_157613"
    mock_date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    mock_video_id = datetime.now().strftime('%Y%m%d%H%M%S')

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
    # 创建并运行完整的流水线
    full_report= FullReport(
        video_path=mock_video_path,
        job=mock_job_title,
        history=mock_history,
        user_id=mock_user_id,
        date=mock_date_str,
        videoID=mock_video_id,
        process_tip_function=my_frontend_callback
    )

    final_report = full_report.run_pipeline()

    if final_report:
        print("\n" + "=" * 25 + " 最终生成的完整JSON报告（预览） " + "=" * 25)
        print(json.dumps(final_report, ensure_ascii=False, indent=2))
"""
Audio_to_question模块 - 封装语音转文本和问题生成逻辑
负责：
1. 调用ASR模块进行语音转写
2. 调用文本分析模块进行打分
3. 根据打分结果和历史记录调用LLM生成下一个问题
"""
import random
import traceback


class Audio_to_question:
    def __init__(self, job: str, history: list, resume_content: str = None):
        """
        初始化音频处理和问题生成器
        
        Args:
            job: 面试岗位
            history: 对话历史记录
            resume_content: 简历内容（可选）
        """
        from app.services.InterviewService.Asr import AudioTranscriber
        from app.services.InterviewService.textAnalysis import SparkFileProcessor

        self.transcriber = AudioTranscriber()
        self.textAnalysis = SparkFileProcessor()
        self.job = job
        self.history = history.copy() if history else []
        self.resume_content = resume_content
        self.transcription = ""
        self.score = 0

    def transcribeAndScore(self, audio_path: str) -> str:
        """
        执行语音转录和文本分析打分
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            str: 转录的文本结果，失败返回空字符串
        """
        print(f"开始处理音频文件: {audio_path}")
        
        try:
            # 1. 调用ASR进行语音转写
            self.transcription = self.transcriber.transcribe_mp3(audio_path)
            print(f"ASR转录结果: {self.transcription[:50]}..." if len(self.transcription) > 50 else f"ASR转录结果: {self.transcription}")
            
        except Exception as e:
            print(f"转录失败: {e}")
            traceback.print_exc()
            self.transcription = ""
        finally:
            self.transcriber.close()

        # 如果转录失败，直接返回空字符串
        if not self.transcription:
            self.score = 0
            print("警告：转录结果为空")
            return ""

        # 2. 调用文本分析进行打分
        try:
            score_result = self.textAnalysis.quantitative_score(self.transcription)
            if isinstance(score_result, dict) and score_result.get('success'):
                self.score = score_result.get('data', 0)
                print(f"文本分析打分完成，分数: {self.score}")
            else:
                self.score = 0
                print("警告：文本评分结果格式不符合预期或处理失败")
        except Exception as e:
            print(f"文本分析综合打分失败：{e}")
            traceback.print_exc()
            self.score = 0

        return self.transcription

    def getNextQuestion(self, question_count: int) -> str:
        """
        根据分数和历史记录生成下一个问题
        
        Args:
            question_count: 当前问题序号
            
        Returns:
            str: 生成的问题
        """
        print(f"生成第 {question_count} 个问题")
        
        if question_count <= 4:
            # 第一阶段：基于简历和自我介绍提问
            return self.basedOnResumeSelfIntroduction()
        else:
            # 第二阶段：基于数据库题库提问
            return self.basedOnDatabase()

    def basedOnResumeSelfIntroduction(self) -> str:
        """
        第一阶段提问逻辑：基于简历和自我介绍
        
        评分策略：
        - score >= 85: 回答质量高，针对回答进行追问
        - score < 60: 回答质量低，针对简历提问
        - 60 <= score < 85: 结合回答和简历提问
        """
        from app.services.InterviewService.llm import SparkLLMQuestion

        try:
            if self.score >= 85:
                print("回答质量高，针对回答进行追问")
                return SparkLLMQuestion(self.job, self.history, 2, self.transcription, resume_content=None)
            elif self.score < 60:
                print("回答质量低，针对简历提问")
                return SparkLLMQuestion(self.job, self.history, 3, user_answer=None, resume_content=self.resume_content)
            else:
                print("回答质量中等，结合回答和简历提问")
                return SparkLLMQuestion(self.job, self.history, 1, self.transcription, self.resume_content)
        except Exception as e:
            print(f"生成问题失败: {e}")
            traceback.print_exc()
            return "抱歉，我暂时无法生成问题，请继续介绍你自己。"

    def basedOnDatabase(self) -> str:
        """
        第二阶段提问逻辑：基于数据库题库
        
        评分策略：
        - score >= 85: 回答质量高，针对回答进行追问
        - score < 85: 回答质量一般，从数据库选题
        """
        from app.services.DataBase_connect.GetQuestion import getQuestion
        from app.services.InterviewService.llm import SparkLLMQuestion

        try:
            if self.score >= 85:
                print("回答质量高，针对回答进行追问")
                return SparkLLMQuestion(self.job, self.history, 2, self.transcription)
            else:
                print("回答质量一般，从数据库选题")
                degree = random.choice(["简单", "中等", "困难"])
                question = getQuestion(self.job, degree)
                return question if question else "我们换一个话题吧，请谈谈你对我们公司的了解。"
        except Exception as e:
            print(f"生成问题失败: {e}")
            traceback.print_exc()
            return "抱歉，我暂时无法生成问题，请继续介绍你的项目经验。"


# 使用示例
if __name__ == "__main__":
    # 模拟历史对话
    mock_history = [
        {"role": "ai", "content": "你好，欢迎参加本次面试。请先用2-3分钟做一个自我介绍，重点突出一下你的项目经验和技术栈。"},
        {"role": "user", "content": "面试官您好，我叫李明。我是一名有三年工作经验的大数据开发工程师。在上一家公司，我主要负责数据仓库的构建和ETL流程的开发。我熟悉Hadoop生态系统，特别是HDFS、MapReduce、Hive和HBase。在数据处理方面，我熟练使用Spark进行大规模数据的批处理和流式处理，也了解Flink的一些基本概念。我参与过两个主要项目，一个是电商用户行为分析系统，另一个是实时风控预警平台。我希望能有机会加入贵公司，为数据平台建设贡献我的力量。"},
        {"role": "ai", "content": "好的，听起来你的经验很匹配。我们来聊聊你提到的实时风控项目。能详细介绍一下这个项目的数据流是怎样的吗？以及你在其中主要负责哪一部分？"},
        {"role": "user", "content": "嗯...好的。这个项目的数据源主要是业务数据库的binlog和前端的用户行为日志。我们使用Canal来实时捕获MySQL的增删改数据，然后将这些数据和用户行为日志一起发送到Kafka消息队列中。接着，我们有一个Spark Streaming作业会消费Kafka中的数据，进行实时的数据清洗、关联和特征计算。比如，我们会计算用户短时间内的交易频率、登录地点异常等特征。计算出的特征会写入到Redis中，供风控规则引擎快速查询。我主要负责的就是Spark Streaming这部分的开发和调优，确保数据处理的低延迟和高吞吐。"},
        {"role": "ai", "content": "明白了。在Spark Streaming的调优方面，你遇到过什么挑战吗？比如数据倾斜问题，你是如何解决的？"},
        {"role": "user", "content": "数据倾斜确实是一个常见的问题。我们遇到过几次。一种情况是某些大客户的key（比如用户ID）数据量特别大。我的解决方法是，首先对这些倾斜的key进行识别，然后给它们加上随机前缀，把一个大的key打散成多个小的key，这样数据就能均匀地分布到不同的Executor上。处理完之后，再把随机前缀去掉，还原成原始的key。呃...另外，对于一些Join操作，我们也会尽量使用广播变量（Broadcast Join）来处理小表，避免shuffle过程中的数据倾斜。"},
        {"role": "ai", "content": "听起来处理得不错。最后一个问题，你对未来的职业发展有什么规划吗？"},
        {"role": "user", "content": "我希望在未来三到五年内，能够从一个执行者成长为能独立负责一个数据模块的架构师。我希望能更深入地研究数据湖、湖仓一体这样的新技术架构，并且提升自己在系统设计和团队协作方面的能力。我对技术充满热情，也乐于分享，希望未来能有机会带领一个小团队。"}
    ]
    
    question_re = Audio_to_question(
        job="大数据：大数据开发工程师", 
        history=mock_history, 
        resume_content="我是四川大学软件学院的一名学生，主修软件工程专业，在校期间参与过多个大数据相关项目。"
    )
    
    # 使用测试音频文件
    question_re.transcribeAndScore("test.mp3")
    question = question_re.getNextQuestion(2)
    print("\n生成的问题:")
    print(question)

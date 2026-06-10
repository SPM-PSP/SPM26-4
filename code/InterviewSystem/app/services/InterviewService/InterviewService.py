"""
面试流程服务管理器 - 管理整个面试会话的生命周期
负责：
1. WebSocket连接管理
2. 视频流接收和片段录制
3. 音频提取和ASR转写
4. LLM问题生成
5. 视频合并和分析报告生成
"""
import json
import os
import asyncio
import re
import uuid
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
import traceback

import pdfplumber

from app.services.InterviewService.Audio_to_question import Audio_to_question


def my_frontend_callback(message: str):
    """占位符回调函数，用于传递给分析模块"""
    print(f"[分析进度更新]: {message}")


class InterviewServiceManager:
    """
    管理整个面试会话的生命周期，包括实时交互和最终分析。
    采用异步设计，将耗时任务卸载到后台线程，以保持WebSocket的响应性。
    """
    SILENCE_TIMEOUT = 12.0  # 接收视频流的超时时间（秒）
    MAX_QUESTIONS = 8       # 最大问题数量

    def __init__(self, user_id: str, date: str, package_root: str, resume_path: str, job: str):
        """
        初始化面试服务管理器
        
        Args:
            user_id: 用户ID
            date: 面试日期时间
            package_root: 项目根目录
            resume_path: 简历文件路径
            job: 面试岗位
        """
        self.user_id = user_id
        self.date = date
        self.package_root = package_root
        self.resume_path = resume_path
        self.job = job

        # 面试数据
        self.resume_content = ""
        self.history = []
        self.question_count = 0

        # 视频录制状态
        self.is_recording = False
        self.current_webm_path = None
        self.current_fragment_stream = None
        self.recorded_webm_paths = []

        # 文件路径
        self.temp_video_path = os.path.join(self.package_root, "tempFile", "Video", self.user_id)
        self.temp_audio_path = os.path.join(self.package_root, "tempFile", "Audio", self.user_id)

        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=3)

        # 初始化设置
        self.getResumeContent()
        self.createDirectory()

        print(f"面试服务管理器初始化完成，用户ID: {user_id}，岗位: {job}")

    def createDirectory(self):
        """确保临时文件目录存在"""
        try:
            os.makedirs(self.temp_video_path, exist_ok=True)
            os.makedirs(self.temp_audio_path, exist_ok=True)
            print(f"临时目录已创建: {self.temp_video_path}")
        except Exception as e:
            print(f"创建目录失败: {e}")

    def getResumeContent(self):
        """从PDF简历中提取文本内容"""
        try:
            with pdfplumber.open(self.resume_path) as pdf:
                text = "".join(page.extract_text() or "" for page in pdf.pages)
                self.resume_content = text.replace("\n", " ").strip()
            print("简历内容提取成功")
        except Exception as e:
            print(f"警告：简历解析失败 - {e}")
            self.resume_content = "无法解析简历内容。"

    def startNewFragment(self):
        """为新的回答片段准备录制文件"""
        fragment_id = f"raw_{len(self.recorded_webm_paths):03d}_{uuid.uuid4().hex[:8]}"
        self.current_webm_path = os.path.join(self.temp_video_path, f"{fragment_id}.webm")
        
        try:
            self.current_fragment_stream = open(self.current_webm_path, "wb")
            self.is_recording = True
            print(f"开始录制新片段: {self.current_webm_path}")
        except Exception as e:
            print(f"创建录制文件失败: {e}")
            self.current_webm_path = None
            self.current_fragment_stream = None
            self.is_recording = False

    def writeVideoChunk(self, data: bytes):
        """将收到的视频流数据块写入文件"""
        if self.is_recording and self.current_fragment_stream:
            try:
                self.current_fragment_stream.write(data)
            except Exception as e:
                print(f"写入视频数据失败: {e}")

    def stopCurrentFragment(self):
        """停止当前片段的录制并保存路径"""
        if self.is_recording and self.current_fragment_stream:
            self.is_recording = False
            try:
                self.current_fragment_stream.close()
                self.current_fragment_stream = None
                
                # 检查文件是否有效
                if os.path.exists(self.current_webm_path) and os.path.getsize(self.current_webm_path) > 1024:
                    print(f"回答片段已保存: {self.current_webm_path}")
                    self.recorded_webm_paths.append(self.current_webm_path)
                else:
                    print(f"片段文件过小或不存在，已丢弃: {self.current_webm_path}")
                    if os.path.exists(self.current_webm_path):
                        os.remove(self.current_webm_path)
            except Exception as e:
                print(f"停止录制失败: {e}")

    async def processLastVideo_getQuestion(self) -> str:
        """
        [异步接口] 处理上一个回答片段并获取下一个问题。
        这是WebSocket端点调用的主要方法。
        """
        self.question_count += 1
        print(f"\n===== 处理第 {self.question_count} 个问题 =====")

        # 检查是否达到最大问题数
        if self.question_count > self.MAX_QUESTIONS:
            return "面试结束，感谢您的参与！请返回个人中心查看面试报告。"

        webm_path = self.current_webm_path

        # 如果是第一次提问（没有有效的上一个片段）
        if not webm_path or not os.path.exists(webm_path) or os.path.getsize(webm_path) < 1024:
            first_question = "您好，我们现在面试开始。请先做一个简单的自我介绍吧。"
            self.history.append({"role": "ai", "content": first_question})
            print(f"发送第一个问题: {first_question}")
            return first_question

        # 将所有耗时的同步操作放入后台线程
        try:
            question = await asyncio.to_thread(self.getNextQuestion, webm_path)
        except Exception as e:
            print(f"处理问题时发生异常: {e}")
            traceback.print_exc()
            question = "抱歉，处理您的回答时遇到一些问题，请继续回答。"

        # 将新问题添加到历史记录中
        self.history.append({"role": "ai", "content": question})
        print(f"生成问题: {question}")
        
        return question

    def getNextQuestion(self, webm_path: str) -> str:
        """[同步阻塞] 包含了所有提问前的耗时操作，在后台线程中执行。"""
        try:
            # 1. 提取音频
            mp3_path = self.extractAudio(webm_path)
            if not mp3_path:
                return "处理您的回答时遇到一些技术问题，我们可以跳过这个话题，继续下一个问题吗？"

            # 2. 初始化提问器，传入最新的历史记录
            audio_processor = Audio_to_question(self.job, self.history, self.resume_content)

            # 3. 转录并打分
            user_answer = audio_processor.transcribeAndScore(mp3_path)
            print(f"用户回答转录结果: {user_answer[:100]}..." if len(user_answer) > 100 else f"用户回答: {user_answer}")

            # 4. 将用户的回答添加到历史记录中
            self.history.append({"role": "user", "content": user_answer})

            # 5. 根据最新的历史记录和分数，获取下一个问题
            next_question = audio_processor.getNextQuestion(self.question_count)
            return next_question

        except Exception as e:
            print(f"获取下一个问题失败: {e}")
            traceback.print_exc()
            return "抱歉，我暂时无法生成问题，请继续介绍你自己。"

    def extractAudio(self, webm_path: str) -> str or None:
        """[同步阻塞] 从webm文件中提取mp3音频。"""
        mp3_path = os.path.join(self.temp_audio_path, os.path.basename(webm_path).replace('.webm', '.mp3'))
        command = ['ffmpeg', '-i', webm_path, '-y', '-vn', '-acodec', 'libmp3lame', '-q:a', '2', mp3_path]
        
        try:
            print(f"正在使用 FFmpeg 从 {os.path.basename(webm_path)} 提取音频...")
            result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
            print(f"音频提取成功: {mp3_path}")
            return mp3_path
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg 音频提取失败! Stderr:\n{e.stderr}")
            return None
        except FileNotFoundError:
            print("错误: 'ffmpeg' 命令未找到。请确保FFmpeg已安装并已添加到系统PATH。")
            return None

    def backgroundFinalize(self):
        """将最终的、耗时的合并和分析任务提交到后台线程池，实现“发射后不管”。"""
        print("\n会话结束，提交最终的合并与分析任务到后台...")
        self.executor.submit(self.mergeAnalysis)

    def mergeAnalysis(self):
        """[同步阻塞] 包含了所有会话结束后的耗时操作。"""
        try:
            print("开始合并视频片段...")
            final_filepath = self.mergeVideo()
            
            if final_filepath:
                print(f"视频合并完成: {final_filepath}")
                self.videoAnalysis(final_filepath)
            else:
                print("没有可供分析的最终视频文件。")
        except Exception as e:
            print(f"合并分析过程中发生错误: {e}")
            traceback.print_exc()
        finally:
            self.cleanTempFiles()
            self.close()

    def mergeVideo(self) -> str or None:
        """[同步阻塞] 合并所有录制的视频片段。"""
        if not self.recorded_webm_paths:
            print("没有录制的视频片段可供合并。")
            return None

        final_video_dir = os.path.join(self.package_root, "DataFile", "Video", self.user_id)
        os.makedirs(final_video_dir, exist_ok=True)
        videoID = re.sub(r'[^0-9]', '', self.date)
        final_filepath = os.path.join(final_video_dir, f"{videoID}.mp4")

        # 删除可能存在的旧文件
        if os.path.exists(final_filepath):
            os.remove(final_filepath)

        # 转换webm为mp4
        repaired_mp4_paths = []
        for webm_path in self.recorded_webm_paths:
            mp4_path = webm_path.replace('.webm', '.repaired.mp4')
            command = [
                'ffmpeg', '-y', '-i', webm_path,
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
                '-c:a', 'aac', '-b:a', '128k',
                '-pix_fmt', 'yuv420p', mp4_path
            ]
            try:
                subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
                repaired_mp4_paths.append(mp4_path)
            except subprocess.CalledProcessError as e:
                print(f"FFmpeg修复文件 {os.path.basename(webm_path)} 失败! Stderr:\n{e.stderr}")

        if not repaired_mp4_paths:
            print("没有成功修复的视频文件可供合并。")
            return None

        # 创建合并列表文件
        concat_list_path = os.path.join(self.temp_video_path, "concat_list.txt")
        with open(concat_list_path, "w", encoding='utf-8') as f:
            for path in repaired_mp4_paths:
                safe_path = path.replace('\\', '/')
                f.write(f"file '{safe_path}'\n")

        # 执行合并
        merge_command = [
            'ffmpeg', '-f', 'concat', '-safe', '0',
            '-i', concat_list_path, '-c', 'copy', '-y', final_filepath
        ]
        try:
            print(f"开始合并 {len(repaired_mp4_paths)} 个视频片段...")
            subprocess.run(merge_command, check=True, capture_output=True, text=True, encoding='utf-8')
            print(f"所有片段已成功合并到: {final_filepath}")
            return final_filepath
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg 视频合并失败! Stderr:\n{e.stderr}")
            return None

    def videoAnalysis(self, final_video_path: str):
        """[同步阻塞] 调用 FullReport 进行最终的、全面的视频分析。"""
        from app.services.InterviewService.Video_analysis import FullReport

        videoID = os.path.splitext(os.path.basename(final_video_path))[0]
        try:
            print("开始视频分析...")
            full_report_pipeline = FullReport(
                video_path=final_video_path, job=self.job, history=self.history,
                user_id=self.user_id, date=self.date, videoID=videoID,
                process_tip_function=my_frontend_callback
            )
            final_report = full_report_pipeline.run_pipeline()
            
            if final_report:
                print("\n" + "=" * 25 + " 最终生成的完整JSON报告（预览） " + "=" * 25)
                print(json.dumps(final_report, ensure_ascii=False, indent=2))
            else:
                print("最终分析报告生成失败。")
        except Exception as e:
            print(f"在 video_analysis 阶段发生严重错误: {e}")
            traceback.print_exc()

    def cleanTempFiles(self):
        """[同步阻塞] 清理会话产生的所有临时文件。"""
        print("正在清理临时文件...")
        try:
            if os.path.exists(self.temp_video_path):
                shutil.rmtree(self.temp_video_path)
            if os.path.exists(self.temp_audio_path):
                shutil.rmtree(self.temp_audio_path)
            print("临时文件清理完成。")
        except OSError as e:
            print(f"清理临时文件目录时出错: {e}")

    def close(self):
        """安全地关闭线程池，等待后台任务完成。"""
        if self.executor:
            print("等待后台任务完成...")
            self.executor.shutdown(wait=True, cancel_futures=False)
            print("线程池已关闭。")

# """
# AudioProcessor.py (综合分析):
#     - 从视频中提取音频。
#     - 并行执行两大任务:
#         1. 调用 ASR 模块进行语音转文本，并接着使用 Sound 模块分析语速和语调。
#         2. 使用预训练模型分析言语流畅度（口吃）。
#     - 将所有结果汇总成一份综合报告。
# """

import os
import traceback
from moviepy.editor import VideoFileClip


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import logging

logging.getLogger("tensorflow").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)


class AudioProcessor:
    def __init__(self, video_path=None):
        if not video_path or not os.path.exists(video_path):
            raise FileNotFoundError(f"错误：视频文件 {video_path} 不存在或路径为空")
        self.video_path = video_path
        self.output_audio_path = f"temp_audio_for_{os.path.basename(video_path)}.wav"
        self.stutter_model = None

    def _initialize_stutter_model(self):
        from transformers import pipeline

        if self.stutter_model is None:
            print("\n正在初始化言语流畅度模型...")
            self.stutter_model = pipeline("audio-classification",
                                          model="HareemFatima/distilhubert-finetuned-stutterdetection")
            print("言语流暢度模型初始化完成。")

    def _extract_audio(self):
        if os.path.exists(self.output_audio_path):
            os.remove(self.output_audio_path)
        try:
            with VideoFileClip(self.video_path) as video_clip:
                if video_clip.audio is None:
                    print("警告: 视频中没有音轨。")
                    return False
                video_clip.audio.write_audiofile(self.output_audio_path, codec='pcm_s16le', logger=None)
            return True
        except Exception as e:
            print(f"\n错误：提取音频失败 - {e}")
            return False

    def _analyze_stutter(self, audio_path):
        try:
            self._initialize_stutter_model()
            print("开始分析言语流暢度...")
            result = self.stutter_model(audio_path, top_k=None)
            print("言语流暢度分析完成。")
            return result
        except Exception as e:
            print(f"严重错误: 言语流畅度分析模块崩溃 - {e}")
            traceback.print_exc()
            return []

    def _analyze_sound_and_asr(self, audio_path):
        transcribed_text = ""
        sound_analysis_result = {}

        try:
            from app.services.InterviewService.Asr import AudioTranscriber

            print("开始语音转文本(ASR)...")
            transcriber = AudioTranscriber()
            transcribed_text = transcriber.transcribe_mp3(audio_path)
            print(f"语音转文本完成。文本长度: {len(transcribed_text)}")
        except Exception as e:
            print("=" * 20 + " 严重错误：ASR模块崩溃！ " + "=" * 20)
            traceback.print_exc()
            transcribed_text = ""

        try:
            from app.services.InterviewService.sound import evaluate_from_input

            print("开始分析语速和语调...")
            sound_analysis_result = evaluate_from_input(audio_path, transcribed_text)
            print("语速语调分析完成。")
        except Exception as e:
            print("=" * 20 + " 严重错误：语速语调分析模块崩溃！ " + "=" * 20)
            traceback.print_exc()
            sound_analysis_result = {
                "error": True, "message": f"分析模块内部错误: {e}",
                "rhythm_score": 0, "rhythm_desc": "分析失败",
                "speed_score": 0.0, "speed_desc": "分析失败"
            }

        return {"transcription": transcribed_text, "sound_analysis": sound_analysis_result}

    def run_full_analysis(self):
        from concurrent.futures import ThreadPoolExecutor

        print("\n--- 开始综合音频分析 ---")
        full_report = {
            'stutter_analysis': [], 'transcription': "音频分析失败或无语音内容。",
            'sound_analysis': {'error': True, 'message': '分析未执行或失败'}
        }

        print("步骤 1: 正在从视频中提取音频...")
        if not self._extract_audio():
            print("错误：音频提取失败，返回默认报告。")
            return full_report
        print("音频提取完成。")

        print("\n步骤 2: 并行启动各项音频分析任务...")
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_stutter = executor.submit(self._analyze_stutter, self.output_audio_path)
            future_sound_asr = executor.submit(self._analyze_sound_and_asr, self.output_audio_path)

            print("等待分析任务完成...")
            try:
                stutter_report = future_stutter.result()
                full_report['stutter_analysis'] = stutter_report if isinstance(stutter_report, list) else []
            except Exception as e:
                print(f"错误: 获取言语流畅度分析结果时失败 - {e}")

            try:
                sound_asr_report = future_sound_asr.result()
                if isinstance(sound_asr_report, dict): full_report.update(sound_asr_report)
            except Exception as e:
                print(f"错误: 获取ASR与声音分析结果时失败 - {e}")

        if os.path.exists(self.output_audio_path):
            try:
                os.remove(self.output_audio_path)
            except Exception as e:
                print(f"警告：无法删除临时音频文件 {self.output_audio_path} - {e}")

        print("综合分析全部完成！")
        return full_report


if __name__ == "__main__":
    # ... 主执行代码保持不变 ...
    video_path = "/DataFile/Video/1/1.mp4"
    try:
        processor = AudioProcessor(video_path)
        final_report = processor.run_full_analysis()
        if final_report:
            print("\n" + "=" * 25 + " 综合音频分析报告 " + "=" * 25)
            print("\n--- 语速与语调评估 ---")
            sound_res = final_report.get('sound_analysis', {})
            if sound_res and not sound_res.get('error'):
                print(f"语调得分: {sound_res.get('rhythm_score', 'N/A')} —— {sound_res.get('rhythm_desc', '无评估')}")
                print(
                    f"语速得分: {float(sound_res.get('speed_score', 0)):.1f} —— {sound_res.get('speed_desc', '无评估')}")
            else:
                print(f"评估失败: {sound_res.get('message', '未知错误')}")
            print("\n--- 言语流畅度评估 ---")
            stutter_res = final_report.get('stutter_analysis', [])
            if stutter_res:
                for label_info in stutter_res: print(f"{label_info['label']} (置信度: {label_info['score']:.4f})")
            else:
                print("无评估结果。")
            print("\n--- 语音转录文本 ---")
            print(f"\"{final_report.get('transcription', '无转录文本。')}\"")
            print("\n" + "=" * 68)
    except FileNotFoundError as e:
        print(f"\n错误: {e}")
    except Exception as e:
        print(f"\n程序执行过程中发生严重错误: {e}")

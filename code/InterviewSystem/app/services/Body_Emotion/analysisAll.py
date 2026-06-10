"""
这个类综合调用了BodyLanguage等六种分析，产生的数据形式如：
{
  "comment": "面试分析综合报告",
  "summary": "（这里是根据所有分析结果生成的300-500字综合评语）",
  "radarCharData": {
    "comment": "雷达图数据，包含针对岗位的五个核心指标及其得分"
  },
  "pose": {
    "comment": "身体姿态分析结果，单位为百分比",
    "Head looks down": 95.45,
    "Hand on waist": 4.55,
    "Normal": 0.0,
    "Hands clasped": 0.0
  },
  "emotion": {
    "comment": "面部情绪分析结果，单位为百分比",
    "angry": 14.55,
    "disgust": 14.55,
    "fear": 7.27,
    "happy": 36.36,
    "sad": 5.45,
    "surprise": 0.0,
    "neutral": 21.82
  },
  "eye_contact": {
    "comment": "眼神接触分析结果，单位为百分比",
    "Contact": 0.0,
    "Not Contact": 100.0
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
      "blocks": 0.001
    },
    "rhythm_analysis": {
      "comment": "语调分析",
      "score": 25,
      "description": "语调较为生硬"
    },
    "speed_analysis": {
      "comment": "语速分析",
      "score": 0,
      "words_per_minute": 35,
      "description": "语速偏慢 35字/分钟"
    }
  },
  "study_route": {
    "comment": "个性化学习资源推荐",
    "recommendations": []
  },
  "overall_score": 0
}

"""
import cv2
import sys
import time
from concurrent.futures import ThreadPoolExecutor
import json
import re  # 导入正则表达式库，用于从描述中提取数字



class ComprehensiveAnalyzer:
    """
    一个高效的、并行的综合面试分析器。
    它只读取一次视频，并将帧分发给所有视觉分析模块，
    同时并行处理音频分析，最后汇总所有结果。
    """

    def __init__(self, video_path):
        from app.services.Body_Emotion.BodyLanguageRecognizer import BodyLanguageRecognizer
        from app.services.Body_Emotion.Eyecontact import EyeContact
        from app.services.Body_Emotion.EmotionDetector import EmotionDetector
        from app.services.Body_Emotion.HandMovementDetector import HandMovementDetector
        from app.services.Body_Emotion.object_tracker import ObjectTracker
        from app.services.Body_Emotion.Stutter_analysis import AudioProcessor

        if not cv2.os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件未找到: {video_path}")
        self.video_path = video_path

        # 1. 一次性获取视频元数据
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"无法打开视频文件: {video_path}")
        self.fps = cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) > 0 else 30
        self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        # 2. 一次性初始化所有分析器实例
        print("--- 正在初始化所有分析模块 ---")
        self.analyzers = {
            'body_language': BodyLanguageRecognizer(),
            'eye_contact': EyeContact(),
            'emotion': EmotionDetector(),
            'hand_movement': HandMovementDetector(total_video_frames=self.total_frames),
            'object_tracker': ObjectTracker(total_video_frames=self.total_frames),
            'audio': AudioProcessor(video_path=self.video_path)
        }
        print("--- 所有模块初始化完成 ---\n")

    def _run_video_analysis_loop(self, analyses_per_second, progress_callback):
        """[内部任务] 包含单一的视频读取循环，并将帧分发给所有视觉分析器。"""
        visual_analyzers = {k: v for k, v in self.analyzers.items() if k != 'audio'}

        for name in visual_analyzers:
            progress_callback(f"开始进行 {name.replace('_', ' ').title()} 分析...")

        cap = cv2.VideoCapture(self.video_path)
        analysis_interval = max(1, int(self.fps / analyses_per_second))
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break

            frame_count += 1

            if frame_count % analysis_interval == 0:
                for analyzer in visual_analyzers.values():
                    analyzer.process_frame(frame)

            if frame_count % int(self.fps) == 0:
                progress_percentage = (frame_count / self.total_frames) * 100
                progress_callback(f"视频分析进度: {progress_percentage:.0f}%")

        cap.release()
        for analyzer in visual_analyzers.values():
            if hasattr(analyzer, 'close'): analyzer.close()
        progress_callback("所有视觉分析完成。")

        results = {name: analyzer.get_summary() for name, analyzer in visual_analyzers.items()}
        return results

    def _run_audio_analysis_task(self, progress_callback):
        """[内部任务] 运行完整的音频分析流程。"""
        progress_callback("开始进行综合音频分析（此过程可能较长）...")
        result = self.analyzers['audio'].run_full_analysis()
        progress_callback("音频分析完成。")
        return result

    def run_full_analysis(self, analyses_per_second=2, progress_callback=None):
        """并行执行所有分析任务并返回一个包含所有结果的字典。"""
        if progress_callback is None:
            progress_callback = lambda msg: print(f"[进度更新] {msg}")

        final_report = {}
        with ThreadPoolExecutor(max_workers=2) as executor:
            progress_callback("并行启动视频和音频分析任务...")
            future_video = executor.submit(self._run_video_analysis_loop, analyses_per_second, progress_callback)
            future_audio = executor.submit(self._run_audio_analysis_task, progress_callback)

            progress_callback("等待所有分析任务完成...")
            video_results = future_video.result()
            audio_results = future_audio.result()

        progress_callback("正在聚合最终报告...")
        final_report.update(video_results)
        final_report['audio_analysis'] = audio_results
        progress_callback("综合分析全部完成！")

        return final_report


    @staticmethod
    def format_report_to_json_structure(report):
        """
        [最终防御版本]
        将任何形式的分析结果安全地格式化为您期望的最终JSON结构。
        此函数能处理None、空字典、缺少键等所有异常情况。
        """

        def format_floats(data_dict, default_decimals=2):
            """一个辅助函数，用于安全地格式化字典中的所有浮点数。"""
            if not isinstance(data_dict, dict):
                return {}  # 如果输入不是字典，返回空字典
            return {key: round(value, default_decimals) if isinstance(value, float) else value
                    for key, value in data_dict.items()}

        # --- 1. 安全地处理Pose, Emotion, Eye Contact, Hand Movement ---
        # 这些模块的 get_summary 已经很健壮了，但我们还是用 .get() 防护
        pose_data = format_floats(report.get('body_language', {}))
        emotion_data = format_floats(report.get('emotion', {}))
        eye_contact_data = format_floats(report.get('eye_contact', {}))
        hand_movement_data = format_floats(report.get('hand_movement', {}))

        # --- 2. 安全地处理 Object Tracker ---
        object_tracker_raw = report.get('object_tracker', {})
        if not isinstance(object_tracker_raw, dict): object_tracker_raw = {}  # 终极防护
        object_tracker_formatted = {
            "comment": "身体整体移动评估",
            "total_distance": round(object_tracker_raw.get('total_movement', 0.0), 2),
            "average_distance_per_frame": round(object_tracker_raw.get('average_movement', 0.0), 2),
            "assessment": object_tracker_raw.get('assessment', "无评估数据")
        }

        # --- 3. 安全地处理整个音频分析模块 (Stutter, Speed, Rhythm) ---
        audio_report = report.get('audio_analysis', {})
        if not isinstance(audio_report, dict): audio_report = {}  # 终极防护

        # a. Stutter Analysis
        stutter_analysis_formatted = {"comment": "言语流畅度分析，值为置信度"}
        stutter_data = audio_report.get('stutter_analysis')
        if isinstance(stutter_data, list):
            for item in stutter_data:
                if isinstance(item, dict) and 'label' in item and 'score' in item:
                    stutter_analysis_formatted[item['label']] = round(item.get('score', 0.0), 4)
        # 确保所有可能的标签都存在
        for label in ["nonstutter", "repetition", "prolongation", "blocks"]:
            stutter_analysis_formatted.setdefault(label, 0.0)

        # b. Sound Analysis (Speed and Rhythm)
        sound_analysis = audio_report.get('sound_analysis', {})
        if not isinstance(sound_analysis, dict): sound_analysis = {}  # 终极防护

        rhythm_analysis_formatted = {
            "comment": "语调分析",
            "score": round(sound_analysis.get('rhythm_score', 0), 2),
            "description": sound_analysis.get('rhythm_desc', "无评估数据")
        }

        speed_desc = sound_analysis.get('speed_desc', "0 字/分钟")
        wpm_match = re.search(r'(\d+)', str(speed_desc))  # 使用 str() 避免非字符串输入
        wpm = int(wpm_match.group(1)) if wpm_match else 0

        speed_analysis_formatted = {
            "comment": "语速分析",
            "score": round(sound_analysis.get('speed_score', 0), 2),
            "words_per_minute": wpm,
            "description": speed_desc
        }

        # --- 4. 构建最终的、结构保证完整的JSON ---
        final_json = {
            "comment": "面试分析综合报告",
            "summary": "（等待大模型生成...）",
            "radarCharData": {
                "comment": "雷达图数据，包含针对岗位的五个核心指标及其得分",
            },
            "pose": {
                "comment": "身体姿态分析结果，单位为百分比",
                **pose_data
            },
            "emotion": {
                "comment": "面部情绪分析结果，单位为百分比",
                **emotion_data
            },
            "eye_contact": {
                "comment": "眼神接触分析结果，单位为百分比",
                **eye_contact_data
            },
            "hand_movement": {
                "comment": "手部移动量化分析",
                **hand_movement_data
            },
            "object_tracker": object_tracker_formatted,
            "stutter_speed_rhythm": {
                "comment": "言语分析：包含流畅度、语速和语调",
                "stutter_analysis": stutter_analysis_formatted,
                "rhythm_analysis": rhythm_analysis_formatted,
                "speed_analysis": speed_analysis_formatted
            },
            "study_route": {
                "comment": "个性化学习资源推荐",
                "recommendations": []
            },
            "overall_score": 0.0
        }
        return final_json


# --- 使用示例 ---
def my_frontend_callback(message: str):
    """示例回调函数，用于向前端发送进度。"""
    print(f"[发送到前端]: {message}")


if __name__ == '__main__':
    video_path = "./Test_video.mp4"
    try:
        pipeline = ComprehensiveAnalyzer(video_path)
        final_report = pipeline.run_full_analysis(
            analyses_per_second=2,
            progress_callback=my_frontend_callback
        )
        final_json_data = ComprehensiveAnalyzer.format_report_to_json_structure(final_report)

        print("\n" + "=" * 25 + " 最终生成的JSON数据 " + "=" * 25)
        # indent=2 使打印出来的JSON格式更美观
        print(json.dumps(final_json_data, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"\n主流程发生严重错误: {e}")
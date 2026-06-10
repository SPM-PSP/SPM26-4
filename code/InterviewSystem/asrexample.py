#!/usr/bin/env python3
"""
阿里云百炼 qwen3-asr-flash 语音转写测试脚本
功能：从视频文件中提取音频并调用ASR服务进行转写

(AIinterview_python3.9) E:\CODE_File\SPM26-4\code\InterviewSystem>python asrexample.py
============================================================
    阿里云百炼 qwen3-asr-flash 语音转写测试
============================================================
✅ ASR转写器初始化完成
   - API地址: https://dashscope.aliyuncs.com/api/v1

🔊 正在从视频中提取音频...
   输入: E:\CODE_File\SPM26-4\code\InterviewSystem\DataFile\Video\testuser001\20260531155958.mp4 
   输出: E:\CODE_File\SPM26-4\code\InterviewSystem\DataFile\Video\testuser001\20260531155958_audio.mp3
✅ 音频提取成功

🎙️ 正在调用 qwen3-asr-flash 模型进行转写...
   音频文件: E:\CODE_File\SPM26-4\code\InterviewSystem\DataFile\Video\testuser001\20260531155958_audio.mp3
   文件大小: 146.25 KB

📝 转写结果:
   [{'text': '你好，我是四川大学软件工程专业的，一名大三学生。嗯。'}]

❌ 测试失败: write() argument must be str, not list
Traceback (most recent call last):
  File "E:\CODE_File\SPM26-4\code\InterviewSystem\asrexample.py", line 186, in main
    f.write(result)
TypeError: write() argument must be str, not list

(AIinterview_python3.9) E:\CODE_File\SPM26-4\code\InterviewSystem>
(AIinterview_python3.9) E:\CODE_File\SPM26-4\code\InterviewSystem>python asrexample.py
============================================================
    阿里云百炼 qwen3-asr-flash 语音转写测试
============================================================
✅ ASR转写器初始化完成
   - API地址: https://dashscope.aliyuncs.com/api/v1

🔊 正在从视频中提取音频...
   输入: E:\CODE_File\SPM26-4\code\InterviewSystem\DataFile\Video\testuser001\20260531155958.mp4 
   输出: E:\CODE_File\SPM26-4\code\InterviewSystem\DataFile\Video\testuser001\20260531155958_audio.mp3
✅ 音频提取成功

🎙️ 正在调用 qwen3-asr-flash 模型进行转写...
   音频文件: E:\CODE_File\SPM26-4\code\InterviewSystem\DataFile\Video\testuser001\20260531155958_audio.mp3
   文件大小: 146.25 KB

📝 转写结果:
   [{'text': '你好，我是四川大学软件工程专业的，一名大三学生。嗯。'}]

❌ 测试失败: write() argument must be str, not list
Traceback (most recent call last):
  File "E:\CODE_File\SPM26-4\code\InterviewSystem\asrexample.py", line 186, in main
    f.write(result)
TypeError: write() argument must be str, not list

(AIinterview_python3.9) E:\CODE_File\SPM26-4\code\InterviewSystem>使用base64编码直接发送音频数据，无需OSS上传
"""
import os
import sys
import subprocess
import json
import traceback
import base64

# 请确保已安装 dashscope
# pip install dashscope

try:
    import dashscope
except ImportError:
    print("错误：未安装 dashscope 库")
    print("请运行：pip install dashscope")
    sys.exit(1)


class QwenASRTranscriber:
    """基于阿里云百炼 qwen3-asr-flash 的语音转写器"""
    
    def __init__(self, api_key=None):
        """
        初始化ASR转写器
        
        Args:
            api_key: 阿里云百炼API Key，若未提供则从环境变量获取
        """
        # 设置API Key
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("请设置 DASHSCOPE_API_KEY 环境变量或传入 api_key 参数")
        
        # 设置API地址（北京地域）
        dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"
        
        print(f"✅ ASR转写器初始化完成")
        print(f"   - API地址: {dashscope.base_http_api_url}")
    
    def extract_audio_from_video(self, video_path, output_audio_path=None):
        """
        从视频文件中提取音频
        
        Args:
            video_path: 视频文件路径
            output_audio_path: 输出音频文件路径，默认为同目录下的mp3文件
            
        Returns:
            str: 音频文件路径
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在: {video_path}")
        
        # 默认输出路径
        if output_audio_path is None:
            base_name = os.path.splitext(video_path)[0]
            output_audio_path = f"{base_name}_audio.mp3"
        
        # 使用FFmpeg提取音频
        command = [
            'ffmpeg',
            '-i', video_path,           # 输入视频
            '-y',                       # 覆盖输出文件
            '-vn',                      # 禁用视频流
            '-acodec', 'libmp3lame',    # MP3编码
            '-q:a', '2',                # 音质
            '-ac', '1',                 # 单声道
            '-ar', '16000',             # 采样率16kHz
            output_audio_path
        ]
        
        print(f"\n🔊 正在从视频中提取音频...")
        print(f"   输入: {video_path}")
        print(f"   输出: {output_audio_path}")
        
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            print(f"✅ 音频提取成功")
            return output_audio_path
        except subprocess.CalledProcessError as e:
            print(f"❌ 音频提取失败: {e.stderr}")
            raise
        except FileNotFoundError:
            print("❌ FFmpeg未安装或未添加到系统PATH")
            raise
    
    def transcribe_audio_file(self, audio_path):
        """
        直接转写本地音频文件（使用base64编码发送）
        
        Args:
            audio_path: 本地音频文件路径
            
        Returns:
            str: 转写结果文本
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")
        
        # 获取文件大小
        file_size = os.path.getsize(audio_path)
        print(f"\n🎙️ 正在调用 qwen3-asr-flash 模型进行转写...")
        print(f"   音频文件: {audio_path}")
        print(f"   文件大小: {file_size / 1024:.2f} KB")
        
        # 读取音频文件并进行base64编码
        with open(audio_path, "rb") as f:
            audio_data = f.read()
        
        # 构建消息
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "audio": f"data:audio/mp3;base64,{base64.b64encode(audio_data).decode('utf-8')}"
                    }
                ]
            }
        ]
        
        try:
            response = dashscope.MultiModalConversation.call(
                api_key=self.api_key,
                model="qwen3-asr-flash",
                messages=messages,
                result_format="message",
                asr_options={
                    "language": "zh",     # 指定中文语种，提升识别准确率
                    "enable_itn": False   # 是否启用ITN（逆文本规范化）
                }
            )
            
            # 解析响应
            if response.status_code == 200:
                content = response.output.choices[0].message.content
                
                # 处理返回结果格式
                if isinstance(content, list) and len(content) > 0:
                    # 格式: [{'text': '...'}]
                    if isinstance(content[0], dict) and 'text' in content[0]:
                        result = content[0]['text']
                    else:
                        result = str(content)
                else:
                    result = str(content)
                
                print(f"\n📝 转写结果:")
                print(f"   {result}")
                return result
            else:
                print(f"❌ 转写失败: {response.message}")
                return None
                
        except Exception as e:
            print(f"❌ 调用ASR服务时发生错误: {e}")
            traceback.print_exc()
            return None


def main():
    """主函数"""
    print("="*60)
    print("    阿里云百炼 qwen3-asr-flash 语音转写测试")
    print("="*60)
    
    # 配置参数
    API_KEY = "sk-44be5cbebff74727ae8460ebc4079353"  # 百炼API Key（sk-开头）
    VIDEO_PATH = r"E:\CODE_File\SPM26-4\code\InterviewSystem\DataFile\Video\testuser001\20260531155958.mp4"
    
    try:
        # 创建转写器
        transcriber = QwenASRTranscriber(api_key=API_KEY)
        
        # 1. 从视频提取音频
        audio_path = transcriber.extract_audio_from_video(VIDEO_PATH)
        
        # 2. 直接转写音频（使用base64编码）
        result = transcriber.transcribe_audio_file(audio_path)
        
        # 3. 保存结果
        if result:
            output_file = os.path.splitext(VIDEO_PATH)[0] + "_transcription.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"\n💾 转写结果已保存到: {output_file}")
        
        print("\n🎉 测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

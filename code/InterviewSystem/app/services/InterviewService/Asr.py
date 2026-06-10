"""
ASR模块 - 基于阿里云百炼 qwen3-asr-flash 模型
负责将语音文件转换为文本，支持本地文件直接转写
"""
import os
import sys
import base64
import traceback

try:
    import dashscope
except ImportError:
    print("错误：未安装 dashscope 库")
    print("请运行：pip install dashscope")


class AudioTranscriber:
    """基于阿里云百炼 qwen3-asr-flash 的语音转写器"""
    
    # 阿里云百炼API配置
    API_KEY = "sk-44be5cbebff74727ae8460ebc4079353"
    API_BASE_URL = "https://dashscope.aliyuncs.com/api/v1"
    
    def __init__(self):
        """初始化ASR转写器"""
        self.transcription = ""
        self.error_message = None
        
        # 设置API地址（北京地域）
        dashscope.base_http_api_url = self.API_BASE_URL
        
        print(f"✅ ASR转写器初始化完成 (qwen3-asr-flash)")
        print(f"   - API地址: {self.API_BASE_URL}")

    def transcribe_mp3(self, file_path):
        """
        将音频文件转录为文本（使用阿里云百炼 qwen3-asr-flash）
        支持 MP3 和 WAV 格式
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            str: 转录的文本结果，失败返回空字符串
        """
        # 重置状态
        self.transcription = ""
        self.error_message = None
        
        if not os.path.exists(file_path):
            self.error_message = f"文件不存在: {file_path}"
            print(f"❌ {self.error_message}")
            return ""
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        print(f"🎙️ 正在调用 qwen3-asr-flash 模型进行转写...")
        print(f"   文件: {file_path}")
        print(f"   大小: {file_size / 1024:.2f} KB")
        
        try:
            # 读取音频文件并进行base64编码
            with open(file_path, "rb") as f:
                audio_data = f.read()
            
            # 检测文件格式
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.wav':
                mime_type = 'audio/wav'
            else:
                mime_type = 'audio/mp3'
            
            # 构建消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "audio": f"data:{mime_type};base64,{base64.b64encode(audio_data).decode('utf-8')}"
                        }
                    ]
                }
            ]
            
            # 调用ASR服务
            response = dashscope.MultiModalConversation.call(
                api_key=self.API_KEY,
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
                        self.transcription = content[0]['text']
                    else:
                        self.transcription = str(content)
                else:
                    self.transcription = str(content)
                
                print(f"✅ 转写成功，结果长度: {len(self.transcription)}字符")
                print(f"   内容: {self.transcription[:50]}..." if len(self.transcription) > 50 else f"   内容: {self.transcription}")
                
            else:
                self.error_message = f"转写失败: {response.message}"
                print(f"❌ {self.error_message}")
                
        except Exception as e:
            self.error_message = f"转写过程中发生错误: {str(e)}"
            print(f"❌ {self.error_message}")
            traceback.print_exc()
            
        return self.transcription

    def getFinalText(self):
        """获取最终转录文本"""
        return self.transcription

    def close(self):
        """关闭资源（兼容旧接口）"""
        print("ASR连接已关闭")


# 使用示例
if __name__ == "__main__":
    transcriber = AudioTranscriber()
    try:
        mp3_file = "test.mp3"
        result = transcriber.transcribe_mp3(mp3_file)
        print("\n" + "=" * 60)
        print("转录结果:")
        print(result)
        print("=" * 60)
    except Exception as e:
        print(f"转录失败: {e}")
    finally:
        transcriber.close()

"""
    textAnalysis是文本分析模块，对用户的回答进行打分、结合面试岗位以及预先设定的指标对用户的问题回答、个人简历信息进行专业能力评估
"""

import json
import re
import os
import PyPDF2
from langchain.tools import tool
from typing import Dict, Any, Optional, Union

# 阿里云百炼配置
API_KEY = "sk-44be5cbebff74727ae8460ebc4079353"
API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_MODEL = "qwen3.5-plus"


def create_llm_client():
    """创建LLM客户端"""
    from openai import OpenAI
    return OpenAI(
        api_key=API_KEY,
        base_url=API_BASE
    )


def call_llm(messages, temperature=0.7, max_tokens=2048):
    """调用LLM并返回响应"""
    client = create_llm_client()
    
    # 转换历史记录中的角色
    converted_messages = []
    for msg in messages:
        role = msg.get('role', '')
        if role == 'ai':
            converted_messages.append({"role": "assistant", "content": msg.get('content', '')})
        elif role in ['system', 'assistant', 'user', 'tool', 'function']:
            converted_messages.append({"role": role, "content": msg.get('content', '')})
        else:
            converted_messages.append({"role": "user", "content": msg.get('content', '')})
    
    completion = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=converted_messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return completion.choices[0].message.content


class AliyunFileProcessor:
    """阿里云百炼文档评估处理器，支持处理文件路径或直接传入字符串。"""
    
    def __init__(
        self,
        temperature: float = 0.1
    ):
        self.temperature = temperature
        
    def _get_content(self, input_data: Union[str, os.PathLike]) -> str:
        """根据输入类型获取文本内容：如果是文件路径则读取，否则直接返回字符串。"""
        if isinstance(input_data, (str, os.PathLike)) and os.path.exists(input_data):
            file_path = str(input_data)
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif ext == '.pdf':
                with open(file_path, 'rb') as f:
                    return '\n'.join(
                        page.extract_text() or '' 
                        for page in PyPDF2.PdfReader(f).pages
                    )
            else:
                raise ValueError("仅支持TXT/PDF文件路径")
        elif isinstance(input_data, str):
            return input_data
        else:
            raise TypeError("输入必须是文件路径（TXT/PDF）或字符串")
    
    def comprehensive_evaluate(self, input_data: Union[str, os.PathLike]) -> Dict[str, Any]:
        """
        综合评估（纯评语版）
        :param input_data: 要评估的文本内容字符串或文件路径（TXT/PDF）
        """
        try:
            content = self._get_content(input_data)
            query = (
                "根据文本内容，从大数据、人工智能、物联网三个领域中选择一个领域，"
                "如果是物联网则从用户需求洞察力，技术可行性分析，商业化能力，跨团队协作能力，市场敏感度，应变能力这些方面去用简要中文进行评估并且引用支撑材料，如果不涉及则不对对应方面做阐述"
                "如果是大数据领域则从数据架构设计能力，编程与算法能力，问题排查效率，技术文档能力，新技术学习能力，团队协作意识这些方面去用简要中文进行评估并且引用支撑材料，如果不涉及则不对对应方面做阐述"
                "如果是人工智能领域则从模型测试，数据质量分析，自动化测试开发、伦理安全、跨领域知识储备、应急响应能力这些方面去用中文进行评估并且引用支撑材料，如果不涉及则不对对应方面做阐述" 
                "结果以json的格式返回" 
                "例：{"
                "用户洞察力：较强的用户洞察力\n"
                "技术可行性分析：......\n}"
                f"\n文本内容：\n{content}"
            )
            
            messages = [{"role": "user", "content": query}]
            response = call_llm(messages, temperature=self.temperature, max_tokens=4096)
            
            if response:
                cleaned = response.strip().replace("。", "")
                return {"success": True, "data": cleaned}
            return {"success": False, "error": "未收到响应"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def quantitative_score(self, input_data: Union[str, os.PathLike]) -> Dict[str, Any]:
        """
        生成量化评分（仅总分）
        :param input_data: 要评分的文本内容字符串或文件路径（TXT/PDF）
        """
        try:
            content = self._get_content(input_data)
            query = (
                "你是一个专业的面试官评分助手。请根据以下文本内容进行评分：\n\n"
                "评分规则：\n"
                "- 首先判断文本涉及的领域：大数据、人工智能或物联网\n"
                "- 物联网领域评分维度：用户需求洞察力、技术可行性分析、商业化能力、跨团队协作能力、市场敏感度、应变能力\n"
                "- 大数据领域评分维度：数据架构设计能力、编程与算法能力、问题排查效率、技术文档能力、新技术学习能力、团队协作意识\n"
                "- 人工智能领域评分维度：模型测试、数据质量分析、自动化测试开发、伦理安全、跨领域知识储备、应急响应能力\n"
                "- 请综合各维度给出百分制总分（0-100的整数）\n\n"
                "输出格式要求：\n"
                "- 必须以 ```json 开头，以 ``` 结尾\n"
                "- 内容必须是标准JSON格式\n"
                "- 只包含一个键'score'，值为整数\n"
                "- 示例输出：\n"
                "```json\n"
                "{\"score\":90}\n"
                "```\n\n"
                f"待评分文本：\n{content}"
            )
            
            messages = [{"role": "user", "content": query}]
            response = call_llm(messages, temperature=self.temperature, max_tokens=1024)
        
            if response:
                response_data_str = response
                
                # 首先尝试从 Markdown 代码块中提取 JSON 字符串
                json_match = re.search(r'```json\s*(\{.*\})\s*```', response_data_str, re.DOTALL)
                
                extracted_json_str = None
                if json_match:
                    extracted_json_str = json_match.group(1)
                else:
                    print(f"警告: 未在API响应中找到 ```json``` 代码块，尝试直接解析原始字符串。")
                    extracted_json_str = response_data_str

                # 确保提取到的数据是字符串类型且不为空
                if not isinstance(extracted_json_str, str) or not extracted_json_str.strip():
                    return {"success": False, "error": f"API返回的数据为空或不是有效的字符串格式。"}

                # --- 尝试 1: 解析为 JSON ---
                try:
                    parsed_data = json.loads(extracted_json_str)
                    score = parsed_data.get("score")
                    if score is not None:
                        return {
                            "success": True,
                            "data": int(score)
                        }
                    else:
                        return {"success": False, "error": f"从API响应的JSON中未找到 'score' 键。"}

                except json.JSONDecodeError as e:
                    # --- 尝试 2: 如果 JSON 解析失败，则尝试直接从字符串中提取数字 ---
                    try:
                        # 尝试匹配 "score:数字" 格式
                        match = re.search(r'score:(\d+)', response_data_str)
                        if match:
                            score_str = match.group(1)
                        else:
                            # 如果不是 "score:数字" 格式，尝试直接匹配字符串中的所有数字
                            match = re.search(r'(\d+)', response_data_str)
                            if match:
                                score_str = match.group(1)
                            else:
                                return {
                                    "success": False,
                                    "error": f"无法从API响应中找到有效的评分数字。"
                                }
                        
                        return {
                            "success": True,
                            "data": int(score_str)
                        }

                    except ValueError:
                        return {
                            "success": False,
                            "error": f"从API响应中提取的评分无法转换为整数。"
                        }
                    except Exception as e:
                        return {"success": False, "error": f"直接解析API响应失败: {str(e)}"}

            return {"success": False, "error": "未收到响应"}
        except Exception as e:
            return {"success": False, "error": str(e)}


# 工具函数组
@tool("document_evaluator", return_direct=True)
def evaluate_tool(input_data: Union[str, os.PathLike]) -> dict:
    """文档综合评估工具，输入为待评估的文本内容字符串或文件路径（TXT/PDF）。"""
    return AliyunFileProcessor().comprehensive_evaluate(input_data)

@tool("document_scorer", return_direct=True)
def score_tool(input_data: Union[str, os.PathLike]) -> dict:
    """文档量化评分工具，输入为待评分的文本内容字符串或文件路径（TXT/PDF）。"""
    return AliyunFileProcessor().quantitative_score(input_data)


# 兼容性别名 - 保持原有类名不变
SparkFileProcessor = AliyunFileProcessor


if __name__ == "__main__":
    # 使用示例
    processor = AliyunFileProcessor()
    
    # 示例文本内容
    sample_text_content = """
    然后在我研究生这两年期间主要参与并负责了个项目。
    第一个项目是工程机械智慧施工。在第一个项目中，
    我主要负责的工作可以分为三个部分。
    因为我们项目主要是为了实现一个推土机在整个矿区场景中自主作业的功能。
    因此，我首先是搭建了一个通讯系统，因为涉及到一些任务的下发和应答，
    包括传感器状态转发和传感及数据。
    """
    
    print("\n--- 评估直接字符串 ---")
    scoring_string = processor.quantitative_score(sample_text_content)
    print("字符串量化评分结果：", scoring_string)

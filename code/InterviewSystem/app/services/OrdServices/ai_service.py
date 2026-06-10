"""
AI助手服务模块 - 使用阿里云百炼（DashScope）大语言模型
"""
import json
from typing import Optional, List, Dict
from openai import OpenAI

# ==================== 配置信息（阿里云百炼 DashScope）====================
LLM_API_KEY = "sk-44be5cbebff74727ae8460ebc4079353"
LLM_API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_MODEL = "qwen3.5-plus"


def create_llm_client(api_key: str = LLM_API_KEY, base_url: str = LLM_API_BASE) -> OpenAI:
    """
    创建 LLM 客户端（兼容 openai >= 1.0.0 版本）
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


def get_ai_answer_from_spark(query: str, history: Optional[List[Dict]] = None) -> str:
    """
    调用AI助手获取回答（兼容原函数签名，实际使用阿里云百炼模型）
    
    Args:
        query: 用户查询
        history: 对话历史列表，格式: [{"role": "user/assistant", "content": "..."}]
    
    Returns:
        AI 的响应文本
    """
    # 构建消息列表
    messages = []
    
    # 添加系统提示
    system_prompt = "你是一名专业的AI助手，擅长回答各种问题。请用中文简洁明了地回答用户的问题。"
    messages.append({"role": "system", "content": system_prompt})
    
    # 添加历史对话
    if history:
        for msg in history:
            # 兼容旧格式：将 'ai' 角色转换为 'assistant'
            role = msg["role"]
            if role == "ai":
                role = "assistant"
            messages.append({"role": role, "content": msg["content"]})
    
    # 添加当前用户查询
    messages.append({"role": "user", "content": query})
    
    # 调用大模型
    try:
        response = call_llm(messages, temperature=0.5, max_tokens=4096)
        return response
    except Exception as e:
        print(f"LLM调用错误: {e}")
        return f"抱歉，我暂时无法回答您的问题。错误信息: {str(e)}"

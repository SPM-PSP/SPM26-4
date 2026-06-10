#!/usr/bin/env python3
"""
最简单的AI对话模型调用脚本

本脚本展示了如何使用 OpenAI SDK 调用阿里云百炼（DashScope）大语言模型进行对话。

运行前准备：
1. 确保安装了 openai >= 1.0.0 版本
2. 配置已硬编码在脚本中

使用方法：
python simple_llm_call.py

项目背景：
本项目使用阿里云百炼平台的通义千问模型（qwen3.5-plus），
通过 OpenAI 兼容模式 API 进行调用。
"""

import os
from openai import OpenAI


# ==================== 配置信息（从 infra/.env 硬编码）====================
LLM_API_KEY = "sk-44be5cbebff74727ae8460ebc4079353"
LLM_API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_MODEL = "qwen3.5-plus"


def create_llm_client(api_key: str, base_url: str):
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


def simple_chat(client: OpenAI, user_message: str, model: str = DEFAULT_MODEL) -> str:
    """
    最简单的单轮对话调用
    
    Args:
        client: OpenAI 客户端实例
        user_message: 用户输入消息
        model: 模型名称，默认为 qwen3.5-plus
    
    Returns:
        AI 的响应文本
    """
    # 构建对话消息格式
    messages = [
        {
            "role": "user",
            "content": user_message
        }
    ]
    
    # 调用 API（openai >= 1.0.0 版本）
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,      # 温度参数，控制回答的随机性
        max_tokens=2048       # 最大生成 token 数
    )
    
    # 提取响应内容
    return completion.choices[0].message.content


def multi_turn_chat(client: OpenAI, messages: list, model: str = DEFAULT_MODEL) -> str:
    """
    多轮对话调用（保持对话历史）
    
    Args:
        client: OpenAI 客户端实例
        messages: 对话历史列表，格式: [{"role": "user/assistant", "content": "..."}]
        model: 模型名称
    
    Returns:
        AI 的响应文本
    """
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=2048
    )
    
    return completion.choices[0].message.content


if __name__ == "__main__":
    # 1. 创建 LLM 客户端
    print("正在创建 LLM 客户端...")
    client = create_llm_client(LLM_API_KEY, LLM_API_BASE)
    print("客户端创建成功！")
    print()
    
    # 2. 示例1：简单单轮对话
    print("=" * 50)
    print("示例1：简单单轮对话")
    print("=" * 50)
    user_input = "你好，请问你是谁？"
    print(f"用户: {user_input}")
    response = simple_chat(client, user_input)
    print(f"AI: {response}")
    print()
    
    # 3. 示例2：多轮对话
    print("=" * 50)
    print("示例2：多轮对话")
    print("=" * 50)
    messages = [
        {"role": "user", "content": "解释一下什么是机器学习"},
        {"role": "assistant", "content": "机器学习是一种人工智能技术，..."},  # 模拟历史回复
        {"role": "user", "content": "它和深度学习有什么区别？"}
    ]
    print(f"用户: {messages[-1]['content']}")
    response = multi_turn_chat(client, messages)
    print(f"AI: {response}")
    print()
    
    print("测试完成！")

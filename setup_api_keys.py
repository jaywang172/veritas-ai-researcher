#!/usr/bin/env python3
"""API Keys 設置輔助腳本"""

import os
import sys
from pathlib import Path

def setup_api_keys():
    """引導用戶設置 API Keys"""
    print("🔑 Veritas v3.0 API Keys 設置")
    print("=" * 50)
    print()
    
    # 讀取當前 .env 檔案
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env 檔案不存在，請先運行：python create_env.py")
        return
    
    print("請設置您的 API Keys：")
    print()
    
    # 獲取 OpenAI API Key
    print("1. OpenAI API Key (必須)")
    print("   獲取方式：https://platform.openai.com/account/api-keys")
    openai_key = input("   請輸入您的 OpenAI API Key (sk-...): ").strip()
    
    if not openai_key or openai_key == 'your_openai_api_key_here':
        print("❌ 必須提供有效的 OpenAI API Key")
        return
    
    print()
    
    # 獲取 Tavily API Key (可選)
    print("2. Tavily Search API Key (可選，用於網路搜尋)")
    print("   獲取方式：https://tavily.com/")
    tavily_key = input("   請輸入您的 Tavily API Key (或按 Enter 跳過): ").strip()
    
    if not tavily_key:
        tavily_key = "your_tavily_api_key_here"
    
    # 更新 .env 檔案
    env_content = f"""# Veritas v3.0 Environment Configuration
# API Keys 已設置

# OpenAI API Key (必須)
OPENAI_API_KEY={openai_key}

# Tavily Search API Key (可選，用於網路搜尋)
TAVILY_API_KEY={tavily_key}

# Google API Key (可選，如果使用 Gemini 模型)
GOOGLE_API_KEY=your_google_api_key_here

# LangChain 追蹤 (可選，用於除錯)
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=your_langchain_api_key_here
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print()
    print("✅ API Keys 已設置完成！")
    print("現在可以運行：python main.py")

if __name__ == "__main__":
    setup_api_keys()

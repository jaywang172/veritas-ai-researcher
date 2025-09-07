#!/usr/bin/env python3
"""
Veritas Prototype - Main Entry Point
A multi-agent system for automated literature research and synthesis.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """
    Main function to run the Veritas prototype.
    """
    print("🚀 正在啟動Veritas代理人團隊...")

    # Get research topic from user
    research_topic = input("請輸入研究主題：")

    if not research_topic.strip():
        print("❌ 研究主題不能為空")
        return

    print(f"📚 正在研究主題：{research_topic}")
    print("🔍 代理人團隊開始工作...")

    # TODO: Implement Crew execution here (Sprint 4)

    print("✅ 報告生成完畢！")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Veritas Prototype - Main Entry Point
A multi-agent system for automated literature research and synthesis.
"""

import os
import sys
from dotenv import load_dotenv
from crewai import Crew
from agents import literature_scout
from tasks import create_research_task

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

    try:
        # Sprint 1: Single agent with search tool
        print("\n=== Sprint 1: 文獻搜集階段 ===")

        # Create the research task
        research_task = create_research_task(research_topic)

        # Create a Crew with just the LiteratureScoutAgent
        crew = Crew(
            agents=[literature_scout],
            tasks=[research_task],
            verbose=True
        )

        # Execute the crew
        print("執行Crew...")
        result = crew.kickoff()

        # Display results
        print("\n=== 搜集結果 ===")
        print(result)

        print("\n✅ Sprint 1 完成！文獻搜集代理人成功運行")

    except Exception as e:
        print(f"❌ 執行過程中發生錯誤: {str(e)}")
        print("請檢查API金鑰是否正確設置")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Veritas Prototype - Main Entry Point
A multi-agent system for automated literature research and synthesis.
"""

import os
import sys
from dotenv import load_dotenv
from crewai import Crew, Process
from agents import LiteratureScoutAgent, SynthesizerAgent
from tasks import create_research_task, create_summarize_task

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
        # Sprint 2: Two agents collaboration with data passing
        print("\n=== Sprint 2: 雙代理人協作階段 ===")

        # Initialize agents
        scout_agent_creator = LiteratureScoutAgent()
        synthesizer_agent_creator = SynthesizerAgent()

        # Create agent instances
        researcher = scout_agent_creator.create()
        summarizer = synthesizer_agent_creator.create()

        # Create task instances
        research_task_instance = create_research_task(research_topic)

        # Create summarize task with research task as context
        summarize_task_instance = create_summarize_task()

        # Set up context relationship - research task output feeds into summarize task
        summarize_task_instance.context = [research_task_instance]

        # Create Crew with both agents and tasks
        veritas_crew = Crew(
            agents=[researcher, summarizer],
            tasks=[research_task_instance, summarize_task_instance],
            verbose=2,
            process=Process.sequential
        )

        # Execute the crew
        print("🚀 啟動 Veritas 代理人團隊...")
        result = veritas_crew.kickoff()

        # Display results
        print("\n\n✅ 任務完成！以下是生成的綜述報告：")
        print("----------------------------------------")
        print(result)

        print("\n✅ Sprint 2 完成！雙代理人協作成功")

    except Exception as e:
        print(f"❌ 執行過程中發生錯誤: {str(e)}")
        print("請檢查API金鑰是否正確設置")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Veritas Prototype - Main Entry Point
A multi-agent system for automated literature research and synthesis.
"""

import os
import sys
import json
import time
from dotenv import load_dotenv
from crewai import Crew, Process
from agents import LiteratureScoutAgent, SynthesizerAgent
from tasks import create_research_task, create_summarize_task

# Load environment variables
load_dotenv()

# ----------------- 新增：一個簡單的動畫函式 -----------------
def thinking_animation():
    """顯示一個簡單的思考動畫"""
    chars = "|/-\\"
    for _ in range(20):
        for char in chars:
            print(f"\r🤔 代理人團隊正在思考... {char}", end="", flush=True)
            time.sleep(0.1)
    print("\r🤔 代理人團隊正在思考... ✓")


# ----------------- 新增：美化的標題函式 -----------------
def print_header():
    """打印應用程式的標題"""
    print("="*60)
    print("🔬 Veritas - 透明化AI研究協調平台 (原型 v1.0)".center(60))
    print("="*60)
    print("\n")


def main():
    """
    Main function to run the Veritas prototype.
    """
    # --- 修改點 1: 在程式開始時打印標題 ---
    print_header()

    # Get research topic from user
    topic = input("请输入您想研究的主題 (例如: the impact of remote work on employee productivity): \n> ")
    if not topic:
        print("錯誤：研究主題不能為空。")
        return

    research_topic = topic

    print(f"📚 正在研究主題：{research_topic}")
    print("🔍 代理人團隊開始工作...")

    try:
        # Sprint 3: Traceability layer - Structured JSON output with source citations
        print("\n=== Sprint 3: 可追溯性實現階段 ===")

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
            verbose=False, # 將這裡改為 False，我們用自己的動畫來提示進度
            process=Process.sequential
        )

        # Execute the crew
        print("\n🚀 啟動 Veritas 代理人團隊...")

        # --- 修改點 3: 執行 kickoff 並顯示動畫 ---
        # 由於 kickoff 是阻塞的，我們無法同時顯示動畫。
        # 這裡我們只打印一個啟動訊息。在更進階的版本中，會使用多線程。
        print("   - 正在進行文獻搜尋與分析，請稍候...")

        result_json_string = veritas_crew.kickoff()

        # --- 修改點 4: 更新結果呈現部分 ---
        print("\n\n" + "="*60)
        print("✅ 任務完成！".center(60))
        print("="*60 + "\n")

        try:
            report_data = json.loads(result_json_string)

            if not isinstance(report_data, list):
                print("❌ 錯誤：輸出的JSON不是一個列表。")
                print("   原始輸出：", result_json_string)
                return

            print(f"主題： {research_topic}\n")
            print("--- 綜述報告 (可追溯) ---\n")

            if not report_data:
                print("ℹ️ 未能從找到的資料中提取出有效的論點。")
            else:
                for i, item in enumerate(report_data, 1):
                    sentence = item.get('sentence', 'N/A')
                    source = item.get('source', 'N/A')
                    print(f"{i}. {sentence}")
                    print(f"   └─ 來源: {source}\n")

            print("\n--- 報告結束 ---\n")

        except json.JSONDecodeError:
            print("❌ 錯誤：無法解析LLM返回的JSON。")
            print("   LLM原始輸出：\n", result_json_string)
        except Exception as e:
            print(f"❌ 處理結果時發生未知錯誤: {e}")
            print("   原始輸出：", result_json_string)

    except Exception as e:
        print(f"\n❌ 程式發生嚴重錯誤: {e}")
        print("   💡 請檢查API金鑰是否正確設置")

if __name__ == "__main__":
    main()

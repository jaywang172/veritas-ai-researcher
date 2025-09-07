#!/usr/bin/env python3
"""
Veritas Prototype - Main Entry Point
A multi-agent system for automated literature research and synthesis.
"""

import os
import sys
import json
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
            verbose=2,
            process=Process.sequential
        )

        # Execute the crew
        print("🚀 啟動 Veritas 代理人團隊...")
        print("   - Sprint 3: 專注於實現可追溯性...")
        result_json_string = veritas_crew.kickoff()

        print("\n\n✅ 結構化報告生成完畢！正在解析與呈現...")
        print("-------------------------------------------------")

        # --- 新增的解析與呈現邏輯 ---
        try:
            # 解析Crew返回的JSON字串
            report_data = json.loads(result_json_string)

            if not isinstance(report_data, list):
                print("錯誤：輸出的JSON不是一個列表。")
                print("原始輸出：", result_json_string)
                return

            print(f"研究主題：{research_topic}\n")
            print("綜述報告初稿 (可追溯):\n")

            # 遍歷列表並以指定格式打印
            for item in report_data:
                sentence = item.get('sentence', 'N/A')
                source = item.get('source', 'N/A')
                print(f"- {sentence} [{source}]")

        except json.JSONDecodeError:
            print("錯誤：無法解析LLM返回的JSON。這可能是由於格式錯誤。")
            print("LLM原始輸出：\n", result_json_string)
        except Exception as e:
            print(f"處理結果時發生未知錯誤: {e}")
            print("原始輸出：", result_json_string)

        print("\n✅ Sprint 3 完成！可追溯性實現成功")

    except Exception as e:
        print(f"❌ 執行過程中發生錯誤: {str(e)}")
        print("請檢查API金鑰是否正確設置")

if __name__ == "__main__":
    main()

import os
import sys
import json
import time
from dotenv import load_dotenv
from crewai import Crew, Process
from agents import literature_scout, synthesizer, outline_planner, academic_writer
from tasks import create_research_task, create_summarize_task, create_outline_task, create_writing_task

load_dotenv()


def print_header():
    print("=" * 60)
    print("🔬 Veritas - 透明化AI研究協調平台 (原型 v1.0)".center(60))
    print("=" * 60 + "\n")


def main():
    print_header()

    topic = input("请输入您想研究的主題...\n> ")
    if not topic:
        print("錯誤：研究主題不能為空。")
        return

    print(f"\n📚 正在研究主題：{topic}")

    try:
        # --- 階段一：研究與大綱規劃 ---
        print("\n=== 階段一：研究與大綱規劃 ===")

        research_task = create_research_task(topic)
        summarize_task = create_summarize_task()
        outline_task = create_outline_task()

        # 建立任務鏈
        summarize_task.context = [research_task]
        outline_task.context = [summarize_task]

        planning_crew = Crew(
            agents=[literature_scout, synthesizer, outline_planner],
            tasks=[research_task, summarize_task, outline_task],
            process=Process.sequential,
            verbose=True
        )

        print("\n🚀 啟動規劃團隊...")
        crew_result = planning_crew.kickoff()

        if not crew_result or not crew_result.raw:
            raise ValueError("規劃團隊未能生成有效的大綱。")

        outline_json_string = crew_result.raw
        print("\n✅ 論文大綱JSON生成完畢！")
        outline_data = json.loads(outline_json_string)

        if not summarize_task.output or not summarize_task.output.raw:  # 检查 .raw
            raise ValueError("摘要任務未能生成有效的論點列表。")

        points_json_string = summarize_task.output.raw
        # 增加一層健壯性檢查
        try:
            loaded_points = json.loads(points_json_string)
            # 檢查加載後的數據是否是字典且包含 'outline' 鍵
            if isinstance(loaded_points, dict) and 'outline' in loaded_points:
                all_supporting_points = loaded_points['outline']
                print("ℹ️ 檢測到包裹物件，已成功提取 'outline' 列表。")
            # 檢查是否已經是列表
            elif isinstance(loaded_points, list):
                all_supporting_points = loaded_points
            else:
                raise TypeError("已解析的論點數據既不是列表，也不是包含'outline'鍵的字典。")
        except (json.JSONDecodeError, TypeError) as e:
            print(f"❌ 無法正確解析論點列表: {e}")
            print("   原始輸出:", points_json_string)
            return  # 無法繼續，提前退出

        # --- 階段二：分章節寫作 ---
        print("\n=== 階段二：分章節寫作 ===")

        full_paper_content = f"# {outline_data.get('title', '論文草稿')}\n\n"

        for chapter in outline_data.get("chapters", []):
            chapter_title = chapter.get("chapter_title", "未命名章節")
            indices = chapter.get("supporting_points_indices", [])

            chapter_points = [all_supporting_points[i] for i in indices if i < len(all_supporting_points)]

            print(f"\n✍️  正在撰寫章節：{chapter_title}...")

            writing_task = create_writing_task(chapter_title, json.dumps(chapter_points, ensure_ascii=False, indent=2))

            writing_crew = Crew(
                agents=[academic_writer],
                tasks=[writing_task],
                verbose=False
            )

            chapter_content_result = writing_crew.kickoff()
            if not chapter_content_result or not chapter_content_result.raw:
                print(f"⚠️ 章節「{chapter_title}」未能生成內容，已跳過。")
                chapter_content = "[本章節內容生成失敗]"
            else:
                chapter_content = chapter_content_result.raw

            full_paper_content += f"## {chapter_title}\n\n{chapter_content}\n\n"
            print(f"✅ 章節「{chapter_title}」撰寫完畢！")

        # --- 階段三：輸出最終結果 ---
        print("\n=== 階段三：論文生成與儲存 ===")

        filename = f"{topic.replace(' ', '_')[:30]}_draft.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(full_paper_content)

        print("\n\n" + "=" * 60)
        print("🎉 論文初稿生成成功！".center(60))
        print("=" * 60 + "\n")
        print(f"文件已儲存為：{filename}")

    except Exception as e:
        print(f"\n❌ 程式發生嚴重錯誤: {e}")


if __name__ == "__main__":
    main()
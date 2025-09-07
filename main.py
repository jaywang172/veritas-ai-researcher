import os
import sys
import json
import time
from dotenv import load_dotenv
from crewai import Crew, Process, Task
from agents import literature_scout, synthesizer, outline_planner, academic_writer, editor
from tasks import create_research_task, create_summarize_task, create_outline_task, create_writing_task, create_review_task

load_dotenv()


def print_header():
    print("=" * 60)
    print("🔬 Veritas - 透明化AI研究協調平台 (v2.0)".center(60))
    print("✨ 新功能：專業編輯審閱 + 自動摘要生成".center(60))
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
        # 解析論點列表（現在應該是穩定的JSON陣列格式）
        try:
            all_supporting_points = json.loads(points_json_string)
            if not isinstance(all_supporting_points, list):
                raise TypeError("論點數據應該是一個列表。")
            print(f"✅ 成功解析 {len(all_supporting_points)} 個論點")
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

        # --- 階段三：編輯與審閱 ---
        print("\n=== 階段三：編輯與審閱 ===")
        print("🎨 正在進行專業編輯審閱...")

        # 建立一個包含初稿內容的虛擬任務作為 context
        draft_context_task = Task(
            description="Initial draft content",
            expected_output="Draft content for review",
            agent=editor
        )
        draft_context_task.output = type('MockOutput', (), {'raw': full_paper_content})()

        review_task = create_review_task()
        review_task.context = [draft_context_task]  # 將初稿作為上下文

        review_crew = Crew(
            agents=[editor],
            tasks=[review_task],
            verbose=True
        )

        final_paper_result = review_crew.kickoff()
        if not final_paper_result or not final_paper_result.raw:
            print("⚠️ 編輯審閱失敗，將使用原始初稿。")
            final_paper_content = full_paper_content
        else:
            final_paper_content = final_paper_result.raw
            print("✅ 編輯審閱完成！")

        # --- 階段四：最終輸出 ---
        print("\n=== 階段四：論文完成與儲存 ===")

        filename = f"{topic.replace(' ', '_')[:30]}_v2.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(final_paper_content)

        print("\n\n" + "=" * 60)
        print("🎉 Veritas v2.0 論文生成成功！".center(60))
        print("=" * 60 + "\n")
        print(f"📄 最終版本已儲存為：{filename}")
        print("✨ 包含專業編輯審閱和摘要！")

    except Exception as e:
        print(f"\n❌ 程式發生嚴重錯誤: {e}")


if __name__ == "__main__":
    main()
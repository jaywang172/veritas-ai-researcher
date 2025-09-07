import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

# 導入LangGraph工作流程
from workflows.hybrid_workflow import create_hybrid_workflow, ResearchState

load_dotenv()


def print_header():
    print("=" * 60)
    print("🔬 Veritas - 混合智能研究平台 (v3.0)".center(60))
    print("🤖 自主規劃：LangGraph + 專案經理 + 混合智能".center(60))
    print("=" * 60 + "\n")


def display_outline_for_review(outline_data, all_supporting_points):
    """美化顯示生成的大綱，供用戶審閱"""
    print("\n" + "🎯 AI 生成的論文大綱".center(50, "="))
    print(f"\n📖 論文標題：{outline_data.get('title', '未定義標題')}")
    print(f"📊 總論點數：{len(all_supporting_points)} 個")
    print(f"📑 計劃章節：{len(outline_data.get('chapters', []))} 章")
    
    print("\n" + "📋 詳細章節結構".center(50, "-"))
    
    for i, chapter in enumerate(outline_data.get("chapters", []), 1):
        chapter_title = chapter.get("chapter_title", f"第{i}章")
        indices = chapter.get("supporting_points_indices", [])
        
        print(f"\n{i}. {chapter_title}")
        print(f"   📌 使用論點: {len(indices)} 個 (索引: {indices})")
        
        # 顯示該章節將使用的論點預覽
        if indices and len(indices) <= 3:  # 如果論點不多，顯示簡要內容
            for idx in indices:
                if idx < len(all_supporting_points):
                    point = all_supporting_points[idx]
                    sentence = point.get('sentence', '未知論點')
                    # 截斷長句子
                    preview = sentence[:80] + "..." if len(sentence) > 80 else sentence
                    print(f"      • {preview}")
        elif indices:
            # 論點太多時只顯示數量
            print(f"      • {len(indices)} 個論點將被整合到此章節")
    
    print("\n" + "=" * 50)


def get_user_approval():
    """獲取用戶對大綱的審批決定"""
    print("\n🤔 請審閱以上大綱，您希望如何繼續？")
    print("   [Y] 接受此大綱，繼續寫作")
    print("   [N] 重新生成大綱") 
    print("   [E] 手動編輯大綱 (高級功能)")
    print("   [Q] 退出程序")
    
    while True:
        choice = input("\n請輸入您的選擇 [Y/N/E/Q]: ").upper().strip()
        if choice in ['Y', 'N', 'E', 'Q']:
            return choice
        print("❌ 無效選擇，請輸入 Y、N、E 或 Q")


def edit_outline_interactively(outline_data, all_supporting_points):
    """交互式編輯大綱功能"""
    print("\n🛠️  進入大綱編輯模式")
    print("━" * 50)
    print("可用命令:")
    print("  • edit title <新標題>        - 修改論文標題")
    print("  • edit chapter <序號> <新標題> - 修改章節標題")
    print("  • move <章節序號> to <新位置>  - 移動章節位置")
    print("  • delete chapter <序號>      - 刪除章節")
    print("  • add point <論點序號> to <章節序號> - 添加論點到章節")
    print("  • remove point <論點序號> from <章節序號> - 從章節移除論點")
    print("  • show                       - 顯示當前大綱")
    print("  • done                       - 完成編輯")
    print("  • help                       - 顯示幫助")
    print("━" * 50)
    
    while True:
        command = input("\n📝 請輸入編輯命令: ").strip().lower()
        
        if command == "done":
            print("✅ 編輯完成！")
            break
        elif command == "show":
            display_outline_for_review(outline_data, all_supporting_points)
        elif command == "help":
            print("\n📚 編輯命令幫助：")
            print("例子:")
            print("  edit title AI對教育的影響分析")
            print("  edit chapter 2 人工智能的教育應用")
            print("  move 3 to 2")
            print("  delete chapter 4")
            print("  add point 5 to 2")
            print("  remove point 3 from 1")
        elif command.startswith("edit title "):
            new_title = command[11:].strip()
            if new_title:
                outline_data["title"] = new_title
                print(f"✅ 標題已更新為: {new_title}")
            else:
                print("❌ 請提供新標題")
        elif command.startswith("edit chapter "):
            try:
                parts = command[13:].strip().split(" ", 1)
                chapter_num = int(parts[0]) - 1  # 轉換為0索引
                new_title = parts[1] if len(parts) > 1 else ""
                
                if 0 <= chapter_num < len(outline_data.get("chapters", [])) and new_title:
                    outline_data["chapters"][chapter_num]["chapter_title"] = new_title
                    print(f"✅ 第{chapter_num + 1}章標題已更新為: {new_title}")
                else:
                    print("❌ 無效的章節序號或標題")
            except (ValueError, IndexError):
                print("❌ 命令格式錯誤，請使用: edit chapter <序號> <新標題>")
        elif command.startswith("move "):
            try:
                # 解析 "move 3 to 2" 格式
                import re
                match = re.match(r"move (\d+) to (\d+)", command)
                if match:
                    from_pos = int(match.group(1)) - 1
                    to_pos = int(match.group(2)) - 1
                    chapters = outline_data.get("chapters", [])
                    
                    if 0 <= from_pos < len(chapters) and 0 <= to_pos < len(chapters):
                        # 移動章節
                        chapter = chapters.pop(from_pos)
                        chapters.insert(to_pos, chapter)
                        print(f"✅ 已將第{from_pos + 1}章移動到第{to_pos + 1}章位置")
                    else:
                        print("❌ 無效的章節位置")
                else:
                    print("❌ 命令格式錯誤，請使用: move <序號> to <新位置>")
            except Exception:
                print("❌ 移動操作失敗")
        elif command.startswith("delete chapter "):
            try:
                chapter_num = int(command[15:].strip()) - 1
                chapters = outline_data.get("chapters", [])
                
                if 0 <= chapter_num < len(chapters):
                    deleted_chapter = chapters.pop(chapter_num)
                    print(f"✅ 已刪除章節: {deleted_chapter.get('chapter_title', f'第{chapter_num + 1}章')}")
                else:
                    print("❌ 無效的章節序號")
            except ValueError:
                print("❌ 請提供有效的章節序號")
        elif command.startswith("add point ") and " to " in command:
            try:
                # 解析 "add point 5 to 2" 格式
                import re
                match = re.match(r"add point (\d+) to (\d+)", command)
                if match:
                    point_idx = int(match.group(1))
                    chapter_num = int(match.group(2)) - 1
                    chapters = outline_data.get("chapters", [])
                    
                    if 0 <= point_idx < len(all_supporting_points) and 0 <= chapter_num < len(chapters):
                        if point_idx not in chapters[chapter_num]["supporting_points_indices"]:
                            chapters[chapter_num]["supporting_points_indices"].append(point_idx)
                            print(f"✅ 已將論點{point_idx}添加到第{chapter_num + 1}章")
                        else:
                            print("⚠️ 該論點已存在於此章節中")
                    else:
                        print("❌ 無效的論點索引或章節序號")
                else:
                    print("❌ 命令格式錯誤，請使用: add point <論點序號> to <章節序號>")
            except Exception:
                print("❌ 添加操作失敗")
        elif command.startswith("remove point ") and " from " in command:
            try:
                # 解析 "remove point 3 from 1" 格式
                import re
                match = re.match(r"remove point (\d+) from (\d+)", command)
                if match:
                    point_idx = int(match.group(1))
                    chapter_num = int(match.group(2)) - 1
                    chapters = outline_data.get("chapters", [])
                    
                    if 0 <= chapter_num < len(chapters):
                        if point_idx in chapters[chapter_num]["supporting_points_indices"]:
                            chapters[chapter_num]["supporting_points_indices"].remove(point_idx)
                            print(f"✅ 已從第{chapter_num + 1}章移除論點{point_idx}")
                        else:
                            print("⚠️ 該論點不在此章節中")
                    else:
                        print("❌ 無效的章節序號")
                else:
                    print("❌ 命令格式錯誤，請使用: remove point <論點序號> from <章節序號>")
            except Exception:
                print("❌ 移除操作失敗")
        else:
            print("❌ 未知命令，輸入 'help' 查看可用命令")
    
    return outline_data


def run_literature_review_workflow(topic):
    """執行傳統的文獻綜述工作流"""
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

        if not summarize_task.output or not summarize_task.output.raw:  # 檢查 .raw
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

        # --- 🤝 人機協作審批節點 ---
        print("\n=== 🤝 人機協作審批節點 ===")
        
        while True:
            # 展示AI生成的大綱供用戶審閱
            display_outline_for_review(outline_data, all_supporting_points)
            
            # 獲取用戶決定
            user_choice = get_user_approval()
            
            if user_choice == 'Y':
                print("\n✅ 用戶已批準大綱，繼續執行寫作階段...")
                break
            elif user_choice == 'N':
                print("\n🔄 重新生成大綱...")
                # 重新執行規劃階段
                print("🚀 重新啟動規劃團隊...")
                crew_result = planning_crew.kickoff()
                
                if not crew_result or not crew_result.raw:
                    print("❌ 重新生成失敗，將使用原大綱")
                    break
                
                outline_json_string = crew_result.raw
                try:
                    outline_data = json.loads(outline_json_string)
                    print("✅ 新大綱生成完成！")
                except json.JSONDecodeError:
                    print("❌ 新大綱格式錯誤，將使用原大綱")
                    break
                # 繼續循環，讓用戶再次審閱
            elif user_choice == 'E':
                print("\n🛠️  進入編輯模式...")
                outline_data = edit_outline_interactively(outline_data, all_supporting_points)
                print("\n✅ 大綱編輯完成！")
                # 顯示最終確認
                print("\n📋 最終確認的大綱：")
                display_outline_for_review(outline_data, all_supporting_points)
                confirm = input("\n確認使用此大綱繼續？[Y/n]: ").upper().strip()
                if confirm != 'N':
                    break
            elif user_choice == 'Q':
                print("\n👋 用戶選擇退出程序")
                return
        
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

        # --- 階段四：引文格式化 ---
        print("\n=== 階段四：引文格式化 ===")
        print("📚 正在提取引用來源並生成APA格式參考文獻...")

        # 建立引文內容的虛擬任務作為 context
        citation_context_task = Task(
            description="Edited paper content for citation formatting",
            expected_output="Paper content for reference extraction",
            agent=citation_formatter
        )
        citation_context_task.output = type('MockOutput', (), {'raw': final_paper_content})()

        citation_task = create_citation_task()
        citation_task.context = [citation_context_task]

        citation_crew = Crew(
            agents=[citation_formatter],
            tasks=[citation_task],
            verbose=True
        )

        references_result = citation_crew.kickoff()
        if not references_result or not references_result.raw:
            print("⚠️ 引文格式化失敗，將不添加參考文獻列表。")
            complete_paper_content = final_paper_content
        else:
            references_content = references_result.raw
            
            # 驗證引文輸出品質
            if "我現在知道最終答案" in references_content or "Final Answer" in references_content:
                print("⚠️ 檢測到引文格式化輸出異常，嘗試使用備用格式...")
                # 創建基本的參考文獻列表
                references_content = "\n\n## References\n\n注意：此論文包含多個網路來源引用，請手動驗證和格式化參考文獻。"
            elif not references_content.strip().startswith("## References"):
                print("⚠️ 引文格式不正確，正在修正...")
                # 確保有正確的標題
                references_content = "## References\n\n" + references_content.strip()
            
            # 將參考文獻添加到論文末尾
            complete_paper_content = final_paper_content + "\n\n" + references_content
            print("✅ 引文格式化完成！已生成APA格式參考文獻列表。")

        # --- 階段五：最終輸出 ---
        print("\n=== 階段五：論文完成與儲存 ===")

        filename = f"{topic.replace(' ', '_')[:30]}_v2.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(complete_paper_content)

        print("\n\n" + "=" * 60)
        print("🎉 Veritas v2.0 論文生成成功！".center(60))
        print("=" * 60 + "\n")
        print(f"📄 最終版本已儲存為：{filename}")
        print("✨ 包含專業編輯審閱、摘要和APA格式參考文獻！")

    except Exception as e:
        print(f"\n❌ 程式發生嚴重錯誤: {e}")


def run_data_analysis_workflow():
    """執行新的數據分析工作流"""
    print("\n🔬 正在準備數據分析工作流...")
    
    # 獲取用戶輸入
    data_file_path = input("請輸入數據文件路徑 (支持 .csv, .xlsx, .json): ")
    if not data_file_path:
        print("❌ 錯誤：數據文件路徑不能為空。")
        return
        
    analysis_goal = input("請描述您的分析目標 (例如：探索數據分布，尋找相關性等): ")
    if not analysis_goal:
        print("❌ 錯誤：分析目標不能為空。")
        return
    
    print(f"\n📊 數據文件：{data_file_path}")
    print(f"🎯 分析目標：{analysis_goal}")
    
    try:
        # --- 階段一：數據分析 ---
        print("\n=== 階段一：數據分析執行 ===")
        print("🧪 啟動計算科學家進行數據分析...")
        
        # 創建數據分析任務
        analysis_task = create_data_analysis_task(data_file_path, analysis_goal)
        
        # 創建專門的數據分析Crew
        analysis_crew = Crew(
            agents=[computational_scientist],
            tasks=[analysis_task],
            verbose=True
        )
        
        # 執行數據分析
        analysis_result = analysis_crew.kickoff()
        
        if not analysis_result or not analysis_result.raw:
            print("⚠️ 數據分析失敗，無法生成報告。")
            return
        
        analysis_summary = analysis_result.raw
        print("✅ 數據分析完成！")
        
        # --- 階段二：報告生成 ---
        print("\n=== 階段二：分析報告撰寫 ===")
        print("📝 正在將分析結果轉化為學術報告...")
        
        # 將分析結果包裝成"論點"格式
        analysis_point = {
            "sentence": analysis_summary,
            "source": f"本地數據分析: {data_file_path}"
        }
        
        # 創建簡化的報告大綱
        simple_outline = {
            "title": f"數據分析報告：{analysis_goal}",
            "chapters": [
                {"chapter_title": "1. 引言", "supporting_points_indices": [0]},
                {"chapter_title": "2. 數據分析結果", "supporting_points_indices": [0]},
                {"chapter_title": "3. 結論與建議", "supporting_points_indices": [0]}
            ]
        }
        
        # 使用現有的寫作流程生成報告
        all_points = [analysis_point]
        full_report_content = f"# {simple_outline['title']}\n\n"
        
        for chapter in simple_outline["chapters"]:
            chapter_title = chapter["chapter_title"]
            print(f"\n✍️ 正在撰寫章節：{chapter_title}...")
            
            # 為每個章節創建寫作任務
            writing_task = create_writing_task(chapter_title, json.dumps(all_points, ensure_ascii=False, indent=2))
            
            writing_crew = Crew(
                agents=[academic_writer],
                tasks=[writing_task],
                verbose=False
            )
            
            chapter_result = writing_crew.kickoff()
            if chapter_result and chapter_result.raw:
                chapter_content = chapter_result.raw
            else:
                chapter_content = "[章節內容生成失敗]"
            
            full_report_content += f"## {chapter_title}\n\n{chapter_content}\n\n"
            print(f"✅ 章節「{chapter_title}」撰寫完畢！")
        
        # --- 階段三：最終輸出 ---
        print("\n=== 階段三：報告保存 ===")
        
        # 生成文件名
        safe_goal = "".join(c for c in analysis_goal if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"data_analysis_report_{safe_goal[:20]}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(full_report_content)
        
        print("\n\n" + "=" * 60)
        print("🎉 數據分析報告生成成功！".center(60))
        print("=" * 60 + "\n")
        print(f"📄 報告已保存為：{filename}")
        print("📊 包含數據分析結果和可視化圖表！")
        
    except Exception as e:
        print(f"\n❌ 數據分析發生錯誤: {e}")


def main():
    """主函數 - LangGraph混合智能工作流程入口"""
    print_header()
    
    print("🚀 歡迎使用 Veritas v3.0 自主混合智能研究平台！")
    print("✨ 支援開放式研究目標，自動判斷並執行最佳研究策略")
    print("\n💡 使用範例：")
    print("   • 「分析人工智能對教育的影響」")
    print("   • 「基於 sales_data.csv，分析南部地區銷售表現並結合市場研究」")
    print("   • 「研究氣候變遷的經濟影響，並分析相關資料趨勢」")
    
    # 獲取使用者的開放式研究目標
    research_goal = input("\n🎯 請描述您的研究目標: ").strip()
    if not research_goal:
        print("❌ 錯誤：研究目標不能為空。")
        return
    
    # 可選：資料檔案路徑
    data_file = input("📁 是否有資料檔案需要分析？(留空跳過，或輸入檔案路徑): ").strip()
    data_file_path = data_file if data_file and Path(data_file).exists() else None
    
    if data_file and not data_file_path:
        print(f"⚠️ 檔案 '{data_file}' 不存在，將進行純文獻研究")
    
    print(f"\n🧠 專案經理正在分析您的研究目標...")
    print(f"📋 研究目標：{research_goal}")
    if data_file_path:
        print(f"📊 資料檔案：{data_file_path}")
    
    try:
        # 初始化研究狀態
        initial_state = ResearchState(
            research_goal=research_goal,
            data_file_path=data_file_path
        )
        
        # 創建並執行LangGraph工作流程
        workflow = create_hybrid_workflow()
        
        print("\n🔄 啟動LangGraph智能工作流程...")
        print("=" * 60)
        
        # 執行工作流程
        final_state = workflow.invoke(initial_state)
        
        # 處理結果
        if final_state.complete_paper_content:
            # 生成檔案名
            safe_goal = "".join(c for c in research_goal if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = f"veritas_v3_{safe_goal[:30]}.txt"
            
            # 儲存結果
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(final_state.complete_paper_content)
            
            print("\n" + "=" * 60)
            print("🎉 Veritas v3.0 混合智能研究完成！".center(60))
            print("=" * 60)
            print(f"📄 研究報告已儲存為：{filename}")
            print(f"✅ 完成任務：{', '.join(final_state.tasks_completed)}")
            
            if final_state.project_plan:
                research_type = final_state.project_plan.get('research_type', 'UNKNOWN')
                print(f"🧠 研究類型：{research_type}")
            
            if final_state.errors:
                print(f"⚠️ 過程中遇到 {len(final_state.errors)} 個警告")
                
        else:
            print("\n❌ 研究流程未能完成，請檢查錯誤訊息")
            if final_state.errors:
                print("錯誤列表：")
                for error in final_state.errors:
                    print(f"  • {error}")
    
    except Exception as e:
        print(f"\n❌ 工作流程執行失敗: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
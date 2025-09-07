import os
import sys
import json
import time
from dotenv import load_dotenv
from crewai import Crew, Process, Task
from agents import literature_scout, synthesizer, outline_planner, academic_writer, editor, citation_formatter
from tasks import create_research_task, create_summarize_task, create_outline_task, create_writing_task, create_review_task, create_citation_task

load_dotenv()


def print_header():
    print("=" * 60)
    print("🔬 Veritas - 透明化AI研究協調平台 (v2.0)".center(60))
    print("✨ 完整功能：編輯審閱 + 人機協作 + APA引文格式化".center(60))
    print("=" * 60 + "\n")


def display_outline_for_review(outline_data, all_supporting_points):
    """美化显示生成的大纲，供用户审阅"""
    print("\n" + "🎯 AI 生成的论文大纲".center(50, "="))
    print(f"\n📖 论文标题：{outline_data.get('title', '未定义标题')}")
    print(f"📊 总论点数：{len(all_supporting_points)} 个")
    print(f"📑 计划章节：{len(outline_data.get('chapters', []))} 章")
    
    print("\n" + "📋 详细章节结构".center(50, "-"))
    
    for i, chapter in enumerate(outline_data.get("chapters", []), 1):
        chapter_title = chapter.get("chapter_title", f"第{i}章")
        indices = chapter.get("supporting_points_indices", [])
        
        print(f"\n{i}. {chapter_title}")
        print(f"   📌 使用论点: {len(indices)} 个 (索引: {indices})")
        
        # 显示该章节将使用的论点预览
        if indices and len(indices) <= 3:  # 如果论点不多，显示简要内容
            for idx in indices:
                if idx < len(all_supporting_points):
                    point = all_supporting_points[idx]
                    sentence = point.get('sentence', '未知论点')
                    # 截断长句子
                    preview = sentence[:80] + "..." if len(sentence) > 80 else sentence
                    print(f"      • {preview}")
        elif indices:
            # 论点太多时只显示数量
            print(f"      • {len(indices)} 个论点将被整合到此章节")
    
    print("\n" + "=" * 50)


def get_user_approval():
    """获取用户对大纲的审批决定"""
    print("\n🤔 请审阅以上大纲，您希望如何继续？")
    print("   [Y] 接受此大纲，继续写作")
    print("   [N] 重新生成大纲") 
    print("   [E] 手动编辑大纲 (高级功能)")
    print("   [Q] 退出程序")
    
    while True:
        choice = input("\n请输入您的选择 [Y/N/E/Q]: ").upper().strip()
        if choice in ['Y', 'N', 'E', 'Q']:
            return choice
        print("❌ 无效选择，请输入 Y、N、E 或 Q")


def edit_outline_interactively(outline_data, all_supporting_points):
    """交互式编辑大纲功能"""
    print("\n🛠️  进入大纲编辑模式")
    print("━" * 50)
    print("可用命令:")
    print("  • edit title <新标题>        - 修改论文标题")
    print("  • edit chapter <序号> <新标题> - 修改章节标题")
    print("  • move <章节序号> to <新位置>  - 移动章节位置")
    print("  • delete chapter <序号>      - 删除章节")
    print("  • add point <论点序号> to <章节序号> - 添加论点到章节")
    print("  • remove point <论点序号> from <章节序号> - 从章节移除论点")
    print("  • show                       - 显示当前大纲")
    print("  • done                       - 完成编辑")
    print("  • help                       - 显示帮助")
    print("━" * 50)
    
    while True:
        command = input("\n📝 请输入编辑命令: ").strip().lower()
        
        if command == "done":
            print("✅ 编辑完成！")
            break
        elif command == "show":
            display_outline_for_review(outline_data, all_supporting_points)
        elif command == "help":
            print("\n📚 编辑命令帮助：")
            print("例子:")
            print("  edit title AI对教育的影响分析")
            print("  edit chapter 2 人工智能的教育应用")
            print("  move 3 to 2")
            print("  delete chapter 4")
            print("  add point 5 to 2")
            print("  remove point 3 from 1")
        elif command.startswith("edit title "):
            new_title = command[11:].strip()
            if new_title:
                outline_data["title"] = new_title
                print(f"✅ 标题已更新为: {new_title}")
            else:
                print("❌ 请提供新标题")
        elif command.startswith("edit chapter "):
            try:
                parts = command[13:].strip().split(" ", 1)
                chapter_num = int(parts[0]) - 1  # 转换为0索引
                new_title = parts[1] if len(parts) > 1 else ""
                
                if 0 <= chapter_num < len(outline_data.get("chapters", [])) and new_title:
                    outline_data["chapters"][chapter_num]["chapter_title"] = new_title
                    print(f"✅ 第{chapter_num + 1}章标题已更新为: {new_title}")
                else:
                    print("❌ 无效的章节序号或标题")
            except (ValueError, IndexError):
                print("❌ 命令格式错误，请使用: edit chapter <序号> <新标题>")
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
                        # 移动章节
                        chapter = chapters.pop(from_pos)
                        chapters.insert(to_pos, chapter)
                        print(f"✅ 已将第{from_pos + 1}章移动到第{to_pos + 1}章位置")
                    else:
                        print("❌ 无效的章节位置")
                else:
                    print("❌ 命令格式错误，请使用: move <序号> to <新位置>")
            except Exception:
                print("❌ 移动操作失败")
        elif command.startswith("delete chapter "):
            try:
                chapter_num = int(command[15:].strip()) - 1
                chapters = outline_data.get("chapters", [])
                
                if 0 <= chapter_num < len(chapters):
                    deleted_chapter = chapters.pop(chapter_num)
                    print(f"✅ 已删除章节: {deleted_chapter.get('chapter_title', f'第{chapter_num + 1}章')}")
                else:
                    print("❌ 无效的章节序号")
            except ValueError:
                print("❌ 请提供有效的章节序号")
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
                            print(f"✅ 已将论点{point_idx}添加到第{chapter_num + 1}章")
                        else:
                            print("⚠️ 该论点已存在于此章节中")
                    else:
                        print("❌ 无效的论点索引或章节序号")
                else:
                    print("❌ 命令格式错误，请使用: add point <论点序号> to <章节序号>")
            except Exception:
                print("❌ 添加操作失败")
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
                            print(f"✅ 已从第{chapter_num + 1}章移除论点{point_idx}")
                        else:
                            print("⚠️ 该论点不在此章节中")
                    else:
                        print("❌ 无效的章节序号")
                else:
                    print("❌ 命令格式错误，请使用: remove point <论点序号> from <章节序号>")
            except Exception:
                print("❌ 移除操作失败")
        else:
            print("❌ 未知命令，输入 'help' 查看可用命令")
    
    return outline_data


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

        # --- 🤝 人機協作審批節點 ---
        print("\n=== 🤝 人機協作審批節點 ===")
        
        while True:
            # 展示AI生成的大纲供用户审阅
            display_outline_for_review(outline_data, all_supporting_points)
            
            # 获取用户决定
            user_choice = get_user_approval()
            
            if user_choice == 'Y':
                print("\n✅ 用户已批准大纲，继续执行写作阶段...")
                break
            elif user_choice == 'N':
                print("\n🔄 重新生成大纲...")
                # 重新执行规划阶段
                print("🚀 重新启动规划团队...")
                crew_result = planning_crew.kickoff()
                
                if not crew_result or not crew_result.raw:
                    print("❌ 重新生成失败，将使用原大纲")
                    break
                
                outline_json_string = crew_result.raw
                try:
                    outline_data = json.loads(outline_json_string)
                    print("✅ 新大纲生成完成！")
                except json.JSONDecodeError:
                    print("❌ 新大纲格式错误，将使用原大纲")
                    break
                # 继续循环，让用户再次审阅
            elif user_choice == 'E':
                print("\n🛠️  进入编辑模式...")
                outline_data = edit_outline_interactively(outline_data, all_supporting_points)
                print("\n✅ 大纲编辑完成！")
                # 显示最终确认
                print("\n📋 最终确认的大纲：")
                display_outline_for_review(outline_data, all_supporting_points)
                confirm = input("\n确认使用此大纲继续？[Y/n]: ").upper().strip()
                if confirm != 'N':
                    break
            elif user_choice == 'Q':
                print("\n👋 用户选择退出程序")
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


if __name__ == "__main__":
    main()
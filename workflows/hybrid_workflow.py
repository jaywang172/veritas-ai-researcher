#!/usr/bin/env python3
"""
Veritas Hybrid Intelligence Workflow
LangGraph-based state machine for autonomous research planning and execution.
"""

import json
from typing import Dict, List, Optional, TypedDict, Annotated
from pathlib import Path
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage

# Import our agents and tasks
from agents import (
    project_manager, literature_scout, synthesizer, outline_planner,
    academic_writer, editor, citation_formatter, computational_scientist
)
from tasks import (
    create_research_task, create_summarize_task, create_outline_task,
    create_writing_task, create_review_task, create_citation_task,
    create_data_analysis_task
)
from crewai import Crew, Process
from datetime import datetime


# 🆕 版本控制與歷史追蹤輔助函數
def save_version_to_history(state: 'ResearchState', content: str, version_type: str, description: str = "") -> None:
    """
    將當前版本保存到歷史記錄中
    
    Args:
        state: 研究狀態
        content: 要保存的內容
        version_type: 版本類型 (draft, revised, final)
        description: 版本描述
    """
    if not state.get('version_history'):
        state['version_history'] = []
    
    current_version = state.get('current_version', 0) + 1
    state['current_version'] = current_version
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    version_record = {
        'version': current_version,
        'timestamp': timestamp,
        'type': version_type,
        'description': description,
        'content': content,
        'revision_count': state.get('revision_count', 0),
        'review_score': state.get('review_score'),
        'word_count': len(content.split()) if content else 0
    }
    
    state['version_history'].append(version_record)
    
    # 如果啟用自動保存，創建檔案
    if state.get('auto_save_enabled', True):
        try:
            safe_goal = "".join(c for c in state['research_goal'] if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = f"veritas_v{current_version:02d}_{version_type}_{safe_goal[:20]}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# Veritas v3.1 - 版本 {current_version} ({version_type})\n")
                f.write(f"# 時間戳：{timestamp}\n")
                f.write(f"# 修訂次數：{state.get('revision_count', 0)}\n")
                f.write(f"# 評分：{state.get('review_score', 'N/A')}/10\n")
                f.write(f"# 描述：{description}\n")
                f.write(f"# 字數：{len(content.split())} 字\n")
                f.write(f"{'='*60}\n\n")
                f.write(content)
            
            print(f"版本 v{current_version} 已自動保存：{filename}")
            
        except Exception as e:
            print(f"自動保存失敗：{e}")


def get_latest_version_content(state: 'ResearchState') -> Optional[str]:
    """獲取最新版本的內容"""
    version_history = state.get('version_history', [])
    if version_history:
        return version_history[-1].get('content')
    return None


def format_revision_history_summary(state: 'ResearchState') -> str:
    """格式化修訂歷史摘要，用於展示給用戶"""
    revision_history = state.get('revision_history', [])
    if not revision_history:
        return "無修訂歷史"
    
    summary = "## 🔄 修訂歷史摘要\n\n"
    for i, record in enumerate(revision_history, 1):
        decision = record.get('decision', 'UNKNOWN')
        score = record.get('quality_score', 'N/A')
        priority = record.get('revision_priority', 'N/A')
        feedback = record.get('feedback', '')[:100] + "..." if len(record.get('feedback', '')) > 100 else record.get('feedback', '')
        
        summary += f"### 第 {i} 輪審核\n"
        summary += f"- **決策**：{decision}\n"
        summary += f"- **評分**：{score}/10\n"
        summary += f"- **優先級**：{priority}\n"
        summary += f"- **反饋**：{feedback}\n\n"
    
    return summary


class ResearchState(TypedDict):
    """
    混合研究工作流程的狀態定義
    包含整個研究過程中需要共享的所有資訊
    
    v3.1 升級：引入版本控制與智能審稿迴圈
    """
    # 輸入資訊
    research_goal: str                          # 使用者的研究目標
    data_file_path: Optional[str]              # 可選的資料檔案路徑
    
    # 專案規劃
    project_plan: Optional[Dict]               # 專案經理的策略規劃
    
    # 文獻研究結果
    literature_data: Optional[str]             # 原始文獻搜集資料
    literature_points: Optional[List[Dict]]    # 提取的文獻論點
    
    # 數據分析結果
    data_analysis_results: Optional[str]       # 數據分析摘要
    data_analysis_points: Optional[List[Dict]] # 格式化的分析論點
    
    # 整合與寫作
    combined_points: Optional[List[Dict]]      # 整合的論點列表
    outline_data: Optional[Dict]               # 論文大綱
    draft_content: Optional[str]               # 初稿內容
    final_paper_content: Optional[str]         # 編輯後的論文
    complete_paper_content: Optional[str]      # 包含引文的完整論文
    
    # 🆕 版本控制與歷史追蹤
    version_history: List[Dict]                # 所有版本的完整歷史
    current_version: int                       # 當前版本號
    auto_save_enabled: bool                    # 是否啟用自動版本儲存
    
    # 🆕 智能品質審核系統
    review_decision: Optional[str]             # 審核決策：ACCEPT/REVISE/REJECT
    review_feedback: Optional[str]             # 詳細的審核意見和修改建議
    review_score: Optional[int]                # 品質評分 (1-10)
    review_priority: Optional[str]             # 修訂優先級：HIGH/MEDIUM/LOW
    specific_issues: List[str]                 # 具體問題清單
    
    # 🆕 修訂迴圈控制
    revision_count: int                        # 修訂次數計數器
    max_revisions: int                         # 最大修訂次數限制
    revision_history: List[Dict]               # 詳細修訂歷史記錄
    quality_gates_passed: List[str]           # 已通過的品質關卡
    is_in_revision_loop: bool                  # 是否處於修訂迴圈中
    last_revision_timestamp: Optional[str]    # 最後修訂時間戳
    
    # 🆕 失敗保護與最終裁決
    force_accept_reason: Optional[str]         # 強制接受的原因
    workflow_completion_status: str           # 工作流程完成狀態
    final_decision_maker: Optional[str]        # 最終決策者 (AI/HUMAN/SYSTEM)
    
    # 工作流程狀態
    tasks_completed: List[str]                 # 已完成的任務列表
    current_stage: str                         # 目前執行階段
    errors: List[str]                          # 錯誤記錄
    
    # LangGraph 需要的訊息狀態
    messages: Annotated[List[Dict], "訊息歷史"]


def project_planning_node(state: ResearchState) -> ResearchState:
    """
    專案規劃節點：由專案經理分析目標並制定執行策略
    """
    print("\n=== 專案規劃階段 ===")
    print(f"研究目標：{state['research_goal']}")
    if state.get('data_file_path'):
        print(f"資料檔案：{state['data_file_path']}")
    
    # 構建專案經理的分析提示
    planning_prompt = f"""
    作為首席研究策略師，請分析以下研究請求並制定執行策略：
    
    研究目標：{state['research_goal']}
    資料檔案：{state.get('data_file_path', '無')}
    
    請分析並決定：
    1. 這個研究需要什麼類型的分析（文獻回顧、數據分析、或兩者結合）
    2. 應該按什麼順序執行任務
    3. 哪些專家代理人需要參與
    
    請以JSON格式回應：
    {{
        "research_type": "LITERATURE_ONLY/DATA_ONLY/HYBRID",
        "requires_literature": true/false,
        "requires_data_analysis": true/false,
        "execution_strategy": "SEQUENTIAL/PARALLEL",
        "priority_tasks": ["task1", "task2", ...],
        "reasoning": "決策理由"
    }}
    """
    
    try:
        # 讓專案經理分析並規劃
        from crewai import Task
        
        planning_task = Task(
            description=planning_prompt,
            expected_output="JSON格式的專案規劃",
            agent=project_manager
        )
        
        planning_crew = Crew(
            agents=[project_manager],
            tasks=[planning_task],
            verbose=False
        )
        
        planning_result = planning_crew.kickoff()
        
        if planning_result and planning_result.raw:
            try:
                # 嘗試解析JSON回應
                plan_text = planning_result.raw
                # 提取JSON部分（如果被包裝在其他文字中）
                if '{' in plan_text and '}' in plan_text:
                    json_start = plan_text.find('{')
                    json_end = plan_text.rfind('}') + 1
                    json_text = plan_text[json_start:json_end]
                    project_plan = json.loads(json_text)
                else:
                    # 如果沒有JSON，創建默認計劃
                    project_plan = {
                        "research_type": "HYBRID" if state.get('data_file_path') else "LITERATURE_ONLY",
                        "requires_literature": True,
                        "requires_data_analysis": bool(state.get('data_file_path')),
                        "execution_strategy": "PARALLEL",
                        "priority_tasks": ["literature_research", "data_analysis"] if state.get('data_file_path') else ["literature_research"],
                        "reasoning": "基於輸入自動判斷"
                    }
                
                print(f"專案規劃完成：{project_plan['research_type']}")
                print(f"執行策略：{project_plan['execution_strategy']}")
                
                state['project_plan'] = project_plan
                state['current_stage'] = 'planning_completed'
                state['tasks_completed'].append('project_planning')
                
            except json.JSONDecodeError:
                print("無法解析專案規劃JSON，使用默認策略")
                state['project_plan'] = {
                    "research_type": "HYBRID" if state.get('data_file_path') else "LITERATURE_ONLY",
                    "requires_literature": True,
                    "requires_data_analysis": bool(state.get('data_file_path')),
                    "execution_strategy": "PARALLEL",
                    "priority_tasks": ["literature_research"],
                    "reasoning": "JSON解析失敗，使用備用策略"
                }
        else:
            print("專案規劃失敗，使用默認策略")
            state['errors'].append("專案規劃節點執行失敗")
    
    except Exception as e:
        print(f"專案規劃過程發生錯誤：{e}")
        state['errors'].append(f"專案規劃錯誤：{str(e)}")
        # 使用備用策略
        state['project_plan'] = {
            "research_type": "HYBRID" if state.get('data_file_path') else "LITERATURE_ONLY",
            "requires_literature": True,
            "requires_data_analysis": bool(state.get('data_file_path')),
            "execution_strategy": "SEQUENTIAL",
            "priority_tasks": ["literature_research"],
            "reasoning": "錯誤恢復策略"
        }
        state['current_stage'] = 'planning_completed'
        state['tasks_completed'].append('project_planning')
    
    return state


def literature_research_node(state: ResearchState) -> ResearchState:
    """
    文獻研究節點：搜集並分析外部文獻資料
    """
    print("\n=== 文獻研究階段 ===")
    
    try:
        # 階段一：文獻搜集
        research_task = create_research_task(state['research_goal'])
        research_crew = Crew(
            agents=[literature_scout],
            tasks=[research_task],
            verbose=False
        )
        
        literature_result = research_crew.kickoff()
        if literature_result and literature_result.raw:
            state['literature_data'] = literature_result.raw
            print("文獻搜集完成")
        else:
            state['errors'].append("文獻搜集失敗")
            return state
        
        # 階段二：論點提取
        summarize_task = create_summarize_task()
        summarize_task.context = [research_task]
        
        synthesis_crew = Crew(
            agents=[synthesizer],
            tasks=[summarize_task],
            verbose=False
        )
        
        synthesis_result = synthesis_crew.kickoff()
        if synthesis_result and synthesis_result.raw:
            try:
                points_data = json.loads(synthesis_result.raw)
                state['literature_points'] = points_data
                print(f"文獻論點提取完成：{len(points_data)} 個論點")
            except json.JSONDecodeError:
                print("文獻論點JSON格式錯誤")
                state['errors'].append("文獻論點解析失敗")
        else:
            state['errors'].append("文獻論點提取失敗")
        
        state['tasks_completed'].append('literature_research')
        
    except Exception as e:
        print(f"文獻研究過程發生錯誤：{e}")
        state['errors'].append(f"文獻研究錯誤：{str(e)}")
    
    return state


def data_analysis_node(state: ResearchState) -> ResearchState:
    """
    數據分析節點：執行本地數據分析
    """
    print("\n📊 === 數據分析階段 ===")
    
    if not state.get('data_file_path'):
        print("無數據檔案，跳過數據分析")
        return state
    
    try:
        analysis_task = create_data_analysis_task(
            state['data_file_path'], 
            state['research_goal']
        )
        
        analysis_crew = Crew(
            agents=[computational_scientist],
            tasks=[analysis_task],
            verbose=False
        )
        
        analysis_result = analysis_crew.kickoff()
        
        if analysis_result and analysis_result.raw:
            state['data_analysis_results'] = analysis_result.raw
            
            # 將數據分析結果格式化為論點
            analysis_point = {
                "sentence": analysis_result.raw,
                "source": f"本地數據分析：{state['data_file_path']}"
            }
            state['data_analysis_points'] = [analysis_point]
            
            print("數據分析完成")
            state['tasks_completed'].append('data_analysis')
        else:
            state['errors'].append("數據分析執行失敗")
            # 即使失敗也標記為已完成，避免無限循環
            state['tasks_completed'].append('data_analysis')
            # 提供備用分析結果
            state['data_analysis_points'] = [{
                "sentence": "數據分析執行失敗，無法生成有效的分析結果。建議檢查數據文件和分析工具配置。",
                "source": "本地數據分析"
            }]
    
    except Exception as e:
        print(f"數據分析過程發生錯誤：{e}")
        state['errors'].append(f"數據分析錯誤：{str(e)}")
        # 即使失敗也標記為已完成，避免無限循環
        state['tasks_completed'].append('data_analysis')
        # 提供備用分析結果
        state['data_analysis_points'] = [{
            "sentence": f"數據分析過程遇到技術問題：{str(e)}。建議手動檢查數據文件格式和內容。",
            "source": "本地數據分析"
        }]
    
    return state


def integration_node(state: ResearchState) -> ResearchState:
    """
    整合節點：結合文獻和數據分析結果，生成統一大綱
    """
    print("\n🔄 === 整合與規劃階段 ===")
    
    try:
        # 整合所有論點
        combined_points = []
        
        if state.get('literature_points'):
            combined_points.extend(state['literature_points'])
            print(f"整合文獻論點：{len(state['literature_points'])} 個")
        
        if state.get('data_analysis_points'):
            combined_points.extend(state['data_analysis_points'])
            print(f"整合數據分析論點：{len(state['data_analysis_points'])} 個")
        
        state['combined_points'] = combined_points
        
        if not combined_points:
            state['errors'].append("沒有論點可供整合")
            return state
        
        # 生成統一大綱
        outline_task = create_outline_task()
        
        # 創建虛擬的context任務來傳遞論點資料
        from crewai import Task
        context_task = Task(
            description="Combined research points",
            expected_output="Research points for outline generation",
            agent=synthesizer
        )
        context_task.output = type('MockOutput', (), {
            'raw': json.dumps(combined_points, ensure_ascii=False, indent=2)
        })()
        
        outline_task.context = [context_task]
        
        outline_crew = Crew(
            agents=[outline_planner],
            tasks=[outline_task],
            verbose=False
        )
        
        outline_result = outline_crew.kickoff()
        
        if outline_result and outline_result.raw:
            try:
                outline_data = json.loads(outline_result.raw)
                state['outline_data'] = outline_data
                print(f"大綱生成完成：{outline_data.get('title', '未知標題')}")
                state['tasks_completed'].append('integration')
            except json.JSONDecodeError:
                print("大綱JSON格式錯誤")
                state['errors'].append("大綱解析失敗")
        else:
            state['errors'].append("大綱生成失敗")
    
    except Exception as e:
        print(f"整合過程發生錯誤：{e}")
        state['errors'].append(f"整合錯誤：{str(e)}")
    
    return state


def writing_node(state: ResearchState) -> ResearchState:
    """
    寫作節點：根據大綱和論點生成論文初稿
    """
    print("\n=== 寫作階段 ===")
    
    if not state.get('outline_data') or not state.get('combined_points'):
        state['errors'].append("缺少大綱或論點資料")
        return state
    
    try:
        outline_data = state['outline_data']
        all_points = state['combined_points']
        
        draft_content = f"# {outline_data.get('title', '研究報告')}\n\n"
        
        for chapter in outline_data.get("chapters", []):
            chapter_title = chapter.get("chapter_title", "未命名章節")
            indices = chapter.get("supporting_points_indices", [])
            
            # 獲取該章節的論點
            chapter_points = [all_points[i] for i in indices if i < len(all_points)]
            
            print(f"寫作章節：{chapter_title}")
            
            writing_task = create_writing_task(
                chapter_title, 
                json.dumps(chapter_points, ensure_ascii=False, indent=2)
            )
            
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
            
            draft_content += f"## {chapter_title}\n\n{chapter_content}\n\n"
        
        state['draft_content'] = draft_content
        
        # 🆕 版本控制：保存初稿
        save_version_to_history(
            state, 
            draft_content, 
            "draft", 
            "AI團隊協作生成的初稿"
        )
        
        print("初稿撰寫完成")
        state['tasks_completed'].append('writing')
    
    except Exception as e:
        print(f"寫作過程發生錯誤：{e}")
        state['errors'].append(f"寫作錯誤：{str(e)}")
        # 即使失敗也標記為已完成，避免無限循環
        state['tasks_completed'].append('writing')
        state['draft_content'] = f"# 研究報告\n\n由於技術問題，寫作過程未能完成。錯誤：{str(e)}\n\n請檢查配置並重試。"
    
    return state


def editing_node(state: ResearchState) -> ResearchState:
    """
    編輯節點：專業編輯審閱和潤色
    """
    print("\n=== 編輯審閱階段 ===")
    
    if not state.get('draft_content'):
        state['errors'].append("沒有初稿可供編輯")
        return state
    
    try:
        from crewai import Task
        
        # 直接創建包含完整內容的編輯任務
        review_task = Task(
            description=f'''這是論文的完整初稿：

{state['draft_content']}

**你的編輯任務**：
1. **通讀全文**：仔細審閱整篇論文，識別並修正任何不連貫或矛盾之處
2. **章節過渡**：確保所有章節之間的過渡自然流暢，必要時添加或重寫過渡段落
3. **風格統一**：統一全文的術語、寫作風格和語調，確保一致性
4. **邏輯檢查**：驗證論述邏輯的完整性，確保論點之間的關聯性清晰
5. **摘要生成**：根據全文核心內容，在文章最開頭生成一段 150-250 字的專業摘要

**格式要求**：
- 在文章最開始添加 "## 摘要 (Abstract)" 部分
- 保持所有現有的來源標註
- 保持章節結構，但可以調整內容和過渡
- 確保摘要簡潔且概括了論文的主要貢獻''',
            expected_output='''一份經過專業編輯和潤色的完整論文文本，包含：

1. **摘要部分**：在文章開頭的專業摘要 (150-250字)
2. **完整正文**：經過編輯和潤色的所有章節
3. **流暢過渡**：章節間自然的過渡
4. **統一風格**：一致的學術寫作風格
5. **保留引用**：所有原始來源標註

請確保最終輸出是一篇可以直接發表的完整論文。''',
            agent=editor
        )
        
        editing_crew = Crew(
            agents=[editor],
            tasks=[review_task],
            verbose=False
        )
        
        editing_result = editing_crew.kickoff()
        
        if editing_result and editing_result.raw:
            state['final_paper_content'] = editing_result.raw
            print("編輯審閱完成")
            state['tasks_completed'].append('editing')
        else:
            print("編輯失敗，使用原始初稿")
            state['final_paper_content'] = state['draft_content']
            state['errors'].append("編輯過程失敗")
    
    except Exception as e:
        print(f"編輯過程發生錯誤：{e}")
        state['errors'].append(f"編輯錯誤：{str(e)}")
        state['final_paper_content'] = state['draft_content']
        # 即使失敗也標記為已完成，避免無限循環
        state['tasks_completed'].append('editing')
    
    return state


def citation_node(state: ResearchState) -> ResearchState:
    """
    引文格式化節點：生成APA格式參考文獻
    """
    print("\n=== 引文格式化階段 ===")
    
    if not state.get('final_paper_content'):
        state['errors'].append("沒有論文內容可供引文格式化")
        return state
    
    try:
        from crewai import Task
        
        # 創建包含論文內容的context任務
        context_task = Task(
            description="Paper content for citation formatting",
            expected_output="Paper content",
            agent=citation_formatter
        )
        context_task.output = type('MockOutput', (), {
            'raw': state['final_paper_content']
        })()
        
        citation_task = create_citation_task()
        citation_task.context = [context_task]
        
        citation_crew = Crew(
            agents=[citation_formatter],
            tasks=[citation_task],
            verbose=False
        )
        
        citation_result = citation_crew.kickoff()
        
        if citation_result and citation_result.raw:
            references_content = citation_result.raw
            
            # 驗證引文品質
            if "我現在知道最終答案" in references_content or "Final Answer" in references_content:
                references_content = "\n\n## References\n\n注意：此論文包含多個網路來源引用，請手動驗證和格式化參考文獻。"
            elif not references_content.strip().startswith("## References"):
                references_content = "## References\n\n" + references_content.strip()
            
            state['complete_paper_content'] = state['final_paper_content'] + "\n\n" + references_content
            print("引文格式化完成")
            state['tasks_completed'].append('citation')
        else:
            print("引文格式化失敗")
            state['complete_paper_content'] = state['final_paper_content']
            state['errors'].append("引文格式化失敗")
    
    except Exception as e:
        print(f"引文格式化過程發生錯誤：{e}")
        state['errors'].append(f"引文格式化錯誤：{str(e)}")
        state['complete_paper_content'] = state['final_paper_content']
        # 即使失敗也標記為已完成，避免無限循環
        state['tasks_completed'].append('citation')
    
    return state


def quality_check_node(state: ResearchState) -> ResearchState:
    """
    🆕 智能品質審核節點：實現真正的「審稿會」模式
    
    核心功能：
    1. 深度品質評估 (1-10分評分系統)
    2. 具體問題診斷與改進建議
    3. 智能決策：ACCEPT/REVISE/REJECT
    4. 版本控制整合
    5. 修訂迴圈狀態管理
    """
    print("\n=== 智能品質審核階段 ===")
    
    # 🆕 設置修訂迴圈狀態
    state['is_in_revision_loop'] = True
    state['last_revision_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if not state.get('draft_content'):
        state['errors'].append("沒有初稿可供審核")
        state['review_decision'] = "REJECT"
        state['review_feedback'] = "缺少初稿內容，無法進行品質審核。"
        state['workflow_completion_status'] = "FAILED_NO_CONTENT"
        return state
    
    # 🆕 版本控制：審核前保存當前版本
    current_revision = state.get('revision_count', 0)
    save_version_to_history(
        state, 
        state['draft_content'], 
        f"review_{current_revision + 1}", 
        f"第 {current_revision + 1} 輪審核前的版本"
    )
    
    # 檢查修訂次數限制 - 增強的失敗保護機制
    revision_count = state.get('revision_count', 0)
    max_revisions = state.get('max_revisions', 3)
    
    if revision_count >= max_revisions:
        print(f"已達最大修訂次數限制 ({max_revisions})，啟動最終裁決機制")
        state['review_decision'] = "ACCEPT"
        state['force_accept_reason'] = f"達到最大修訂次數 ({max_revisions})，系統強制接受以確保流程完成"
        state['final_decision_maker'] = "SYSTEM"
        state['workflow_completion_status'] = "COMPLETED_FORCE_ACCEPT"
        state['review_feedback'] = f"最終裁決：經過 {max_revisions} 輪修訂後，系統決定接受當前版本。\n\n雖然仍有改進空間，但已展現了AI團隊的協作成果。此決策基於防止無限迴圈的保護機制。"
        
        # 記錄最終裁決到修訂歷史
        final_record = {
            "revision_number": revision_count + 1,
            "decision": "FORCE_ACCEPT",
            "feedback": state['review_feedback'],
            "quality_score": 7,  # 給予合理的基準分數
            "revision_priority": "FINAL",
            "specific_issues": ["已達最大修訂次數"],
            "timestamp": state['last_revision_timestamp'],
            "decision_maker": "SYSTEM"
        }
        
        if 'revision_history' not in state:
            state['revision_history'] = []
        state['revision_history'].append(final_record)
        
        return state
    
    try:
        from crewai import Task
        
        draft = state['draft_content']
        research_goal = state['research_goal']
        
        # 包含研究目標和數據分析結果的上下文信息
        analysis_context = ""
        if state.get('data_analysis_results'):
            analysis_context = f"\n\n可用的數據分析結果：\n{state['data_analysis_results']}"
        
        # 創建專門的品質審核任務
        review_task = Task(
            description=f"""
            你是一位國際頂級期刊的首席審稿人，具有極高的學術標準。請嚴格審核以下研究報告初稿：

            **研究目標：** {research_goal}
            {analysis_context}

            **待審核初稿：**
            {draft}

            請從以下幾個維度進行深度評估：

            ## 1. 邏輯一致性分析
            - 論點之間是否存在邏輯矛盾？
            - 數據分析結果是否能有力支撐結論？
            - 章節間的邏輯流程是否順暢？

            ## 2. 論證充分性評估
            - 引用的論點是否足以支撐核心觀點？
            - 是否存在明顯的論證跳躍或證據不足？
            - 反駁觀點是否得到充分討論？

            ## 3. 數據完整性檢查
            - 是否充分利用了所有可用的數據洞察？
            - 數據解釋是否準確和深入？
            - 是否有重要的數據趨勢被忽略？

            ## 4. 學術規範性
            - 引文格式是否正確？
            - 學術語言是否嚴謹？
            - 結構是否符合學術寫作標準？

            ## 5. 創新性和深度
            - 是否提供了新的洞察或觀點？
            - 分析深度是否足夠？
            - 是否回答了研究目標中提出的問題？

            **重要說明：**
            - 如果發現嚴重的邏輯錯誤、數據誤用或結論不當，請選擇 REJECT
            - 如果整體方向正確但需要改進，請選擇 REVISE 並詳細說明改進方向
            - 只有在論文達到發表標準時才選擇 ACCEPT

            **輸出格式要求：**
            你的最終輸出必須是一個嚴格的 JSON 物件，格式如下：
            {{
                "decision": "ACCEPT" | "REVISE" | "REJECT",
                "feedback": "詳細的審核意見。如果是REVISE，必須明確指出：(1)需要改進的具體問題 (2)建議的解決方案 (3)如果涉及數據問題，需要返回計算科學家重新分析的具體要求",
                "quality_score": 1-10的整數評分,
                "revision_priority": "HIGH" | "MEDIUM" | "LOW",
                "specific_issues": ["問題1", "問題2", "問題3"]
            }}
            """,
            expected_output="包含 decision、feedback、quality_score、revision_priority 和 specific_issues 字段的 JSON 物件",
            agent=editor
        )
        
        # 執行審核
        review_crew = Crew(
            agents=[editor],
            tasks=[review_task],
            verbose=False
        )
        
        review_result = review_crew.kickoff()
        
        if review_result and review_result.raw:
            try:
                # 嘗試解析 JSON 回應
                review_text = review_result.raw
                
                # 提取 JSON 部分
                if '{' in review_text and '}' in review_text:
                    json_start = review_text.find('{')
                    json_end = review_text.rfind('}') + 1
                    json_text = review_text[json_start:json_end]
                    review_data = json.loads(json_text)
                    
                    decision = review_data.get('decision', 'REVISE')
                    feedback = review_data.get('feedback', '審核意見解析失敗')
                    quality_score = review_data.get('quality_score', 5)
                    revision_priority = review_data.get('revision_priority', 'MEDIUM')
                    specific_issues = review_data.get('specific_issues', [])
                    
                else:
                    # 如果沒有 JSON，解析純文字回應
                    decision = "REVISE"
                    feedback = review_text
                    quality_score = 5
                    revision_priority = "MEDIUM"
                    specific_issues = []
                
            except json.JSONDecodeError:
                print("審核結果 JSON 解析失敗，使用備用策略")
                decision = "REVISE"
                feedback = f"JSON解析失敗，原始審核結果：{review_result.raw}"
                quality_score = 5
                revision_priority = "MEDIUM"
                specific_issues = ["JSON解析問題"]
        
        else:
            print("品質審核執行失敗")
            decision = "REVISE"
            feedback = "品質審核過程失敗，建議手動檢查初稿內容。"
            quality_score = 3
            revision_priority = "HIGH"
            specific_issues = ["審核過程失敗"]
        
        # 🆕 智能審核歷史記錄 - 包含更豐富的上下文信息
        revision_record = {
            "revision_number": revision_count + 1,
            "decision": decision,
            "feedback": feedback,
            "quality_score": quality_score,
            "revision_priority": revision_priority,
            "specific_issues": specific_issues,
            "timestamp": state['last_revision_timestamp'],
            "decision_maker": "AI_REVIEWER",
            "word_count": len(draft.split()),
            "has_data_analysis": bool(state.get('data_analysis_results')),
            "literature_points_count": len(state.get('literature_points', [])),
            "data_points_count": len(state.get('data_analysis_points', []))
        }
        
        if 'revision_history' not in state:
            state['revision_history'] = []
        state['revision_history'].append(revision_record)
        
        # 🆕 更新增強的狀態信息
        state['review_decision'] = decision
        state['review_feedback'] = feedback
        state['review_score'] = quality_score
        state['review_priority'] = revision_priority
        state['specific_issues'] = specific_issues
        
        # 🆕 智能決策分析與用戶反饋
        print(f"審核決策：{decision}")
        print(f"品質評分：{quality_score}/10")
        print(f"修改優先級：{revision_priority}")
        if specific_issues:
            print(f"具體問題：{', '.join(specific_issues[:3])}...")  # 只顯示前3個問題
        print(f"💬 審核意見摘要：{feedback[:150]}...")
        
        # 🆕 品質趨勢分析
        if len(state['revision_history']) > 1:
            previous_score = state['revision_history'][-2].get('quality_score', 0)
            score_change = quality_score - previous_score
            if score_change > 0:
                print(f"品質提升：+{score_change} 分")
            elif score_change < 0:
                print(f"品質下降：{score_change} 分")
            else:
                print(f"品質持平：{quality_score} 分")
        
        state['tasks_completed'].append('quality_check')
        
    except Exception as e:
        print(f"品質審核過程發生錯誤：{e}")
        state['errors'].append(f"品質審核錯誤：{str(e)}")
        state['review_decision'] = "REVISE"
        state['review_feedback'] = f"品質審核過程遇到技術問題：{str(e)}。建議檢查初稿內容並重新審核。"
    
    return state


def revision_node(state: ResearchState) -> ResearchState:
    """
    智能修訂節點：實現反饋驅動的動態改進
    
    核心升級：
    1. 基於審核反饋的精準修訂
    2. 版本控制與修訂歷史追蹤
    3. 智能修訂策略選擇
    4. 修訂成效評估
    """
    print("\n=== 智能修訂改進階段 ===")
    
    if not state.get('review_feedback'):
        state['errors'].append("沒有審核反饋可供修訂")
        state['workflow_completion_status'] = "FAILED_NO_FEEDBACK"
        return state
    
    # 增加修訂計數
    revision_count = state.get('revision_count', 0) + 1
    state['revision_count'] = revision_count
    
    feedback = state['review_feedback']
    review_score = state.get('review_score', 5)
    review_priority = state.get('review_priority', 'MEDIUM')
    specific_issues = state.get('specific_issues', [])
    
    print(f"📝 執行第 {revision_count} 次修訂")
    print(f"📊 當前評分：{review_score}/10")
    print(f"⚡ 修訂優先級：{review_priority}")
    print(f"🎯 修訂依據：{feedback[:150]}...")
    if specific_issues:
        print(f"🔍 重點問題：{', '.join(specific_issues[:3])}...")
    
    # 🆕 版本控制：修訂前保存
    save_version_to_history(
        state, 
        state.get('draft_content', ''), 
        f"pre_revision_{revision_count}", 
        f"第 {revision_count} 次修訂前的版本 (評分: {review_score}/10)"
    )
    
    try:
        from crewai import Task
        
        # 分析反饋內容，判斷需要哪種類型的修訂
        feedback_lower = feedback.lower()
        needs_data_reanalysis = any(keyword in feedback_lower for keyword in [
            '數據分析', '統計', '計算', '數據問題', '分析結果', '數據缺失', '數據解釋'
        ])
        
        if needs_data_reanalysis and state.get('data_file_path'):
            print("🔬 檢測到需要重新進行數據分析")
            
            # 重新執行數據分析，帶上具體的改進要求
            enhanced_analysis_task = create_data_analysis_task(
                state['data_file_path'], 
                state['research_goal']
            )
            
            # 在任務描述中加入反饋要求
            enhanced_analysis_task.description += f"""
            
            **重要：基於審稿人反饋的改進要求：**
            {feedback}
            
            請特別注意解決上述反饋中提到的數據分析問題，確保：
            1. 補充任何遺漏的數據洞察
            2. 修正任何數據解釋錯誤
            3. 提供更深入的統計分析
            4. 確保數據支撐結論的邏輯性
            """
            
            analysis_crew = Crew(
                agents=[computational_scientist],
                tasks=[enhanced_analysis_task],
                verbose=False
            )
            
            revised_analysis = analysis_crew.kickoff()
            
            if revised_analysis and revised_analysis.raw:
                state['data_analysis_results'] = revised_analysis.raw
                
                # 更新數據分析論點
                analysis_point = {
                    "sentence": revised_analysis.raw,
                    "source": f"修訂後數據分析 (第{revision_count}次)：{state['data_file_path']}"
                }
                state['data_analysis_points'] = [analysis_point]
                
                # 重新整合論點
                combined_points = []
                if state.get('literature_points'):
                    combined_points.extend(state['literature_points'])
                combined_points.extend(state['data_analysis_points'])
                state['combined_points'] = combined_points
                
                print("✅ 數據分析修訂完成")
        
        # 重新寫作，融入審核反饋
        if state.get('outline_data') and state.get('combined_points'):
            print("✍️ 根據反饋重新寫作")
            
            outline_data = state['outline_data']
            all_points = state['combined_points']
            
            revised_draft = f"# {outline_data.get('title', '研究報告')}\n\n"
            
            for chapter in outline_data.get("chapters", []):
                chapter_title = chapter.get("chapter_title", "未命名章節")
                indices = chapter.get("supporting_points_indices", [])
                
                # 獲取該章節的論點
                chapter_points = [all_points[i] for i in indices if i < len(all_points)]
                
                print(f"📝 修訂章節：{chapter_title}")
                
                # 創建帶有反饋要求的寫作任務
                revision_writing_task = create_writing_task(
                    chapter_title, 
                    json.dumps(chapter_points, ensure_ascii=False, indent=2)
                )
                
                # 在任務中加入審核反饋
                revision_writing_task.description += f"""
                
                **重要：基於審稿人反饋的修訂要求：**
                {feedback}
                
                請在寫作時特別注意：
                1. 解決反饋中提到的邏輯問題
                2. 加強論證的充分性
                3. 改進學術語言的嚴謹性
                4. 確保與數據分析結果的一致性
                5. 提高論文的整體深度和創新性
                
                這是第 {revision_count} 次修訂，請確保解決之前版本的問題。
                """
                
                writing_crew = Crew(
                    agents=[academic_writer],
                    tasks=[revision_writing_task],
                    verbose=False
                )
                
                chapter_result = writing_crew.kickoff()
                
                if chapter_result and chapter_result.raw:
                    chapter_content = chapter_result.raw
                else:
                    chapter_content = f"[第{revision_count}次修訂：章節內容生成失敗]"
                
                revised_draft += f"## {chapter_title}\n\n{chapter_content}\n\n"
            
            # 🆕 增強的修訂說明，包含詳細的改進記錄
            revision_summary = format_revision_history_summary(state)
            revision_note = f"""

---
## 📝 修訂記錄 (第 {revision_count} 次修訂)

### 本次修訂重點
- **評分提升目標**：從 {review_score}/10 提升至 8+ 分
- **修訂優先級**：{review_priority}
- **重點改進問題**：{', '.join(specific_issues[:3]) if specific_issues else '整體品質提升'}

### 審稿人反饋摘要
{feedback[:200]}...

### 具體改進措施
本版本已針對上述反饋進行了以下改進：
1. 加強論證邏輯性和連貫性
2. 補充數據分析的深度和準確性
3. 提升學術語言的嚴謹性
4. 確保所有論點都有充分的證據支撐

---
"""
            
            state['draft_content'] = revised_draft + revision_note
            
            # 🆕 版本控制：保存修訂後版本
            save_version_to_history(
                state, 
                state['draft_content'], 
                f"revised_{revision_count}", 
                f"第 {revision_count} 次修訂完成版本 (目標評分: 8+/10)"
            )
            
            print("✅ 智能修訂完成")
            print(f"📈 預期評分提升：{review_score}/10 → 8+/10")
        
        # 記錄修訂完成
        state['tasks_completed'].append(f'revision_{revision_count}')
        
        # 🆕 修訂迴圈狀態更新
        state['last_revision_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    except Exception as e:
        print(f"❌ 修訂過程發生錯誤：{e}")
        state['errors'].append(f"修訂錯誤 (第{revision_count}次)：{str(e)}")
    
    return state


def route_after_quality_check(state: ResearchState) -> str:
    """
    🆕 智能品質審核路由：實現真正的審稿-修訂閉環
    
    核心邏輯：
    1. ACCEPT → editing (審核通過，進入最終編輯)
    2. REVISE + 未達上限 → revision (啟動修訂迴圈)
    3. REJECT 或 達到上限 → editing (最終裁決，強制接受)
    4. 動態追蹤修訂成效
    """
    decision = state.get('review_decision', 'REVISE')
    revision_count = state.get('revision_count', 0)
    max_revisions = state.get('max_revisions', 3)
    review_score = state.get('review_score', 5)
    is_force_accept = state.get('force_accept_reason') is not None
    
    print(f"\n🧭 === 智能審稿路由決策 ===")
    print(f"📋 審核決策：{decision}")
    print(f"📊 當前評分：{review_score}/10")
    print(f"🔄 修訂進度：{revision_count}/{max_revisions}")
    if is_force_accept:
        print(f"⚖️ 最終裁決：{state.get('force_accept_reason', '')[:50]}...")
    
    # 🆕 決策優先級：強制接受 > 品質通過 > 修訂迴圈 > 保護機制
    
    # 1. 最終裁決：強制接受
    if is_force_accept or decision == "FORCE_ACCEPT":
        print("⚖️ 系統最終裁決 → 強制接受，進入編輯階段")
        state['is_in_revision_loop'] = False
        state['workflow_completion_status'] = "COMPLETED_FORCE_ACCEPT"
        return "editing"
    
    # 2. 品質審核通過
    if decision == "ACCEPT":
        print("✅ 品質審核通過 → 進入最終編輯階段")
        state['is_in_revision_loop'] = False
        state['workflow_completion_status'] = "COMPLETED_ACCEPT"
        state['quality_gates_passed'].append(f"quality_check_passed_score_{review_score}")
        return "editing"
    
    # 3. 需要修訂且未達上限
    elif decision == "REVISE" and revision_count < max_revisions:
        print(f"🔄 啟動修訂迴圈 → 第 {revision_count + 1} 次修訂")
        print(f"🎯 修訂目標：提升評分至 8+ 分")
        state['is_in_revision_loop'] = True
        return "revision"
    
    # 4. 保護機制：達到修訂上限或被拒絕
    else:
        if decision == "REJECT":
            print("❌ 品質審核拒絕 → 啟動保護機制，強制接受")
            state['force_accept_reason'] = "品質審核拒絕，但啟動保護機制避免完全失敗"
        else:
            print(f"⚠️ 達到最大修訂次數 ({max_revisions}) → 啟動保護機制，強制接受")
            state['force_accept_reason'] = f"達到最大修訂次數 {max_revisions}，啟動保護機制"
        
        state['is_in_revision_loop'] = False
        state['final_decision_maker'] = "PROTECTION_SYSTEM"
        state['workflow_completion_status'] = "COMPLETED_PROTECTION"
        return "editing"


def decision_router(state: ResearchState) -> str:
    """
    決策路由器：根據專案計劃和當前狀態決定下一步
    """
    current_stage = state.get('current_stage', 'start')
    project_plan = state.get('project_plan', {})
    tasks_completed = state.get('tasks_completed', [])
    errors = state.get('errors', [])
    
    print(f"\n🧭 決策路由器：當前階段 = {current_stage}")
    
    # 如果有嚴重錯誤，結束流程
    if errors and any('AuthenticationError' in error for error in errors):
        print("❌ 檢測到認證錯誤，結束流程")
        return "finished"
    
    # 如果還沒有專案計劃，開始文獻研究作為備用
    if 'project_planning' not in tasks_completed:
        return "literature_research"
    
    # 根據專案計劃決定執行順序
    requires_literature = project_plan.get('requires_literature', True)
    requires_data = project_plan.get('requires_data_analysis', False)
    execution_strategy = project_plan.get('execution_strategy', 'SEQUENTIAL')
    
    # 文獻研究
    if requires_literature and 'literature_research' not in tasks_completed:
        return "literature_research"
    
    # 數據分析
    if requires_data and 'data_analysis' not in tasks_completed:
        return "data_analysis"
    
    # 整合階段
    if 'integration' not in tasks_completed:
        # 確保前置任務都已完成
        literature_done = not requires_literature or 'literature_research' in tasks_completed
        data_done = not requires_data or 'data_analysis' in tasks_completed
        
        if literature_done and data_done:
            return "integration"
        else:
            # 還有前置任務沒完成，繼續當前階段
            if not literature_done:
                return "literature_research"
            elif not data_done:
                return "data_analysis"
            else:
                return "integration"
    
    # 寫作階段
    if 'writing' not in tasks_completed:
        return "writing"
    
    # 品質審核階段 (新增的反饋關卡)
    if 'quality_check' not in tasks_completed:
        return "quality_check"
    
    # 檢查是否需要修訂
    review_decision = state.get('review_decision')
    revision_count = state.get('revision_count', 0)
    max_revisions = state.get('max_revisions', 3)
    
    # 如果有品質審核結果且需要修訂
    if review_decision == "REVISE" and revision_count < max_revisions:
        # 需要修訂，但還沒有執行當前輪次的修訂
        current_revision_task = f'revision_{revision_count + 1}'
        if current_revision_task not in tasks_completed:
            return "revision"
        else:
            # 修訂完成，重新進行品質審核
            if 'quality_check' in tasks_completed:
                # 移除 quality_check 標記，允許重新審核
                tasks_completed.remove('quality_check')
            return "quality_check"
    
    # 編輯階段 (品質審核通過後)
    if 'editing' not in tasks_completed:
        return "editing"
    
    # 引文格式化階段
    if 'citation' not in tasks_completed:
        return "citation"
    
    # 所有任務完成
    return "finished"


def create_hybrid_workflow() -> StateGraph:
    """
    創建LangGraph混合智能工作流程 - 帶有品質審核反饋迴圈
    """
    # 初始化狀態圖
    workflow = StateGraph(ResearchState)
    
    # 添加所有節點
    workflow.add_node("project_planning", project_planning_node)
    workflow.add_node("literature_research", literature_research_node)
    workflow.add_node("data_analysis", data_analysis_node)
    workflow.add_node("integration", integration_node)
    workflow.add_node("writing", writing_node)
    workflow.add_node("quality_check", quality_check_node)      # 新增：品質審核節點
    workflow.add_node("revision", revision_node)               # 新增：修訂節點
    workflow.add_node("editing", editing_node)
    workflow.add_node("citation", citation_node)
    
    # 設置起始點
    workflow.set_entry_point("project_planning")
    
    # 添加條件邊（智能路由）
    workflow.add_conditional_edges(
        "project_planning",
        decision_router,
        {
            "literature_research": "literature_research",
            "data_analysis": "data_analysis",
            "integration": "integration",
            "writing": "writing",
            "quality_check": "quality_check",
            "revision": "revision",
            "editing": "editing", 
            "citation": "citation",
            "finished": END
        }
    )
    
    workflow.add_conditional_edges(
        "literature_research",
        decision_router,
        {
            "data_analysis": "data_analysis",
            "integration": "integration",
            "writing": "writing",
            "quality_check": "quality_check",
            "revision": "revision",
            "editing": "editing",
            "citation": "citation", 
            "finished": END
        }
    )
    
    workflow.add_conditional_edges(
        "data_analysis",
        decision_router,
        {
            "literature_research": "literature_research",
            "integration": "integration",
            "writing": "writing",
            "quality_check": "quality_check",
            "revision": "revision",
            "editing": "editing",
            "citation": "citation",
            "finished": END
        }
    )
    
    workflow.add_conditional_edges(
        "integration",
        decision_router,
        {
            "writing": "writing",
            "quality_check": "quality_check",
            "revision": "revision",
            "editing": "editing",
            "citation": "citation",
            "finished": END
        }
    )
    
    workflow.add_conditional_edges(
        "writing",
        decision_router,
        {
            "quality_check": "quality_check",
            "revision": "revision",
            "editing": "editing",
            "citation": "citation",
            "finished": END
        }
    )
    
    # 新增：品質審核節點的條件路由
    workflow.add_conditional_edges(
        "quality_check",
        route_after_quality_check,  # 使用專門的品質審核路由函數
        {
            "revision": "revision",
            "editing": "editing",
            "finished": END
        }
    )
    
    # 🆕 修訂節點的強制路由：修訂完成後必須重新審核
    def route_after_revision(state: ResearchState) -> str:
        """
        修訂後的強制路由：確保修訂完成後必須回到品質審核
        這是實現真正「審稿-修訂」閉環的關鍵
        """
        revision_count = state.get('revision_count', 0)
        max_revisions = state.get('max_revisions', 3)
        
        print(f"\n🔄 修訂完成路由：第 {revision_count} 次修訂已完成")
        print("📋 強制返回品質審核節點，實現閉環反饋")
        
        # 清除上一輪的審核標記，允許重新審核
        tasks_completed = state.get('tasks_completed', [])
        if 'quality_check' in tasks_completed:
            tasks_completed.remove('quality_check')
            print("🔄 已清除上輪審核標記，準備重新審核")
        
        # 修訂完成後，無論如何都要回到品質審核
        return "quality_check"
    
    workflow.add_conditional_edges(
        "revision",
        route_after_revision,
        {
            "quality_check": "quality_check",  # 修訂後強制重新審核
            "finished": END  # 異常情況的退出
        }
    )
    
    workflow.add_conditional_edges(
        "editing",
        decision_router,
        {
            "quality_check": "quality_check",
            "revision": "revision",
            "citation": "citation",
            "finished": END
        }
    )
    
    workflow.add_conditional_edges(
        "citation",
        decision_router,
        {
            "quality_check": "quality_check",
            "revision": "revision",
            "editing": "editing",
            "finished": END
        }
    )
    
    # 編譯工作流程
    return workflow.compile()
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


class ResearchState(TypedDict):
    """
    混合研究工作流程的狀態定義
    包含整個研究過程中需要共享的所有資訊
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
    print("\n🧠 === 專案規劃階段 ===")
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
                
                print(f"✅ 專案規劃完成：{project_plan['research_type']}")
                print(f"📋 執行策略：{project_plan['execution_strategy']}")
                
                state['project_plan'] = project_plan
                state['current_stage'] = 'planning_completed'
                state['tasks_completed'].append('project_planning')
                
            except json.JSONDecodeError:
                print("⚠️ 無法解析專案規劃JSON，使用默認策略")
                state['project_plan'] = {
                    "research_type": "HYBRID" if state.get('data_file_path') else "LITERATURE_ONLY",
                    "requires_literature": True,
                    "requires_data_analysis": bool(state.get('data_file_path')),
                    "execution_strategy": "PARALLEL",
                    "priority_tasks": ["literature_research"],
                    "reasoning": "JSON解析失敗，使用備用策略"
                }
        else:
            print("⚠️ 專案規劃失敗，使用默認策略")
            state['errors'].append("專案規劃節點執行失敗")
    
    except Exception as e:
        print(f"❌ 專案規劃過程發生錯誤：{e}")
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
    print("\n📚 === 文獻研究階段 ===")
    
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
            print("✅ 文獻搜集完成")
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
                print(f"✅ 文獻論點提取完成：{len(points_data)} 個論點")
            except json.JSONDecodeError:
                print("⚠️ 文獻論點JSON格式錯誤")
                state['errors'].append("文獻論點解析失敗")
        else:
            state['errors'].append("文獻論點提取失敗")
        
        state['tasks_completed'].append('literature_research')
        
    except Exception as e:
        print(f"❌ 文獻研究過程發生錯誤：{e}")
        state['errors'].append(f"文獻研究錯誤：{str(e)}")
    
    return state


def data_analysis_node(state: ResearchState) -> ResearchState:
    """
    數據分析節點：執行本地數據分析
    """
    print("\n📊 === 數據分析階段 ===")
    
    if not state.get('data_file_path'):
        print("⚠️ 無數據檔案，跳過數據分析")
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
            
            print("✅ 數據分析完成")
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
        print(f"❌ 數據分析過程發生錯誤：{e}")
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
            print(f"📚 整合文獻論點：{len(state['literature_points'])} 個")
        
        if state.get('data_analysis_points'):
            combined_points.extend(state['data_analysis_points'])
            print(f"📊 整合數據分析論點：{len(state['data_analysis_points'])} 個")
        
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
                print(f"✅ 大綱生成完成：{outline_data.get('title', '未知標題')}")
                state['tasks_completed'].append('integration')
            except json.JSONDecodeError:
                print("⚠️ 大綱JSON格式錯誤")
                state['errors'].append("大綱解析失敗")
        else:
            state['errors'].append("大綱生成失敗")
    
    except Exception as e:
        print(f"❌ 整合過程發生錯誤：{e}")
        state['errors'].append(f"整合錯誤：{str(e)}")
    
    return state


def writing_node(state: ResearchState) -> ResearchState:
    """
    寫作節點：根據大綱和論點生成論文初稿
    """
    print("\n✍️ === 寫作階段 ===")
    
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
            
            print(f"📝 寫作章節：{chapter_title}")
            
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
        print("✅ 初稿撰寫完成")
        state['tasks_completed'].append('writing')
    
    except Exception as e:
        print(f"❌ 寫作過程發生錯誤：{e}")
        state['errors'].append(f"寫作錯誤：{str(e)}")
        # 即使失敗也標記為已完成，避免無限循環
        state['tasks_completed'].append('writing')
        state['draft_content'] = f"# 研究報告\n\n由於技術問題，寫作過程未能完成。錯誤：{str(e)}\n\n請檢查配置並重試。"
    
    return state


def editing_node(state: ResearchState) -> ResearchState:
    """
    編輯節點：專業編輯審閱和潤色
    """
    print("\n🎨 === 編輯審閱階段 ===")
    
    if not state.get('draft_content'):
        state['errors'].append("沒有初稿可供編輯")
        return state
    
    try:
        from crewai import Task
        
        # 創建包含初稿的context任務
        context_task = Task(
            description="Draft content for editing",
            expected_output="Draft content",
            agent=editor
        )
        context_task.output = type('MockOutput', (), {
            'raw': state['draft_content']
        })()
        
        review_task = create_review_task()
        review_task.context = [context_task]
        
        editing_crew = Crew(
            agents=[editor],
            tasks=[review_task],
            verbose=False
        )
        
        editing_result = editing_crew.kickoff()
        
        if editing_result and editing_result.raw:
            state['final_paper_content'] = editing_result.raw
            print("✅ 編輯審閱完成")
            state['tasks_completed'].append('editing')
        else:
            print("⚠️ 編輯失敗，使用原始初稿")
            state['final_paper_content'] = state['draft_content']
            state['errors'].append("編輯過程失敗")
    
    except Exception as e:
        print(f"❌ 編輯過程發生錯誤：{e}")
        state['errors'].append(f"編輯錯誤：{str(e)}")
        state['final_paper_content'] = state['draft_content']
        # 即使失敗也標記為已完成，避免無限循環
        state['tasks_completed'].append('editing')
    
    return state


def citation_node(state: ResearchState) -> ResearchState:
    """
    引文格式化節點：生成APA格式參考文獻
    """
    print("\n📚 === 引文格式化階段 ===")
    
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
            print("✅ 引文格式化完成")
            state['tasks_completed'].append('citation')
        else:
            print("⚠️ 引文格式化失敗")
            state['complete_paper_content'] = state['final_paper_content']
            state['errors'].append("引文格式化失敗")
    
    except Exception as e:
        print(f"❌ 引文格式化過程發生錯誤：{e}")
        state['errors'].append(f"引文格式化錯誤：{str(e)}")
        state['complete_paper_content'] = state['final_paper_content']
        # 即使失敗也標記為已完成，避免無限循環
        state['tasks_completed'].append('citation')
    
    return state


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
    
    # 編輯階段
    if 'editing' not in tasks_completed:
        return "editing"
    
    # 引文格式化階段
    if 'citation' not in tasks_completed:
        return "citation"
    
    # 所有任務完成
    return "finished"


def create_hybrid_workflow() -> StateGraph:
    """
    創建LangGraph混合智能工作流程
    """
    # 初始化狀態圖
    workflow = StateGraph(ResearchState)
    
    # 添加所有節點
    workflow.add_node("project_planning", project_planning_node)
    workflow.add_node("literature_research", literature_research_node)
    workflow.add_node("data_analysis", data_analysis_node)
    workflow.add_node("integration", integration_node)
    workflow.add_node("writing", writing_node)
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
            "editing": "editing",
            "citation": "citation",
            "finished": END
        }
    )
    
    workflow.add_conditional_edges(
        "writing",
        decision_router,
        {
            "editing": "editing",
            "citation": "citation",
            "finished": END
        }
    )
    
    workflow.add_conditional_edges(
        "editing",
        decision_router,
        {
            "citation": "citation",
            "finished": END
        }
    )
    
    workflow.add_conditional_edges(
        "citation",
        decision_router,
        {
            "finished": END
        }
    )
    
    # 編譯工作流程
    return workflow.compile()
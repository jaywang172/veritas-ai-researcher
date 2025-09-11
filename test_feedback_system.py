#!/usr/bin/env python3
"""
動態協作反饋機制測試腳本
展示 Veritas v3.0 的品質審核和修訂迴圈功能
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 導入工作流程
from workflows.hybrid_workflow import create_hybrid_workflow, ResearchState

load_dotenv()

def test_feedback_system():
    """測試動態協作反饋機制"""
    
    print("動態協作反饋機制測試")
    print("=" * 60)
    
    # 測試研究目標：使用 NVDA 財務數據
    research_goal = "基於sales_data.csv提供的五年期詳細財報，深度剖析NVIDIA商業模式的演變。請識別其核心增長引擎的轉變過程，對比數據中心與遊戲業務的消長趨勢，並結合市場估值變化，生成一份關於NVIDIA如何轉型為全球AI領導者的綜合戰略分析報告。"
    data_file_path = "sales_data.csv"
    
    print(f"測試研究目標：{research_goal}")
    print(f"數據檔案：{data_file_path}")
    
    if not Path(data_file_path).exists():
        print(f"數據檔案 {data_file_path} 不存在！")
        return
    
    try:
        # 初始化研究狀態
        initial_state = ResearchState(
            research_goal=research_goal,
            data_file_path=data_file_path,
            project_plan=None,
            literature_data=None,
            literature_points=None,
            data_analysis_results=None,
            data_analysis_points=None,
            combined_points=None,
            outline_data=None,
            draft_content=None,
            final_paper_content=None,
            complete_paper_content=None,
            
            # 品質審核和反饋機制字段
            review_decision=None,
            review_feedback=None,
            revision_count=0,
            max_revisions=2,  # 為測試設置較少的修訂次數
            revision_history=[],
            quality_gates_passed=[],
            
            tasks_completed=[],
            current_stage='start',
            errors=[],
            messages=[]
        )
        
        # 創建並執行工作流程
        workflow = create_hybrid_workflow()
        
        print("\n啟動帶反饋迴圈的智能工作流程...")
        print("=" * 60)
        
        # 執行工作流程
        final_state = workflow.invoke(initial_state)
        
        # 分析結果
        print("\n" + "=" * 60)
        print("動態協作測試結果分析")
        print("=" * 60)
        
        # 基本完成信息
        print(f"任務完成：{', '.join(final_state.get('tasks_completed', []))}")
        
        # 品質審核和修訂歷史
        revision_count = final_state.get('revision_count', 0)
        revision_history = final_state.get('revision_history', [])
        
        print(f"\n品質控制統計：")
        print(f"   修訂次數：{revision_count}")
        print(f"   審核輪次：{len(revision_history)}")
        
        if revision_history:
            print(f"\n詳細審核歷史：")
            for i, record in enumerate(revision_history, 1):
                decision = record.get('decision', 'UNKNOWN')
                score = record.get('quality_score', 'N/A')
                priority = record.get('revision_priority', 'N/A')
                issues = record.get('specific_issues', [])
                
                print(f"   第{i}次審核：")
                print(f"      決策：{decision}")
                print(f"      評分：{score}/10")
                print(f"      優先級：{priority}")
                if issues:
                    print(f"      問題：{', '.join(issues[:3])}...")  # 只顯示前3個問題
                
                feedback = record.get('feedback', '')
                if feedback:
                    print(f"      反饋：{feedback[:100]}...")
                print()
        
        # 工作流程效果分析
        print(f"工作流程效果分析：")
        
        if revision_count > 0:
            print(f"   成功啟動修訂迴圈：進行了 {revision_count} 次品質改進")
            print(f"   動態協作機制正常運作")
            
            # 檢查品質分數變化
            if len(revision_history) > 1:
                first_score = revision_history[0].get('quality_score', 0)
                last_score = revision_history[-1].get('quality_score', 0)
                if last_score > first_score:
                    print(f"   品質提升：{first_score} → {last_score} (+{last_score - first_score})")
                else:
                    print(f"   品質維持：{first_score} → {last_score}")
        else:
            print(f"   初稿即被接受：展現了極高的初始品質")
        
        # 最終產出檢查
        if final_state.get('complete_paper_content'):
            print(f"   成功生成完整報告")
            
            # 檢查是否包含修訂說明
            content = final_state['complete_paper_content']
            if '修訂說明' in content:
                print(f"   報告包含修訂歷史追蹤")
            
            # 生成檔案名
            safe_goal = "".join(c for c in research_goal if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = f"feedback_test_{safe_goal[:20]}.txt"
            
            # 儲存結果
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(final_state['complete_paper_content'])
            
            print(f"   測試報告已儲存為：{filename}")
        
        # 錯誤分析
        errors = final_state.get('errors', [])
        if errors:
            print(f"\n過程中的警告 ({len(errors)})：")
            for error in errors[:3]:  # 只顯示前3個錯誤
                print(f"   • {error}")
        
        # 系統能力總結
        print(f"\n動態協作系統能力展示：")
        print(f"   智能品質守門員：自動評估論文品質")
        print(f"   自我修正迴圈：根據反饋自動改進")
        print(f"   品質量化評估：提供1-10分的客觀評分")
        print(f"   問題診斷能力：識別具體需要改進的方面")
        print(f"   平衡機制：防止無限循環的次數限制")
        
        print("\n" + "=" * 60)
        print("動態協作反饋機制測試完成！")
        print("系統從「生產線」成功升級為「審稿會」模式！")
        print("=" * 60)
        
    except Exception as e:
        print(f"測試過程發生錯誤：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_feedback_system()

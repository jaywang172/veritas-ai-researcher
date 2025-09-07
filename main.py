#!/usr/bin/env python3
"""
Veritas v3.0 - 混合智能研究平台
LangGraph驅動的自主規劃與執行系統
"""

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
            tasks_completed=[],
            current_stage='start',
            errors=[],
            messages=[]
        )
        
        # 創建並執行LangGraph工作流程
        workflow = create_hybrid_workflow()
        
        print("\n🔄 啟動LangGraph智能工作流程...")
        print("=" * 60)
        
        # 執行工作流程
        final_state = workflow.invoke(initial_state)
        
        # 處理結果
        if final_state.get('complete_paper_content'):
            # 生成檔案名
            safe_goal = "".join(c for c in research_goal if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = f"veritas_v3_{safe_goal[:30]}.txt"
            
            # 儲存結果
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(final_state['complete_paper_content'])
            
            print("\n" + "=" * 60)
            print("🎉 Veritas v3.0 混合智能研究完成！".center(60))
            print("=" * 60)
            print(f"📄 研究報告已儲存為：{filename}")
            print(f"✅ 完成任務：{', '.join(final_state.get('tasks_completed', []))}")
            
            if final_state.get('project_plan'):
                research_type = final_state['project_plan'].get('research_type', 'UNKNOWN')
                print(f"🧠 研究類型：{research_type}")
            
            if final_state.get('errors'):
                print(f"⚠️ 過程中遇到 {len(final_state['errors'])} 個警告")
                
        else:
            print("\n❌ 研究流程未能完成，請檢查錯誤訊息")
            if final_state.get('errors'):
                print("錯誤列表：")
                for error in final_state['errors']:
                    print(f"  • {error}")
    
    except Exception as e:
        print(f"\n❌ 工作流程執行失敗: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Veritas Tasks - Task Definitions
Contains task definitions for the CrewAI workflow.
"""

from crewai import Task
from agents import literature_scout, synthesizer

def create_research_task(research_topic: str):
    """Create a research task for the Literature Scout Agent."""
    return Task(
        description=f"""根據研究主題「{research_topic}」，使用搜尋工具查找相關的學術文獻和研究資料。

請重點關注：
1. 最近5年內的相關研究
2. 高影響力的期刊論文
3. 系統性的文獻回顧
4. 可靠的學術來源

請提供具體的來源URL和簡要摘要。""",
        expected_output="""一個包含相關文獻來源的清單，每個來源包含：
- 標題
- 作者
- 來源URL
- 簡要摘要（2-3句）""",
        agent=literature_scout
    )

def create_summarize_task():
    """Create a summarization task for the Synthesizer Agent."""
    return Task(
        description=(
            '分析以下由文獻搜集代理人提供的研究資料，並撰寫一份全面的學術綜述。'
            '確保你的綜述能夠涵蓋資料中的主要發現、趨勢和爭議點。'
            '你的最終報告應該是一段結構完整、邏輯清晰的文字。'
            '這是你需要分析的資料：\n\n{context}'
        ),
        expected_output='一份大約3-5段的學術綜述報告，以Markdown格式呈現。',
        agent=synthesizer,
        context=[]  # This will be populated with the research task output
    )

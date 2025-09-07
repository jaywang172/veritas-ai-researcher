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
            '分析以下由文獻搜集代理人提供的原始研究資料。'
            '你的任務是從這些資料中提取核心論點，並為每一個論點找到其直接的來源URL。'
            '最終，將這些資訊整理成一個JSON陣列。'
            '這是你需要分析的原始資料：\n\n{context}'
        ),
        expected_output=(
            '一個格式嚴格的JSON字串。它應該是一個列表（array），'
            '其中每個元素都是一個包含"sentence"和"source"兩個鍵的對象（object）。'
            '例如：\'[{"sentence": "遠程工作提高了員工的自主性。", "source": "https://example.com/paper1"}, {"sentence": "混合工作模式有助於團隊協作。", "source": "https://example.com/paper2"}]\' '
            '確保整個輸出是一個單一的、可以被JSON解析器直接處理的字串。'
        ),
        agent=synthesizer,
        context=[]  # This will be populated with the research task output
    )

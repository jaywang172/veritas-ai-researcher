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
        description="""基於搜集到的文獻資料，撰寫一個結構化的研究摘要。

要求：
1. 總結主要發現和趨勢
2. 識別研究差距
3. 提供實務建議
4. 每一個陳述必須能夠追溯到具體來源

輸出格式：每句話後面必須附上來源URL。""",
        expected_output="""一段結構化的文字，每句話後面都附上來源URL，格式如下：
主要發現：[來源URL]
研究趨勢：[來源URL]
實務建議：[來源URL]""",
        agent=synthesizer,
        context=[]  # This will be populated with the research task output
    )

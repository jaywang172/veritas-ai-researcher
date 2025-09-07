from crewai import Task
from agents import literature_scout, synthesizer, outline_planner, academic_writer

def create_research_task(research_topic: str) -> Task:
    return Task(
        description=f"根據研究主題「{research_topic}」，使用搜尋工具查找相關的學術文獻和研究資料...",
        expected_output="一個包含相關文獻來源的清單...",
        agent=literature_scout
    )

def create_summarize_task() -> Task:
    return Task(
        description="分析以下由文獻搜集代理人提供的原始研究資料...\n\n{context}",
        expected_output="一個格式嚴格的JSON字串，包含 'sentence' 和 'source'...\n**絕對不要**包含任何Markdown標記...",
        agent=synthesizer,
    )

def create_outline_task() -> Task:
    return Task(
        description="分析以下JSON格式的研究論點列表，並據此創建一份詳細的、可供機器讀取的JSON論文大綱...\n\n{context}",
        expected_output="""一個格式嚴格的JSON字串，包含 "title" 和 "chapters" 兩個鍵...
例如：
{
  "title": "AI對電腦科學的影響分析",
  "chapters": [
    { "chapter_title": "1. 引言", "supporting_points_indices": [0, 4] },
    { "chapter_title": "2. AI在高等教育中的應用", "supporting_points_indices": [0, 1, 2] }
  ]
}""",
        agent=outline_planner
    )

def create_writing_task(chapter_title: str, supporting_points: str) -> Task:
    return Task(
        description=f'當前需要撰寫的章節是："{chapter_title}"...\n\n支援論點如下：\n{supporting_points}',
        expected_output="一段或多段完整的學術段落...",
        agent=academic_writer
    )
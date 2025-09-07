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
        description="""分析以下由文獻搜集代理人提供的原始研究資料，提取關鍵論點：

{context}

**任務要求**：
1. 從原始資料中識別並提取有價值的學術論點
2. 每個論點必須包含完整的來源URL
3. 將所有論點格式化為JSON陣列

**格式要求**：
- 你的回答必須以 [ 開始，以 ] 結束
- 每個論點是一個物件，包含 "sentence" 和 "source" 字段
- 絕對不要包含任何其他文字、解釋或Markdown標記""",
        expected_output="""一個格式嚴格的JSON陣列，必須以 [ 開始，以 ] 結束，包含所有提取的論點：
[
  {
    "sentence": "具體的學術論點或研究發現",
    "source": "完整的來源URL"
  },
  {
    "sentence": "另一個學術論點",
    "source": "對應的來源URL"
  }
]

**絕對禁止**：
- 任何非JSON內容
- Markdown標記（如 ```json）
- 額外的解釋文字
- 不完整的URL""",
        agent=synthesizer,
    )

def create_outline_task() -> Task:
    return Task(
        description="""分析以下JSON格式的研究論點列表，創建一份詳細的JSON論文大綱：

{context}

**任務要求**：
1. 分析所有提供的論點，識別主要主題和邏輯關係
2. 設計合理的章節結構，確保論述流暢
3. 為每個章節分配相關的論點索引
4. 生成完整的JSON大綱

**格式要求**：
- 你的回答必須以 { 開始，以 } 結束
- 必須包含 "title" 和 "chapters" 兩個字段
- 每個chapter包含 "chapter_title" 和 "supporting_points_indices"
- 絕對不要包含任何其他文字或Markdown標記""",
        expected_output="""一個格式嚴格的JSON物件，必須以 { 開始，以 } 結束：
{
  "title": "具體的論文標題",
  "chapters": [
    {
      "chapter_title": "1. 引言",
      "supporting_points_indices": [0, 1, 4]
    },
    {
      "chapter_title": "2. 主要論述章節",
      "supporting_points_indices": [2, 3, 5, 6]
    },
    {
      "chapter_title": "3. 結論",
      "supporting_points_indices": [7, 8]
    }
  ]
}

**絕對禁止**：
- 任何非JSON內容
- Markdown標記
- 額外的解釋文字
- 無效的論點索引""",
        agent=outline_planner
    )

def create_writing_task(chapter_title: str, supporting_points: str) -> Task:
    return Task(
        description=f'''當前需要撰寫的章節是："{chapter_title}"

支援論點如下（每個論點都包含 sentence 和 source 字段）：
{supporting_points}

**寫作要求**：
1. 根據提供的論點撰寫流暢、連貫的學術段落
2. 每當引用或使用任何論點時，必須在句末標註來源：(來源URL)
3. 確保所有使用的資訊都有明確的來源標註
4. 不要包含章節標題本身，只撰寫內容段落''',
        expected_output='''一段或多段完整的學術段落，其中每個引用的資訊都在句末標註來源URL，格式如：
"這是一個重要的研究發現 (https://example.com/source1)。另一項研究也支持這個觀點 (https://example.com/source2)。"

**絕對不要**：
- 忽略來源標註
- 使用沒有提供來源的資訊
- 包含章節標題''',
        agent=academic_writer
    )
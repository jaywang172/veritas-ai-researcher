from crewai import Task
from agents import literature_scout, synthesizer, outline_planner, academic_writer, editor

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

def create_review_task() -> Task:
    return Task(
        description='''這是論文的完整初稿：

{context}

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
2. **流暢內容**：所有章節內容經過潤色，邏輯清晰，過渡自然
3. **統一風格**：全文術語和寫作風格保持一致
4. **完整引用**：保留所有原有的來源標註

輸出應該是可以直接發布的高品質學術文本，展現專業期刊的編輯水準。''',
        agent=editor
    )
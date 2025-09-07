from crewai import Task
from agents import literature_scout, synthesizer, outline_planner, academic_writer, editor, citation_formatter, computational_scientist

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

def create_citation_task() -> Task:
    return Task(
        description='''你是一位專業的學術引文格式化專家。你的唯一任務是從論文中提取URL並生成APA格式的參考文獻列表。

**輸入論文內容**：
{context}

**嚴格執行步驟**：

步驟1：URL提取
- 仔細掃描論文，找出所有括號內的URL：(http://...) 或 (https://...)
- 記錄每個完整的URL

步驟2：元數據檢索  
- 對每個URL使用搜索工具查找：
  * 作者或組織名稱
  * 文章/網頁標題
  * 發布年份
  * 來源網站名稱
- 如果無法找到，使用合理推斷

步驟3：APA格式轉換
- 網頁：Author, A. A. (Year, Month Date). Title of article. *Website Name*. URL
- 報告：Organization. (Year). *Title of report*. URL  
- 新聞：Author, A. A. (Year, Month Date). Article title. *News Site*. URL
- 學術：Author, A. A. (Year). Article title. *Journal Name*, Volume(Issue), pages. DOI or URL

步驟4：排序和格式化
- 按作者姓氏字母順序排列
- 使用懸掛縮排
- 保持URL完整可點擊

**你必須輸出**：
一個以 "## References" 開頭的完整參考文獻列表，包含論文中所有引用的來源。不要輸出任何其他內容、解釋或結論。

**禁止輸出**：
- 不要說"我現在知道最終答案"
- 不要輸出總結性語句
- 不要包含任何非引文內容
- 不要省略任何找到的URL''',
        expected_output='''## References

[按字母順序排列的APA格式參考文獻條目]

範例格式：
Chen, L. (2024, March 10). Artificial intelligence in education. *Tech Review*. https://example.com/ai-education

Ministry of Education. (2023). *Digital learning policy report*. https://example.com/policy-report

Zhang, M., & Liu, K. (2024). Machine learning applications. *Journal of AI Research*, 15(3), 45-62. https://doi.org/10.1000/example

**嚴格要求**：
- 僅包含 "## References" 標題和引文條目
- 每個條目占一行，使用APA第7版格式
- 按作者姓氏字母排序
- 保持所有URL完整
- 包含論文中的所有引用來源''',
        agent=citation_formatter
    )

def create_data_analysis_task(data_file_path: str, analysis_goal: str) -> Task:
    return Task(
        description=f'''你需要執行一個完整的數據分析任務：

**數據文件路徑**: {data_file_path}
**分析目標**: {analysis_goal}

**執行步驟**：
1. **數據讀取**: 使用FileReadTool讀取指定路徑的數據文件
2. **數據探索**: 使用CodeInterpreterTool編寫Python代碼，分析數據結構、基本統計信息
3. **目標分析**: 根據用戶的分析目標，編寫相應的分析代碼
4. **數據可視化**: 創建有意義的圖表來展示分析結果
5. **結果總結**: 將分析發現以清晰的文字形式總結

**代碼要求**：
- 使用pandas進行數據處理
- 使用matplotlib/seaborn進行可視化
- 必要時使用scikit-learn進行機器學習分析
- 確保代碼安全且可覆現
- 將生成的圖表保存為PNG文件

**輸出格式**: 生成圖表文件並提供分析摘要''',
        expected_output='''一份完整的數據分析結果，包含：

**數據概覽**：
- 數據維度：X行 Y列
- 主要字段：[字段1, 字段2, ...]
- 數據質量：缺失值情況等

**分析發現**：
- 基於分析目標的關鍵發現
- 數據中發現的模式、趨勢或異常
- 統計分析結果

**可視化結果**：
- 已生成圖表文件：analysis_chart.png
- 圖表說明和解讀

**結論與建議**：
- 基於分析結果的結論
- 後續分析建議

示例格式：
"通過對數據的分析，我們發現了以下關鍵模式：[具體發現]。詳細的可視化結果已保存為 analysis_chart.png。建議進一步關注 [具體建議]。"''',
        agent=computational_scientist
    )
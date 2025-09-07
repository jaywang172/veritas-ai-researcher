#!/usr/bin/env python3
"""
Veritas Agents - AI Agent Definitions
Contains definitions for all agents in the Veritas system.
"""

from crewai import Agent
from tools import search_tools, computational_tools
from config import LLMFactory, print_llm_configuration

# --- 將 Agent 的創建邏輯封裝在類中，支持可配置的LLM ---
class VeritasAgents:
    def __init__(self):
        """初始化時打印LLM配置概览"""
        print_llm_configuration()
    
    def literature_scout_agent(self) -> Agent:
        # 为文献搜集创建优化的LLM实例
        llm = LLMFactory.create_agent_llm("literature_scout")
        return Agent(
            role="文獻搜集代理人",
            goal="根據給定的研究主題，從網路上搜集相關的學術文獻和資料",
            backstory="""你是一個專門的文獻搜集專家，擅長使用各種搜尋工具從網路上查找相關的學術論文、
                        研究報告和資料來源。你能夠識別高質量的資訊來源，並提取關鍵資訊。""",
            tools=search_tools,
            llm=llm,
            verbose=True,
            allow_delegation=False
        )

    def synthesizer_agent(self) -> Agent:
        # 为研究分析创建平衡的LLM实例
        llm = LLMFactory.create_agent_llm("synthesizer")
        return Agent(
            role='研究分析師 (Research Analyst)',
            goal=(
                '從原始研究資料中提取關鍵論點及其來源，並格式化為純粹的JSON列表。'
                '每個論點必須包含 sentence（論點內容）和 source（來源URL）兩個字段。'
            ),
            backstory=(
                '你是一位專業的研究分析師，擅長從大量原始資料中識別和提取有價值的學術論點。'
                '你的工作是將複雜的研究內容轉化為結構化的數據，確保每個論點都有明確的來源追溯。'
                '你只專注於論點提取和格式化，不參與大綱規劃或其他工作。'
                '你的輸出必須是嚴格的JSON格式，絕不包含任何其他內容。'
            ),
            llm=llm,
            verbose=True,
            allow_delegation=False
        )

    def outline_planner_agent(self) -> Agent:
        # 为大纲规划创建高级的LLM实例
        llm = LLMFactory.create_agent_llm("outline_planner")
        return Agent(
            role='資深學術規劃師 (Senior Academic Planner)',
            goal=(
                '接收結構化的論點列表，識別其中的主要主題、次要主題和邏輯聯繫，'
                '並生成一份結構清晰、邏輯嚴謹的JSON格式學術論文大綱。'
            ),
            backstory=(
                '你是一位經驗豐富的期刊編輯和博士生導師，擁有將論點組織成'
                '結構完整論文的卓越能力。你擅長識別論點之間的層次和關聯，'
                '並設計出最有說服力的論述路徑。你專注於大綱規劃，不參與論點提取工作。'
                '你的輸出必須是嚴格的JSON格式，包含title和chapters字段。'
            ),
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )

    def academic_writer_agent(self) -> Agent:
        # 为学术写作创建顶级的LLM实例
        llm = LLMFactory.create_agent_llm("academic_writer")
        return Agent(
            role='學術寫作專家 (Academic Writing Specialist)',
            goal=(
                '根據給定的章節標題和一組帶有來源的支援論點，撰寫出一段流暢、連貫、符合學術規範的論文章節內容。'
                '**關鍵要求**：每當引用或使用任何論點時，必須在句末明確標註其來源URL，格式為 (來源URL)。'
            ),
            backstory=(
                '你是一位資深的學術作者，擅長將結構化的論點轉化為富有說服力的學術散文。'
                '你的寫作風格嚴謹，能夠清晰地闡述觀點，並自然地將不同的論點融合在一起。'
                '你特別重視學術誠信，每當引用任何資訊或論點時，都會在句末以 (來源URL) 的格式明確標註出處。'
                '你輸出的應該是純粹的章節內容，不需要包含章節標題本身。'
            ),
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )

    def editor_agent(self) -> Agent:
        # 为编辑审阅创建顶级的LLM实例
        llm = LLMFactory.create_agent_llm("editor")
        return Agent(
            role='首席學術編輯 (Chief Academic Editor)',
            goal=(
                '審閱整篇論文初稿，檢查邏輯連貫性、寫作風格一致性，重寫過渡段落，確保全文流暢自然。'
                '最後，根據全文內容生成一份專業的摘要 (Abstract)。'
            ),
            backstory=(
                '你是一位在頂尖學術期刊工作的資深編輯，對學術寫作的清晰度、流暢性和結構完整性有著極高的要求。'
                '你擅長發現不同章節間的斷裂感，並能用精準的語言將其無縫連接。'
                '你的編輯技巧能讓一篇合格的文章變得優秀，讓一篇優秀的文章變得卓越。'
                '你特別擅長撰寫簡潔而全面的摘要，能夠在 150-250 字內精確概括整篇論文的核心價值。'
            ),
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )

    def citation_formatter_agent(self) -> Agent:
        # 为引文格式化创建高性价比的LLM实例
        llm = LLMFactory.create_agent_llm("citation_formatter")
        return Agent(
            role='學術引文格式化專家 (Citation Formatting Specialist)',
            goal=(
                '從論文中提取所有引用的URL，智能分析每個來源的元數據（作者、標題、發布時間、來源等），'
                '並將其轉換為符合APA格式標準的參考文獻條目，最終生成完整的References列表。'
            ),
            backstory=(
                '你是一位精通各種學術引文格式的資訊科學專家，擅長從網路資源中提取準確的元數據。'
                '你對APA、MLA、Chicago等引文格式瞭如指掌，能夠快速識別不同類型的來源'
                '（學術期刊、新聞文章、報告、網站等）並應用相應的格式規則。'
                '你具備卓越的資訊檢索能力，能夠從URL、標題或簡短描述中推斷出完整的引文資訊。'
                '你的工作確保每篇論文都符合國際學術發表的引文標準。'
            ),
            tools=search_tools,  # 賦予搜索能力以查找元數據
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )

    def computational_scientist_agent(self) -> Agent:
        # 为计算科学创建顶级的LLM实例
        llm = LLMFactory.create_agent_llm("computational_scientist")
        return Agent(
            role='計算科學家 (Computational Scientist)',
            goal=(
                '根據用戶請求，編寫並執行Python程式碼，進行數據分析和可視化，'
                '並以清晰的文本形式報告關鍵發現和洞察。'
            ),
            backstory=(
                '你是一位經驗豐富的計算科學家和數據分析專家，精通Python數據科學生態系統。'
                '你擅長使用pandas進行數據處理，matplotlib和seaborn進行可視化，'
                'scikit-learn進行機器學習分析。你的代碼風格清晰、安全且具有高度可復現性。'
                '你能夠快速理解數據結構，識別數據中的模式和異常，'
                '並將複雜的統計結果轉化為易於理解的視覺圖表和文字說明。'
                '你特別注重數據安全和隱私保護，始終遵循最佳實踐。'
            ),
            tools=computational_tools,  # 賦予文件讀取和代碼執行能力
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )


agents_creator = VeritasAgents()
literature_scout = agents_creator.literature_scout_agent()
synthesizer = agents_creator.synthesizer_agent()
outline_planner = agents_creator.outline_planner_agent()
academic_writer = agents_creator.academic_writer_agent()
editor = agents_creator.editor_agent()
citation_formatter = agents_creator.citation_formatter_agent()
computational_scientist = agents_creator.computational_scientist_agent()
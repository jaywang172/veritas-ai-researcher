#!/usr/bin/env python3
"""
Veritas Agents - AI Agent Definitions
Contains definitions for all agents in the Veritas system.
"""

from crewai import Agent
from tools import search_tools, computational_tools
from config import LLMFactory, print_llm_configuration

# --- 將 Agent 的建立邏輯封裝在類別中，支援可配置的LLM ---
class VeritasAgents:
    def __init__(self):
        """初始化時列印LLM配置概覽"""
        print_llm_configuration()
    
    def literature_scout_agent(self) -> Agent:
        # 為文獻搜集建立最佳化的LLM實例
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
        # 為研究分析創建平衡的LLM實例
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
        # 為大綱規劃創建高級的LLM實例
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
        # 為學術寫作創建頂級的LLM實例
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
        # 為編輯審閱創建頂級的LLM實例
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
        # 為引文格式化創建高效能的LLM實例
        llm = LLMFactory.create_agent_llm("citation_formatter")
        return Agent(
            role='專業學術引文格式化專家 (Professional Academic Citation Specialist)',
            goal=(
                '精確提取論文中所有URL引用，使用搜索工具獲取元數據，'
                '並嚴格按照APA第7版格式生成完整的References參考文獻列表。'
                '絕不輸出任何總結性語句或結論，只輸出格式化的引文列表。'
            ),
            backstory=(
                '你是一位在頂尖學術期刊工作20年的專業引文編輯，對APA格式的每個細節都瞭如指掌。'
                '你擅長從URL中準確提取元數據，包括作者、標題、發布日期和來源網站。'
                '你的專業素養要求你只專注於引文格式化任務，絕不偏離主題或添加不必要的評論。'
                '你的輸出必須是純粹的APA格式References列表，沒有任何額外內容。'
                '你使用搜索工具來驗證和完善每個引用來源的準確性。'
                '你堅持"只做引文，不做總結"的職業原則。'
            ),
            tools=search_tools,  # 賦予搜尋能力以查找元資料
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )

    def computational_scientist_agent(self) -> Agent:
        # 為計算科學創建頂級的LLM實例
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

    def project_manager_agent(self) -> Agent:
        # 為專案管理創建最高級的LLM實例
        llm = LLMFactory.create_agent_llm("project_manager")
        return Agent(
            role='首席研究策略師 (Chief Research Strategist)',
            goal=(
                '分析使用者的開放式研究目標，將其分解為具體可執行的子任務，'
                '智慧決策應將任務分配給哪些專家代理人，並協調整個混合研究流程。'
                '確保文獻分析與資料分析能有機結合，產生深度洞察。'
            ),
            backstory=(
                '你是一位具有15年跨學科研究經驗的資深策略師，曾主導過上百個複雜研究專案。'
                '你擅長快速識別研究問題的本質，判斷需要進行質化分析、量化分析，還是混合方法。'
                '你對每位團隊成員的專長瞭如指掌：文獻搜集專家擅長收集外部資訊，'
                '計算科學家精通資料分析和視覺化，研究分析師擅長綜合整理，'
                '大綱規劃師能設計邏輯結構，學術寫作專家能撰寫專業報告，編輯能潤色提升。'
                '你的決策總是基於效率最大化和品質最佳化的原則，'
                '能夠動態調整研究策略，確保每個子任務都能為最終目標服務。'
                '你特別擅長設計並行工作流程，讓不同專家同時工作以提高效率。'
            ),
            tools=[],  # 專案經理主要工作是思考、規劃與決策，不需要特定工具
            llm=llm,
            verbose=True,
            allow_delegation=True,  # 專案經理需要委派任務給其他代理人
        )


agents_creator = VeritasAgents()
literature_scout = agents_creator.literature_scout_agent()
synthesizer = agents_creator.synthesizer_agent()
outline_planner = agents_creator.outline_planner_agent()
academic_writer = agents_creator.academic_writer_agent()
editor = agents_creator.editor_agent()
citation_formatter = agents_creator.citation_formatter_agent()
computational_scientist = agents_creator.computational_scientist_agent()
project_manager = agents_creator.project_manager_agent()

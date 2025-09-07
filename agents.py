#!/usr/bin/env python3
"""
Veritas Agents - AI Agent Definitions
Contains definitions for all agents in the Veritas system.
"""

from crewai import Agent
from tools import search_tools
from langchain_openai import ChatOpenAI

# Initialize the language model
llm = ChatOpenAI(
    model="gpt-4.1",
    temperature=0.1
)

# --- 將 Agent 的創建邏輯封裝在類中 ---
class VeritasAgents:
    def literature_scout_agent(self) -> Agent:
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
        # 這個 agent 現在也負責規劃大綱
        return Agent(
            role='學術規劃與驗證專家 (Academic Planning & Integrity Expert)',
            goal=(
                '分析提供的研究資料，提取核心論點，並將它們組織成一個結構化的JSON論文大綱。'
            ),
            backstory=(
                '你是一位對學術誠信和結構有著極高標準的專家...'
                '你的任務是創建一份可供機器執行的論文藍圖（JSON格式的大綱）。'
                '不要將列表包裹在任何物件中。' # 增加約束
            ),
            llm=llm,
            verbose=True,
            allow_delegation=False
        )

    def outline_planner_agent(self) -> Agent:
        return Agent(
            role='資深學術規劃師 (Senior Academic Planner)',
            goal=(
                '分析提供的所有結構化研究論點，識別其中的主要主題、次要主題和邏輯聯繫。'
                '最終生成一份結構清晰、邏輯嚴謹的學術論文大綱。'
            ),
            backstory=(
                '你是一位經驗豐富的期刊編輯和博士生導師，擁有將大量零散資訊'
                '構建成一篇結構完整論文的卓越能力。你擅長識別論點之間的層次和關聯，'
                '並設計出最有說服力的論述路徑。你的輸出必須是格式化的Markdown大綱。'
            ),
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )

    def academic_writer_agent(self) -> Agent:
        return Agent(
            role='學術寫作專家 (Academic Writing Specialist)',
            goal=(
                '根據給定的章節標題和一組帶有來源的支援論點，撰寫出一段流暢、連貫、符合學術規範的論文章節內容。'
            ),
            backstory=(
                '你是一位資深的學術作者，擅長將結構化的論點轉化為富有說服力的學術散文。'
                '你的寫作風格嚴謹，能夠清晰地闡述觀點，並自然地將不同的論點融合在一起。'
                '你輸出的應該是純粹的章節內容，不需要包含章節標題本身。'
            ),
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )


agents_creator = VeritasAgents()
literature_scout = agents_creator.literature_scout_agent()
synthesizer = agents_creator.synthesizer_agent()

# --- 在这里添加下面这一行 ---
outline_planner = agents_creator.outline_planner_agent()

academic_writer = agents_creator.academic_writer_agent()
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


agents_creator = VeritasAgents()
literature_scout = agents_creator.literature_scout_agent()
synthesizer = agents_creator.synthesizer_agent()

# --- 在这里添加下面这一行 ---
outline_planner = agents_creator.outline_planner_agent()

academic_writer = agents_creator.academic_writer_agent()
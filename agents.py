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
    model="gpt-4",
    temperature=0.1
)

class LiteratureScoutAgent:
    """Agent responsible for searching and collecting literature from the web."""

    @staticmethod
    def create():
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

class SynthesizerAgent:
    """Agent responsible for synthesizing collected information into traceable, structured summaries."""

    @staticmethod
    def create():
        return Agent(
            role='學術誠信驗證員 (Academic Integrity Officer)',
            goal=(
                '根據提供的研究資料，生成一份結構化的JSON報告。'
                '報告中的每一項都必須包含一個核心論點（sentence）和其對應的原始來源URL（source）。'
                '絕對不允許創造任何沒有直接來源支持的資訊。'
            ),
            backstory=(
                '你是一位對學術誠信有著極高標準的專家。你的唯一職責是確保資訊的準確性和可追溯性。'
                '你將任何無法驗證來源的資訊都視為學術不端。'
                '你產出的不是優美的文章，而是嚴謹、可供審計的數據記錄。'
                '你的輸出必須是格式正確的JSON。'
            ),
            llm=llm,
            verbose=True,
            allow_delegation=False
        )

# Agent instances
literature_scout = LiteratureScoutAgent.create()
synthesizer = SynthesizerAgent.create()

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
    """Agent responsible for synthesizing collected information into coherent summaries."""

    @staticmethod
    def create():
        return Agent(
            role='專業學術研究員',
            goal='根據提供的研究資料，撰寫一段簡潔、流暢且全面的學術綜述。',
            backstory=(
                '你是一位在頂尖研究機構工作的資深研究員，'
                '擅長快速閱讀大量文獻並從中提煉出核心觀點和趨勢。'
                '你的寫作風格清晰、精準，能夠將複雜的資訊轉化為易於理解的摘要。'
            ),
            llm=llm,
            verbose=True,
            allow_delegation=False
        )

# Agent instances
literature_scout = LiteratureScoutAgent.create()
synthesizer = SynthesizerAgent.create()

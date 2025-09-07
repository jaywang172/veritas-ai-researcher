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
            role="洞察綜合代理人",
            goal="""根據搜集到的資料撰寫結構化的摘要報告，確保每一句話都能夠明確追溯到來源文獻""",
            backstory="""你是一個經驗豐富的學術寫作專家，擅長將複雜的資訊轉化為清晰、結構化的文字。
            你嚴格要求自己確保內容的可追溯性，每一個陳述都必須有明確的來源依據。""",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )

# Agent instances
literature_scout = LiteratureScoutAgent.create()
synthesizer = SynthesizerAgent.create()

#!/usr/bin/env python3
"""
Veritas Tools - Custom Tools for Agents
Contains tool definitions and configurations for the Veritas system.
"""

# 根據錯誤訊息的提示，使用正確的類別名稱
from crewai_tools import TavilySearchTool

# 使用正確的類別名稱進行初始化
tavily_search = TavilySearchTool()

# 將這個工具放入工具列表
search_tools = [
    tavily_search
]
#!/usr/bin/env python3
"""
Veritas Tools - Custom Tools for Agents
Contains tool definitions and configurations for the Veritas system.
"""

# 導入搜索工具
from crewai_tools import TavilySearchTool

# 導入新的數據處理工具
from crewai_tools import FileReadTool, CodeInterpreterTool

# 初始化搜索工具
tavily_search = TavilySearchTool()

# 初始化文件讀取工具
file_read_tool = FileReadTool()

# 初始化代碼解釋器工具
code_interpreter_tool = CodeInterpreterTool()

# 搜索工具集合（用於文獻搜集和引文格式化）
search_tools = [
    tavily_search
]

# 計算工具集合（用於數據分析和代碼執行）
computational_tools = [
    file_read_tool,
    code_interpreter_tool
]

# 完整工具集合（包含所有工具）
all_tools = search_tools + computational_tools
#!/usr/bin/env python3
"""
Veritas Tools - Custom Tools for Agents
Contains tool definitions and configurations for the Veritas system.
"""

from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from langchain_community.tools.tavily_search import TavilySearchResults

# Initialize search tools
tavily_search = TavilySearchResults(
    max_results=10,
    search_depth="advanced"
)

# List of available tools
search_tools = [
    tavily_search,
    # You can add more tools here as needed
    # SerperDevTool(),
    # ScrapeWebsiteTool()
]

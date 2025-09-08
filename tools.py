#!/usr/bin/env python3
"""
Veritas Tools - Custom Tools for Agents
Contains tool definitions and configurations for the Veritas system.
"""

import os
import sys
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any

# 導入搜索工具
from crewai_tools import TavilySearchTool

# 導入新的數據處理工具
from crewai_tools import FileReadTool
from crewai.tools import BaseTool, tool
from pydantic import BaseModel, Field

# 初始化搜索工具
tavily_search = TavilySearchTool()

# 初始化文件讀取工具
file_read_tool = FileReadTool()


def execute_python_code(python_code: str) -> str:
    """
    在本地 Python 環境中執行 Python 代碼，支援所有已安裝的函式庫。
    比 CodeInterpreterTool 更可靠，因為使用當前虛擬環境。
    
    Args:
        python_code (str): 要執行的 Python 代碼
        
    Returns:
        str: 執行結果或錯誤信息
    """
    try:
        # 創建臨時文件
        temp_dir = Path(tempfile.gettempdir()) / "veritas_code_execution"
        temp_dir.mkdir(exist_ok=True)
        
        # 生成唯一的文件名
        script_id = str(uuid.uuid4())[:8]
        script_path = temp_dir / f"script_{script_id}.py"
        
        # 將代碼寫入臨時文件
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(python_code)
        
        # 確定 Python 解釋器路徑
        # 優先使用虛擬環境中的 Python
        if 'VIRTUAL_ENV' in os.environ:
            python_exec = os.path.join(os.environ['VIRTUAL_ENV'], 'bin', 'python')
        elif hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            # 在虛擬環境中
            python_exec = sys.executable
        else:
            # 使用當前 Python
            python_exec = sys.executable
        
        # 執行代碼
        result = subprocess.run(
            [python_exec, str(script_path)],
            capture_output=True,
            text=True,
            timeout=300,  # 5分鐘超時
            cwd=os.getcwd()  # 使用當前工作目錄，確保能訪問數據文件
        )
        
        # 清理臨時文件
        try:
            script_path.unlink()
        except:
            pass
        
        # 處理執行結果
        if result.returncode == 0:
            output = result.stdout.strip()
            if result.stderr:
                output += f"\n警告信息:\n{result.stderr.strip()}"
            return f"代碼執行成功！\n\n輸出結果:\n{output}" if output else "代碼執行成功，無輸出。"
        else:
            error_msg = result.stderr.strip() if result.stderr else "未知錯誤"
            return f"代碼執行失敗！\n\n錯誤信息:\n{error_msg}"
            
    except subprocess.TimeoutExpired:
        return "代碼執行超時（5分鐘限制）"
    except Exception as e:
        return f"工具執行失敗: {str(e)}"


# 替代原有的 CodeInterpreterTool
class LocalCodeExecutorTool(BaseTool):
    """
    本地代碼執行工具類，提供與 CodeInterpreterTool 兼容的接口
    """
    name: str = "LocalCodeExecutor"
    description: str = """
    在本地 Python 環境中執行 Python 代碼。支援所有已安裝的函式庫，
    包括 pandas, matplotlib, seaborn, numpy 等。比 Docker 環境更可靠。
    
    使用方法：
    - 傳入完整的 Python 代碼字符串
    - 代碼會在當前工作目錄執行，可以訪問本地文件
    - 自動捕獲並返回執行結果或錯誤信息
    """
    
    class ToolInput(BaseModel):
        python_code: str = Field(..., description="要執行的 Python 代碼")
    
    args_schema: type[BaseModel] = ToolInput
    
    def _run(self, python_code: str) -> str:
        """執行 Python 代碼"""
        return execute_python_code(python_code)


# 創建工具實例
local_code_tool = LocalCodeExecutorTool()

# 搜索工具集合（用於文獻搜集和引文格式化）
search_tools = [
    tavily_search
]

# 計算工具集合（用於數據分析和代碼執行）
computational_tools = [
    file_read_tool,
    local_code_tool  # 使用新的本地代碼執行工具
]

# 完整工具集合（包含所有工具）
all_tools = search_tools + computational_tools
---

# Veritas - AI 驅動的自主化研究框架

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Framework](https://img.shields.io/badge/Framework-CrewAI%20&%20LangGraph-orange)](https://github.com/joaomdmoura/crewAI)

**Veritas** 是一個先進的、自主化的多代理人 (Multi-Agent) AI 研究框架。它模擬一個高效的研究團隊，能夠自動化執行從文獻搜集、數據分析、草稿撰寫到編輯審閱和引文格式化的完整研究流程。

其核心設計理念源於 **Linux 哲學**：保持核心功能的簡潔、可靠與可組合性，同時透過可配置的模組來適應不同的研究需求與複雜度。

## 核心理念

- **化繁為簡 (Simplicity)**：提供清晰、線性的工作流程，確保結果的可預測性與可靠性。
- **模組化與可配置 (Modularity & Configurability)**：為每個 AI 代理人獨立配置最強大的大型語言模型 (LLM)，並能根據預算和任務需求動態調整。
- **漸進式增強 (Progressive Enhancement)**：提供從基礎到專家級的多種工作流程，使用者可以根據需求選擇最適合的模式。
- **可靠性 (Reliability)**：拒絕虛假的「完成」狀態。流程中的每一步都必須成功，否則整個流程將會明確地失敗，確保結果的真實性。

## 關鍵特性

- **🤖 專業分工的多代理人系統**：
  - 內建多個專家代理人，各司其職，包括文獻搜集、數據分析、學術寫作、編輯審閱等。
  - 每個代理人的角色、目標和背景故事都經過精心設計，以確保其專業性。

- **🧠 模組化的 LLM 工廠**：
  - 允許為不同的代理人配置最適合的 LLM（例如，為寫作專家配置 GPT-5，為格式化工具配置更經濟的 GPT-4.1-mini）。
  - 支援成本估算和預算友好的配置模式（經濟、平衡、高級）。

- **🌀 多層次的工作流程架構**：
  1.  **簡單工作流程 (`simple_workflow.py`)**：一個乾淨、線性的執行管線，確保基礎研究任務的可靠完成。
  2.  **增強工作流程 (`enhanced_workflow.py`)**：在簡單流程基礎上增加了多輪審稿和修訂循環，適合需要更高學術嚴謹性的任務。
  3.  **領域自適應工作流程 (`domain_adaptive_workflow.py`)**：能自動檢測研究目標的領域（如商業、學術、科技），並調整分析重點、寫作風格和品質標準。
  4.  **混合智慧工作流程 (`hybrid_workflow.py`)**：基於 `LangGraph` 打造的 state machine，實現了真正的「審稿-修訂」反饋閉環，是框架中最先進、最智能的模式。

- **📊 本地代碼執行與數據分析**：
  - 內建 `LocalCodeExecutorTool`，允許 `computational_scientist_agent` 在本地安全地執行 Python 代碼進行數據分析與可視化，支援 `pandas`, `matplotlib` 等所有函式庫。

- **🔧 易於使用的設定腳本**：
  - 提供 `setup_api_keys.py` 腳本，引導使用者輕鬆完成 API Keys 的設定。

## 專案結構

```
.
├── agents.py                   # 定義所有 AI 代理人 (Agents)
├── config.py                   # LLM 模型配置工廠與管理
├── tasks.py                    # 定義每個代理人執行的任務 (Tasks)
├── tools.py                    # 定義代理人使用的工具 (如搜尋、代碼執行)
│
├── simple_main.py              # 🚀 入口點：執行簡單工作流程
├── enhanced_main.py            # 🚀 入口點：執行增強工作流程
├── domain_main.py              # 🚀 入口點：執行領域自適應工作流程
│
├── workflows/
│   ├── simple_workflow.py      # 核心邏輯：簡單線性研究流程
│   ├── enhanced_workflow.py    # 核心邏輯：帶有多輪審閱的增強流程
│   ├── domain_adaptive_workflow.py # 核心邏輯：自適應不同研究領域的流程
│   └── hybrid_workflow.py      # 核心邏輯：基於 LangGraph 的反饋式混合智慧流程
│
├── setup_api_keys.py           # API Keys 設定輔助腳本
└── results/                    # 存放所有研究報告的目錄 (自動生成)
```

## 安裝與設定

### 1. 複製專案

```bash
git clone https://github.com/your-username/veritas.git
cd veritas
```

### 2. 建立並啟用虛擬環境

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 安裝依賴套件

您需要安裝 `requirements.txt` 檔案。

```bash
pip install -r requirements.txt
```

### 4. 設定 API Keys

本專案需要 OpenAI API Key，以及可選的 Tavily Search API Key 以獲得更好的搜尋結果。

執行設定腳本，並根據提示輸入您的 API Keys：

```bash
python setup_api_keys.py
```

這將會自動創建並配置您的 `.env` 檔案。

## 如何使用

您可以根據您的需求選擇不同的入口點來啟動研究流程。

### 1. 執行簡單研究

適用於快速、直接的研究任務。

```bash
python simple_main.py
```

程式會提示您輸入**研究目標**和可選的**資料檔案路徑**。

### 2. 執行增強研究

適用於需要更高品質、經過多輪內部審閱的報告。

```bash
python enhanced_main.py
```

### 3. 執行領域自適應研究

讓 AI 自動判斷或由您指定研究領域，以產出更具專業性的報告。

```bash
# 自動檢測領域
python domain_main.py

# 手動指定領域 (例如 academic, business, scientific, technical)
python domain_main.py academic
```

## 工作流程詳解

- **Simple Workflow**：最基礎的線性流程，依序執行：文獻搜集 → (數據分析) → 綜合 → 大綱 → 寫作 → 編輯 → 引文。可靠且易於除錯。
- **Enhanced Workflow**：在寫作後增加了**多輪審閱與修訂**的步驟，模擬學術界的同儕審查，顯著提升報告品質。
- **Domain-Adaptive Workflow**：在啟動時會分析研究目標的關鍵詞（如 "financial", "literature review", "performance"），自動配置最適合的分析策略與寫作風格。
- **Hybrid Workflow (最先進)**：利用 `LangGraph` 建立了一個動態的狀態圖。其中的**品質審核節點 (`quality_check_node`)** 會對初稿進行評分和評估，如果品質不達標，流程會自動進入**修訂節點 (`revision_node`)**，形成一個自我改進的閉環，直到報告品質滿足要求為止。

## 授權

本專案採用 [MIT License](LICENSE) 授權。

## 致謝

- 本專案基於 [CrewAI](https://github.com/joaomdmoura/crewAI) 框架構建。
- 混合智慧工作流程使用了 [LangGraph](https://github.com/langchain-ai/langgraph) 技術。

---

# 🔬 Veritas - 透明化 AI 研究協調平台（原型 v1.0）

Veritas 是一個以多代理人協作為核心、專注於「可追溯學術綜述」的命令列原型。輸入研究主題後，系統會：搜尋文獻 → 提煉論點 → 規劃大綱（JSON）→ 逐章寫作，最終輸出為一份帶有來源脈絡的初稿。

## 功能特點

- 自動化研究流程：多個 Agent 串接完成研究到寫作全流程。
- 可追溯與結構化：中間產物為嚴格 JSON；章節內容基於具來源的論點生成。
- CLI 體驗：一步輸入主題，生成對應 `*_draft.txt` 初稿。

## 技術棧

- Python 3.10+
- crewAI（多代理人框架）
- langchain_openai（LLM 連接）
- crewai_tools.TavilySearchTool（網路搜尋）
- python-dotenv（環境變數）

## 環境變數

建立 `.env`（可由 `.env.example` 複製）：

```
OPENAI_API_KEY=你的OpenAI金鑰
TAVILY_API_KEY=你的Tavily金鑰
```

預設模型：`gpt-4.1`（可於 `agents.py` 中調整）。

## 快速開始

1) 建立虛擬環境並啟動

```
python -m venv venv
venv\Scripts\activate  # Windows
# 或
source venv/bin/activate # macOS/Linux
```

2) 安裝依賴

```
pip install -r requirements.txt
```

3) 設定環境變數

複製 `.env.example` 為 `.env` 並填入金鑰。

4) 執行

```
cd veritas_prototype
python main.py
```

依提示輸入主題，例如：`AI 對電腦科學教育的影響`。完成後會在當前資料夾產生 `主題_draft.txt`，例如現有樣例 `AI對於電腦科學的衝擊_draft.txt`。

## 專案結構與模組

- `main.py`：CLI 流程與任務編排（研究 → 摘要 → 大綱 → 逐章寫作 → 輸出）。
- `agents.py`：定義四個 Agent（文獻搜集、綜合規劃、大綱規劃、學術寫作）。
- `tasks.py`：針對各 Agent 的 `Task` 說明與預期輸出。
- `tools.py`：搜尋工具 `TavilySearchTool` 設定。
- `requirements.txt`：相依套件清單。
- `AI對於電腦科學的衝擊_draft.txt`：由原型產生的示例輸出。

## 常見問題

- 缺少金鑰：請確認 `.env` 內已正確設定 `OPENAI_API_KEY` 與 `TAVILY_API_KEY`。
- 模型不可用：將 `agents.py` 的 `model` 改為你帳號可用的模型名稱。
- 文字亂碼：請以 UTF-8 編碼開啟輸出檔。

## 授權

此專案為研究原型，用於驗證工作流程與可追溯性設計。

# 🔬 Veritas - 透明化AI研究協調平台 (原型 v1.0)

這是一個基於 `crewAI` 框架的命令列原型，旨在驗證 Veritas 專案的核心價值主張：**自動化生成可追溯的學術綜述**。

## 核心功能

- **自動化研究流程**: 輸入一個研究主題，AI代理人團隊會自動搜尋網路文獻並進行分析。
- **可追溯性**: 最終生成的綜述報告中，每一句話都明確標示其原始資訊來源的URL。
- **結構化輸出**: 利用強大的Prompt Engineering技巧，強制AI以可驗證的JSON格式輸出結果，從根本上杜絕「AI幻覺」。

## 技術棧

- **Python 3.10+**
- **多代理人框架**: `crewAI`
- **LLM連接**: `langchain_openai`
- **網路搜尋工具**: `Tavily Search`
- **環境變數管理**: `python-dotenv`

## 如何運行

1.  **克隆倉庫**
    ```bash
    git clone [你的倉庫URL]
    cd veritas_prototype
    ```

2.  **創建並啟動虛擬環境**
    ```bash
    python -m venv venv
    source venv/bin/activate  # macOS/Linux
    # 或者
    .\venv\Scripts\activate   # Windows
    ```

3.  **安裝依賴**
    ```bash
    pip install -r requirements.txt
    ```

4.  **設定API金鑰**
    - 複製 `.env.example` 並將其命名為 `.env`。
    - 編輯 `.env` 檔案，填入你的 `OPENAI_API_KEY` 和 `Tavily_API_KEY`。

5.  **運行原型**
    ```bash
    python main.py
    ```
    - 根據提示輸入你感興趣的研究主題即可。

## 專案結構

```
veritas_prototype/
├── .venv/
├── .gitignore
├── .env
├── main.py         # 主執行入口
├── agents.py       # 定義所有AI代理人
├── tasks.py        # 定義所有任務
├── tools.py        # 定義代理人使用的工具
├── requirements.txt # Python依賴
├── .env.example    # 環境變數範例
└── README.md       # 本文件
```

## 開發階段

### Sprint 1: 單一代理人與工具驗證 ✅
- [x] 創建 LiteratureScoutAgent
- [x] 實現 TavilySearchResults 工具
- [x] 基本Crew結構

### Sprint 2: 雙代理人協作與資料傳遞 ✅
- [x] 實現 SynthesizerAgent 專業學術研究員角色
- [x] 設定任務間自動資料傳遞 (context機制)
- [x] 實現 Process.sequential 順序執行
- [x] 驗證代理人協作與資料流

### Sprint 3: 核心功能實現 - 可追溯性 ✅
- [x] 實現結構化JSON輸出格式
- [x] 改造SynthesizerAgent為學術誠信驗證員
- [x] 添加JSON解析與錯誤處理
- [x] 實現每一句話的可追溯性
- [x] 從敘述性輸出轉為可驗證的數據結構

### Sprint 4: 整合與最終呈現 ✅
- [x] CLI介面優化與美化
- [x] 添加專業標題和視覺元素
- [x] 改善錯誤處理和用戶體驗
- [x] 最終輸出格式化
- [x] 創建完整的使用說明文檔

## 輸出範例

```
============================================================
🔬 Veritas - 透明化AI研究協調平台 (原型 v1.0)
============================================================

请输入您想研究的主題 (例如: the impact of remote work on employee productivity):
> the impact of remote work on employee productivity

🚀 啟動 Veritas 代理人團隊...
   - 正在進行文獻搜尋與分析，請稍候...

============================================================
✅ 任務完成！
============================================================

主題： the impact of remote work on employee productivity

--- 綜述報告 (可追溯) ---

1. Remote work has shown a significant increase in perceived autonomy among employees, which correlates positively with job satisfaction.
   └─ 來源: https://www.tavily.com/search/...

2. However, challenges in team collaboration and spontaneous communication have also been widely reported.
   └─ 來源: https://www.tavily.com/search/...

--- 報告結束 ---
```

## 授權

這個專案是Veritas專案的原型實現，專注於驗證核心技術概念。

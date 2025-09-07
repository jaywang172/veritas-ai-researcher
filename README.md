# Veritas Prototype

一個由多個AI代理人組成的團隊，能夠自動化地接收一個研究主題，並產出一段每一句話都能明確追溯到來源文獻的綜述性文字。

## 環境設置

### 1. Python 環境
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. 安裝依賴
```bash
pip install crewai crewai[tools] langchain_openai python-dotenv
```

### 3. API 金鑰設置
編輯 `.env` 檔案並填入你的API金鑰：
```
OPENAI_API_KEY="你的OpenAI API金鑰"
TAVILY_API_KEY="你的Tavily API金鑰"
```

## 使用方法

運行原型：
```bash
python main.py
```

然後輸入研究主題，例如："the impact of remote work on employee productivity"

## 專案結構

- `main.py` - 主程式入口
- `agents.py` - AI代理人定義
- `tools.py` - 工具定義
- `tasks.py` - 任務定義
- `.env` - 環境變數（API金鑰）
- `.gitignore` - Git忽略檔案

## 開發階段

### Sprint 1: 單一代理人與工具驗證 ✅
- [x] 創建 LiteratureScoutAgent
- [x] 實現 TavilySearchResults 工具
- [x] 基本Crew結構

### Sprint 2: 雙代理人協作與資料傳遞 🚧
- [ ] 實現 SynthesizerAgent
- [ ] 設定任務間資料傳遞

### Sprint 3: 核心功能實現 - 可追溯性 📋
- [ ] 實現結構化輸出
- [ ] JSON格式處理

### Sprint 4: 整合與最終呈現 📋
- [ ] CLI介面優化
- [ ] 最終輸出格式化

## 注意事項

- 確保 `.env` 檔案中的API金鑰正確
- 不要將 `.env` 檔案提交到Git倉庫
- 運行前確保虛擬環境已啟動

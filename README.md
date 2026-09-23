# Taiwan Weather Forecast - 台灣天氣預報網站

🌤️ **中央氣象署 36 小時天氣預報課程專題儀表板 (Weather Dashboard)**

本專題以教學示範架構為核心，整合 **中央氣象署 (CWA) Open Data API**，運用 Python、Requests、Pandas、SQLite、Plotly 與 Folium，打造具備完整分層架構（Layered Architecture）的現代化互動氣象儀表板。

---

## 📑 目錄
- [專題特色與亮點](#專題特色與亮點)
- [系統分層架構](#系統分層架構)
- [專案結構](#專案結構)
- [環境需求與安裝](#環境需求與安裝)
- [API 金鑰安全配置](#api-金鑰安全配置)
- [啟動與使用方式](#啟動與使用方式)
- [單元測試執行](#單元測試執行)
- [異常防護與優雅降級](#異常防護與優雅降級)

---

## 🌟 專題特色與亮點

1. **五大資料與視覺化呈現區塊**：
   - **地區 Weather Cards**：展示指定縣市當前時段天候（含動態 Emoji 圖示）、最高溫、最低溫、降雨機率及體感舒適度。
   - **未來 36 小時氣溫趨勢圖**：採用 Plotly 雙線平滑折線圖，直觀對比最高溫與最低溫走勢。
   - **降雨機率分析圖**：使用 Plotly 漸層長條圖呈現各時段降雨機率（PoP）。
   - **詳細預報表格**：以清晰的表格呈現未來三個 12 小時時段的完整資訊。
   - **全台天氣概況互動地圖**：結合 Folium 與 streamlit-folium，於地圖上依溫度動態標記全台 22 縣市，支援點擊彈出視窗（Popup）。
2. **高效快取與資料庫儲存**：
   - 整合 SQLite 資料庫 (`data/weather.db`)，具備 `UNIQUE` 鍵約束與 `ON CONFLICT` 防重複寫入機制。
   - 自動判斷快取時效 (TTL)，避免 Streamlit rerun 重複請求外部 API。
3. **安全規範**：
   - 支援 `.env` 與 Streamlit Secrets (`.streamlit/secrets.toml`) 雙重金鑰讀取，不將敏感憑證提交至 Git。
4. **全方位錯誤防護**：
   - 針對 HTTP 異常、Timeout、無效 JSON、欄位缺失、API 錯誤訊息及 SQLite 連線問題做嚴密攔截，網站永不崩潰。

---

## 🏗️ 系統分層架構

本專題完全遵循責任分離原則（Separation of Concerns）：

```
[ UI Layer ] (app.py & components/)
      │
      ▼
[ Service Layer ] (services/weather_service.py)
      │
      ├──────────────────────┬──────────────────────┐
      ▼                      ▼                      ▼
[ CWA API Client ]     [ Data Processing ]     [ Database Layer ]
(cwa_api.py)           (parser/formatter/icon) (db.py & queries.py)
      │                                             │
      ▼                                             ▼
[ CWA Open Data ]                              [ SQLite: weather.db ]
(F-C0032-001)
```

---

## 📂 專案結構

```bash
L3CWA/
├── app.py                      # Streamlit 應用程式主入口 (UI Layer)
├── config.py                   # 專案全域配置、環境變數與常數
├── requirements.txt            # 專案套件依賴清單
├── .gitignore                  # Git 排除清單 (.env, .db, secrets)
├── .env.example                # 環境變數設定範本
├── .streamlit/
│   └── secrets.toml.example    # Streamlit Secrets 設定範本
├── services/                   # 商業邏輯與 API 服務層
│   ├── cwa_api.py              # CWA API 請求與 HTTP/Timeout/JSON 容錯
│   └── weather_service.py      # 資料快取邏輯、資料流程協調與降級處理
├── database/                   # 資料庫存取層 (SQLite)
│   ├── db.py                   # SQLite 連線管理與 Schema 建立
│   ├── models.py               # 資料實體結構 (ForecastRecord, ApiLog)
│   └── queries.py              # SQL 查詢、Upsert 與日誌記錄
├── utils/                      # 資料處理與格式化工具
│   ├── parser.py               # F-C0032-001 JSON 解析為標準結構與 DataFrame
│   ├── formatter.py            # 時間區段與溫度格式化
│   └── weather_icon.py         # Wx 天氣描述文字轉換為 Emoji
├── components/                 # UI 視覺化模組
│   ├── weather_card.py         # 天氣資訊指標卡片
│   ├── charts.py               # Plotly 折線圖、長條圖與預報資料表
│   └── map.py                  # Folium 台灣氣象互動地圖
├── data/                       # 資料目錄 (內含 weather.db)
│   └── .gitkeep
└── tests/                      # 自動化單元測試
    ├── test_parser.py          # JSON 解析與格式化測試
    └── test_database.py        # SQLite 資料表與 Upsert 測試
```

---

## 🚀 環境需求與安裝

### 1. 系統需求
- Python 3.11 或更高版本
- 作業系統：Windows / macOS / Linux

### 2. 安裝套件
開啟終端機（Terminal）並執行：

```powershell
pip install -r requirements.txt
```

---

## 🔑 API 金鑰安全配置

本專案提供兩種配置方式（擇一即可）：

### 方法 A：使用 `.env` 檔案
1. 複製 `.env.example` 為 `.env`：
   ```powershell
   copy .env.example .env
   ```
2. 開啟 `.env` 並填入您的氣象署 API 金鑰：
   ```env
   CWA_API_KEY=CWA-XXXXXXXXXXXXXXXXXXXXXXXX
   ```

### 方法 B：使用 Streamlit Secrets
1. 複製 `.streamlit/secrets.toml.example` 為 `.streamlit/secrets.toml`：
   ```powershell
   copy .streamlit\secrets.toml.example .streamlit\secrets.toml
   ```
2. 填入 API 金鑰：
   ```toml
   CWA_API_KEY = "CWA-XXXXXXXXXXXXXXXXXXXXXXXX"
   ```

> 💡 若尚未設定 API Key，系統會自動載入逼真的全台 22 縣市示範資料，確保網頁功能與圖表能順暢展示！

---

## 🖥️ 啟動與使用方式

在專案目錄下執行：

```powershell
streamlit run app.py
```

執行後瀏覽器會自動開啟 `http://localhost:8501`。

### 操作說明：
1. **切換地區**：在左側側邊欄選擇欲查詢的台灣縣市，儀表板將即時更新。
2. **資料同步**：點擊側邊欄的「🔄 更新天氣資料」按鈕，立即向氣象署拉取最新數據。
3. **互動地圖**：點擊第五區台灣地圖上的各縣市圓點，可展開詳細天氣氣溫浮動視窗。

---

## 🧪 單元測試執行

專案已配置完整的 Pytest 測試套件，涵蓋 JSON 容錯、欄位解析、Wx 圖示映射、SQLite Schema、Upsert 去重與日誌記錄：

```powershell
python -m pytest tests/ -v
```

執行結果全數通過（9/9 Passed）。

---

## 🛡️ 異常防護與優雅降級

系統在每一層皆設置了防禦性編程（Defensive Programming）：
- **API 連線中斷 / 逾時**：捕捉 `requests.exceptions.Timeout` 與 `ConnectionError`，不中斷頁面，並記錄至 `api_logs`。
- **無效回傳 / 缺欄位**：解析器具備安全轉型（`safe_float`），若氣象局短暫缺漏特定氣象欄位，自動補齊預設值。
- **SQLite 連線中斷**：使用 Context Manager 管理交易，遇例外自動 `rollback`，確保資料庫一致性。
- **降級機制 (Graceful Fallback)**：當 API 無法連線時，優先讀取 SQLite 歷史有效快取展示，並提示使用者。

---

## 📜 聲明
- 資料來源：中央氣象署 (CWA) 政府資料開放平臺 (Open Data)。
- 本專案僅供課程專題成果展示使用。

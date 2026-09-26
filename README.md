<div align="center">

# ⚡ TAIWAN WEATHER FORECAST ⚡

### 🌐 中央氣象署 36 小時天氣預報 ── Cyberpunk 科技風儀表板

[![Streamlit](https://img.shields.io/badge/Streamlit-1.64+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![CWA](https://img.shields.io/badge/CWA-Open%20Data-00BFFF?style=for-the-badge)](https://opendata.cwa.gov.tw)
[![License](https://img.shields.io/badge/License-Educational-8B5CF6?style=for-the-badge)](#)

---

**以深色科技美學 (Cyberpunk / Neon) 打造的全功能互動式氣象儀表板。**<br/>
整合中央氣象署 Open Data API，即時呈現全台 22 縣市天氣預報、環境監測指標與互動地圖，<br/>
結合霓虹光暈邊框、掃描線動畫、Glitch 特效與暗色調圖表，帶來彷彿科幻電影控制台般的視覺體驗。

</div>

---

## 📸 畫面預覽

> 以下截圖展示儀表板各功能區塊的實際運行畫面。

| 預報概況 & 環境監測 | 趨勢分析圖表 |
|:---:|:---:|
| ![Dashboard Overview](https://github.com/user-attachments/assets/placeholder-overview.png) | ![Trend Charts](https://github.com/user-attachments/assets/placeholder-charts.png) |

| 36 小時三欄式預報卡片 | 台灣各縣市互動地圖 |
|:---:|:---:|
| ![Forecast Cards](https://github.com/user-attachments/assets/placeholder-cards.png) | ![Taiwan Map](https://github.com/user-attachments/assets/placeholder-map.png) |

---

## 📑 目錄

- [核心功能介紹](#-核心功能介紹)
- [系統分層架構](#️-系統分層架構)
- [專案結構](#-專案結構)
- [技術堆疊](#-技術堆疊)
- [快速啟動指南](#-快速啟動指南)
- [單元測試](#-單元測試)
- [異常防護與優雅降級](#️-異常防護與優雅降級)
- [聲明](#-聲明)

---

## 🌟 核心功能介紹

### 1️⃣ 側邊控制欄 (Sidebar Control Panel)

儀表板左側的指揮中樞，提供完整的操控介面：

| 元素 | 說明 |
|------|------|
| 📍 **縣市下拉選單** | 全台 22 縣市即選即切，選擇後所有區塊即時刷新為該地區的最新資料 |
| 🔄 **更新天氣資料按鈕** | 手動點擊後立即清除所有快取 (`st.cache_data.clear()` + `st.cache_resource.clear()`)，強制向氣象署 API 重新發送請求，並觸發 `st.rerun()` 全頁重渲染 |
| ⏱ **最後更新時間** | 即時顯示資料庫中最近一次 API 同步的時間戳 |
| 🔁 **自動更新狀態** | 顯示「每 30 分鐘」標籤，頁面內嵌 JavaScript `setTimeout` 實現 1,800,000 毫秒自動重整 |

---

### 2️⃣ 預報概況看板 (Forecast Overview Cards)

> **所選縣市當前時段的五大核心指標，一目了然。**

以 `st.columns(5)` 橫向排列五張 Cyberpunk 風格的自訂 HTML/CSS 卡片，每張具備：
- 深色半透明背景 (`rgba(0,0,0,0.6)`) + 毛玻璃效果 (`backdrop-filter: blur`)
- 頂部漸層光條 (Cyan → Magenta)
- Hover 時浮起放大 + 光暈色變動畫

| 卡片 | 內容 | 圖示 |
|------|------|------|
| 天氣現象 | 當前天候描述 (例：晴時多雲) | 根據 Wx 關鍵字動態匹配 Emoji (☀️⛅🌧️⛈️❄️) |
| 最高氣溫 | 日間預測高溫 (°C) | 🔥 |
| 最低氣溫 | 夜間/清晨低溫 (°C) | ❄️ |
| 降雨機率 | PoP 百分比 (%) | 💧 |
| 舒適度 | 人體感受描述 (例：悶熱、舒適) | 🌿 |

---

### 3️⃣ 環境監測指標 (Environmental Metrics — AQI & UVI)

> **獨立於天氣 API 的全新環境感測區塊，雙卡片並排呈現。**

#### 🏭 空氣品質 AQI 卡片

- **大型數值顯示**：AQI 指數以 2.8rem 放大字體置中，搭配脈動呼吸動畫 (`env-pulse`)
- **動態配色**：根據 AQI 等級自動切換顏色 (良好 `#00ff88` → 危害 `#7e0023`)
- **等級徽章**：右上角顯示「良好 / 普通 / 不健康 / 危害」等標籤
- **細項指標**：PM2.5 (μg/m³)、PM10 (μg/m³)、O₃ 臭氧 (ppb)
- **監測站資訊**：顯示對應縣市測站名稱與發布時間

#### ☀️ 紫外線 UVI 卡片

- **大型數值顯示**：UVI 指數搭配等級 Emoji (😎🙂⚠️🔥☠️)
- **漸層進度條**：從 `#00ff88` (低) → `#ffff00` (中) → `#ff8c00` (高) → `#ff003c` (過量) 的漸層量表
- **刻度標尺**：底部標示 0 / 低 / 中 / 高 / 過量 / 15 刻度
- **防曬建議**：自動判斷是否「需防護」或「一般活動」
- **觀測地區**：顯示當前選取的縣市

> 📌 **資料來源**：目前以 Mock Data 模擬，後續可替換為環境部 AQI API (`aqx_p_432`) 及氣象署 UVI API (`O-A0005-001`)，僅需修改 `services/env_api.py`，UI 零變動。

---

### 4️⃣ 趨勢分析 (Trend Analysis Charts)

使用 Plotly 深色主題 (`plotly_dark`) 繪製的兩組圖表，以 `st.columns([3, 2])` 左右排列：

#### 🌡️ 未來 36 小時氣溫趨勢 (左側 — 60% 寬)

- **雙線平滑折線圖** (`shape="spline"`)
- 🔴 **最高氣溫 (MaxT)**：Neon Red (`#ff003c`) 折線 + 數值標註
- 🔵 **最低氣溫 (MinT)**：Neon Blue (`#00f0ff`) 折線 + 數值標註
- X 軸以 `MM/DD (週) HH:MM ~ HH:MM` 格式顯示可讀時段
- 完全透明背景，與深色主題無縫融合

#### 💧 降雨機率分析 (右側 — 40% 寬)

- **直方圖 (Bar Chart)**：Neon Purple (`#d900ff`) 色柱
- 每根柱子標註百分比數值
- Y 軸範圍固定 0–105%，`dtick=20` 便於判讀
- Hover 顯示時段與精確機率

---

### 5️⃣ 未來 36 小時詳細預報 (36-Hour Forecast Cards)

> **捨棄傳統表格，改以三欄式透視卡片呈現近期、中期、後期預報。**

以 `st.columns(3)` 排列三張沉浸式卡片：

| 設計元素 | 實現細節 |
|----------|----------|
| 🏷️ **時段標籤** | 頂部粉紅霓虹字 `▸ 近期預報` / `▸ 中期預報` / `▸ 後期預報`，3px letter-spacing |
| ⏰ **時間區段** | 柔和 Cyan 色顯示 `MM/DD (週) HH:MM ~ HH:MM` |
| 🌤️ **天氣圖示** | 3rem 放大 Emoji，帶 `drop-shadow` 光暈 + 上下浮動動畫 (`fc36-float`, 3s infinite) |
| 🌡️ **溫度區間** | 最高溫 `#ff4d6a` 紅光 / 最低溫 `#00d4ff` 藍光，左右對齊排列 |
| 💧 **降雨機率** | 依風險動態配色 — 低 `#00ff88` / 中 `#ffaa00` / 高 `#ff003c` |
| 🌿 **舒適度** | 人體感受描述 |
| ✨ **卡片外框** | 16px 圓角 + Cyan/Magenta 漸層頂部光條 + Hover 浮起 + 光暈邊框擴散 |

---

### 6️⃣ 台灣縣市天氣概況地圖 (Interactive Weather Map)

> **全台 22 縣市的天氣熱點一覽，互動式地圖體驗。**

- **底圖**：CARTO Dark Matter 暗色 raster tile，完美搭配 Cyberpunk 主題
- **動態標記**：各縣市以 12px 霓虹圓點標示，顏色依最高氣溫自動變化：
  - 🔴 ≥33°C Neon Red | 🟠 ≥30°C Neon Orange | 🟢 ≥26°C Neon Green
  - 🔵 ≥22°C Neon Blue | 🟣 <22°C Neon Purple
- **脈動動畫**：圓點帶有 `pulse-node` 呼吸動畫 (1.5s infinite alternate)
- **點擊彈窗**：點擊圓點展開 Popup，內含：
  - 縣市名稱 + 天氣 Emoji
  - 天氣概況、最高溫 (紅)、最低溫 (藍)、降雨機率 (紫)、人體舒適度 (綠)
  - 全部使用 Cyberpunk 風格內嵌 CSS 渲染
- **Tooltip**：滑鼠懸停顯示 `縣市名：最高溫 / 降雨機率`

---

## 🏗️ 系統分層架構

本專題完全遵循責任分離原則（Separation of Concerns）：

```
[ UI Layer ] (app.py & components/)
      │
      ▼
[ Service Layer ] (services/weather_service.py, services/env_api.py)
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
AIoT_L3_CWA/
├── app.py                          # Streamlit 應用程式主入口 (UI Layer)
├── config.py                       # 全域配置、環境變數、座標常數
├── requirements.txt                # 套件依賴清單
├── .gitignore                      # Git 排除清單
├── .env.example                    # 環境變數設定範本
├── .streamlit/
│   └── secrets.toml.example        # Streamlit Secrets 設定範本
│
├── services/                       # 商業邏輯與 API 服務層
│   ├── cwa_api.py                  # CWA API 請求 + HTTP/Timeout/JSON 容錯
│   ├── weather_service.py          # 資料快取邏輯、資料流程協調與降級處理
│   └── env_api.py                  # 🆕 AQI/UVI 環境指標服務 (獨立於天氣 API)
│
├── database/                       # 資料庫存取層 (SQLite)
│   ├── db.py                       # SQLite 連線管理與 Schema 建立
│   ├── models.py                   # 資料實體結構 (ForecastRecord, ApiLog)
│   └── queries.py                  # SQL 查詢、Upsert 與日誌記錄
│
├── utils/                          # 資料處理與格式化工具
│   ├── parser.py                   # F-C0032-001 JSON 解析為標準結構
│   ├── formatter.py                # 時間區段與溫度格式化
│   └── weather_icon.py             # Wx 天氣描述 → Emoji 映射
│
├── components/                     # UI 視覺化模組
│   ├── cyberpunk_css.py            # 全域 Cyberpunk CSS 注入 (字型、動畫、捲軸)
│   ├── weather_card.py             # 即時天氣指標五卡片
│   ├── charts.py                   # Plotly 氣溫折線圖、降雨機率圖、預報表格
│   ├── forecast_cards.py           # 🆕 36h 三欄式霓虹預報卡片
│   ├── env_indicators.py           # 🆕 AQI/UVI 環境指標雙卡片
│   └── map.py                      # Folium 台灣氣象互動地圖
│
├── data/                           # 資料目錄 (weather.db 自動生成)
│   └── .gitkeep
└── tests/                          # 自動化單元測試
    ├── test_parser.py              # JSON 解析與格式化測試
    └── test_database.py            # SQLite Schema 與 Upsert 測試
```

---

## 🔧 技術堆疊

| 類別 | 技術 |
|------|------|
| **語言** | Python 3.11+ |
| **Web 框架** | Streamlit 1.64+ |
| **視覺化** | Plotly (折線圖、長條圖)、Folium + streamlit-folium (互動地圖) |
| **前端樣式** | 自訂 HTML/CSS (Cyberpunk 主題)、Google Fonts (Share Tech Mono, Fira Code) |
| **資料庫** | SQLite (快取與持久化) |
| **API 來源** | 中央氣象署 CWA Open Data (F-C0032-001)、CARTO Dark Matter 地圖底圖 |
| **環境指標** | 環境部 AQI API / 氣象署 UVI API (預留介面，目前 Mock Data) |
| **套件管理** | pip + requirements.txt |
| **測試** | pytest |
| **部署** | Streamlit Community Cloud |

---

## 🚀 快速啟動指南

### 1. 複製專案

```bash
git clone https://github.com/Kelly0713/AIoT_L3_CWA.git
cd AIoT_L3_CWA
```

### 2. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 3. 設定 API 金鑰

本專案提供兩種配置方式（擇一即可）：

#### 方法 A：使用 `.env` 檔案

```bash
# 複製範本
cp .env.example .env    # Linux/macOS
copy .env.example .env  # Windows
```

編輯 `.env`，填入您的 API 金鑰：

```env
# 中央氣象署 API Key (必填)
# 請至 https://opendata.cwa.gov.tw/ 註冊取得
CWA_API_KEY=CWA-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX

# CARTO 地圖 API Key (選填，可提升地圖品質)
MAP_API_KEY=YOUR_MAP_API_KEY_HERE
```

#### 方法 B：使用 Streamlit Secrets (適用 Cloud 部署)

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

編輯 `secrets.toml`：

```toml
CWA_API_KEY = "CWA-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
MAP_API_KEY = "YOUR_MAP_API_KEY_HERE"
```

> 💡 **免金鑰也能運行！** 若未設定 API Key，系統會自動載入全台 22 縣市的逼真示範資料，所有圖表與功能皆可正常展示。

### 4. 啟動應用

```bash
streamlit run app.py
```

瀏覽器將自動開啟 `http://localhost:8501`，即可看到完整的 Cyberpunk 天氣儀表板。

### 操作提示

| 操作 | 說明 |
|------|------|
| 🔽 **切換地區** | 側邊欄下拉選單選擇縣市，全頁即時刷新 |
| 🔄 **手動更新** | 點擊「更新天氣資料」按鈕，強制清除快取並重新抓取 API |
| ⏰ **自動更新** | 頁面每 30 分鐘自動重整，無需手動操作 |
| 🗺️ **地圖互動** | 點擊地圖上的霓虹圓點，查看該縣市詳細天候資訊 |

---

## 🧪 單元測試

專案配置完整的 Pytest 測試套件，涵蓋 JSON 容錯、欄位解析、Wx 圖示映射、SQLite Schema 與 Upsert 去重：

```bash
python -m pytest tests/ -v
```

---

## 🛡️ 異常防護與優雅降級

系統在每一層皆設置了防禦性編程（Defensive Programming）：

| 層級 | 防護策略 |
|------|----------|
| **API 連線** | 捕捉 `Timeout`、`ConnectionError`、`SSLError` (自動切換備援連線模式)，並記錄至 `api_logs` |
| **JSON 解析** | `safe_float()` 安全轉型，缺漏欄位自動補預設值，無效 JSON 不崩潰 |
| **資料庫** | Context Manager 管理交易，例外自動 `rollback`，確保一致性 |
| **降級機制** | API 無法連線時優先讀取 SQLite 歷史快取；未設定 API Key 時自動載入示範資料 |
| **UI 層** | 各元件獨立渲染，單一區塊資料異常不影響其餘功能 |

---

## 📜 聲明

- 氣象資料來源：[中央氣象署 (CWA) 政府資料開放平臺](https://opendata.cwa.gov.tw/)
- 地圖底圖：[CARTO](https://carto.com/) Dark Matter Basemaps
- 本專案僅供課程專題成果展示使用

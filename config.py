"""專案全域配置與常數設定模組.

負責管理環境變數、API 端點、快取時間與地理座標等全域配置。
"""

import os
from pathlib import Path
from typing import Dict, Tuple
from dotenv import load_dotenv

# 基礎專案路徑
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "weather.db"

# 載入 .env 檔案（如果存在）
load_dotenv(BASE_DIR / ".env")

# CWA API 相關配置
CWA_API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
API_TIMEOUT_SECONDS = 15
CACHE_TTL_SECONDS = 3600  # 資料庫資料快取時效：1 小時

# Thunderforest 地圖底圖 API
THUNDERFOREST_TILE_URL = "https://tile.thunderforest.com/atlas/{z}/{x}/{y}.png?apikey={apikey}"
THUNDERFOREST_ATTR = '&copy; <a href="https://www.thunderforest.com/">Thunderforest</a>, &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'


def get_cwa_api_key() -> str:
    """安全獲取中央氣象署 API 金鑰.

    優先順序：
    1. Streamlit Secrets (st.secrets["CWA_API_KEY"])
    2. 系統環境變數或 .env 檔案 (os.getenv("CWA_API_KEY"))

    Returns:
        str: API Key，若未設定則回傳空字串。
    """
    # 嘗試從 Streamlit Secrets 讀取
    try:
        import streamlit as st

        if hasattr(st, "secrets") and "CWA_API_KEY" in st.secrets:
            key = st.secrets["CWA_API_KEY"]
            if key and key.strip():
                return key.strip()
    except Exception:
        pass

    # 嘗試從環境變數讀取
    env_key = os.getenv("CWA_API_KEY", "")
    return env_key.strip() if env_key else ""


def get_map_api_key() -> str:
    """安全獲取 Thunderforest 地圖 API 金鑰.

    優先順序：
    1. Streamlit Secrets (st.secrets["MAP_API_KEY"])
    2. 系統環境變數或 .env 檔案 (os.getenv("MAP_API_KEY"))

    Returns:
        str: 地圖 API Key，若未設定則回傳空字串。
    """
    try:
        import streamlit as st

        if hasattr(st, "secrets") and "MAP_API_KEY" in st.secrets:
            key = st.secrets["MAP_API_KEY"]
            if key and key.strip():
                return key.strip()
    except Exception:
        pass

    env_key = os.getenv("MAP_API_KEY", "")
    return env_key.strip() if env_key else ""


# 台灣各縣市中心點經緯度座標 (供 Folium 繪圖使用)
CITY_COORDINATES: Dict[str, Tuple[float, float]] = {
    "基隆市": (25.1276, 121.7392),
    "臺北市": (25.0330, 121.5654),
    "新北市": (25.0169, 121.4627),
    "桃園市": (24.9936, 121.3010),
    "新竹市": (24.8138, 120.9675),
    "新竹縣": (24.8387, 121.0177),
    "苗栗縣": (24.5602, 120.8214),
    "臺中市": (24.1477, 120.6736),
    "彰化縣": (24.0518, 120.5161),
    "南投縣": (23.9609, 120.9719),
    "雲林縣": (23.7092, 120.4313),
    "嘉義市": (23.4800, 120.4491),
    "嘉義縣": (23.4518, 120.2559),
    "臺南市": (22.9997, 120.2270),
    "高雄市": (22.6273, 120.3014),
    "屏東縣": (22.5519, 120.5487),
    "宜蘭縣": (24.7021, 121.7377),
    "花蓮縣": (23.9871, 121.6015),
    "臺東縣": (22.7583, 121.1444),
    "澎湖縣": (23.5711, 119.5793),
    "金門縣": (24.4493, 118.3766),
    "連江縣": (26.1505, 119.9499),
}

# 預設展示縣市
DEFAULT_REGION = "臺北市"

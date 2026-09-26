"""環境指標資料服務 (AQI / UVI).

獨立於原有天氣 API 的新服務，負責取得空氣品質 (AQI) 與紫外線 (UVI) 資料。
目前以 Mock Data 實作，後續可替換為真實 API 串接（如環境部 OpenData）。

⚠️ 此模組不會修改任何原有 services/ 檔案。
"""

import logging
import random
from dataclasses import dataclass
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


@dataclass
class AQIData:
    """空氣品質指標資料."""
    aqi: int
    status: str          # 良好 / 普通 / 對敏感族群不健康 / 不健康 / 非常不健康 / 危害
    pm25: float
    pm10: float
    o3: float
    station: str         # 監測站名稱
    publish_time: str    # 發布時間


@dataclass
class UVIData:
    """紫外線指標資料."""
    uvi: float
    level: str           # 低量級 / 中量級 / 高量級 / 過量級 / 危險級
    county: str
    publish_time: str


# AQI 等級對照
AQI_LEVELS = [
    (50,  "良好",          "#00ff88", "😊"),
    (100, "普通",          "#ffff00", "🙂"),
    (150, "對敏感族群不健康", "#ff8c00", "😐"),
    (200, "不健康",        "#ff003c", "😷"),
    (300, "非常不健康",    "#990099", "🤢"),
    (500, "危害",          "#7e0023", "☠️"),
]

# UVI 等級對照
UVI_LEVELS = [
    (2,  "低量級",   "#00ff88", "😎"),
    (5,  "中量級",   "#ffff00", "🙂"),
    (7,  "高量級",   "#ff8c00", "⚠️"),
    (10, "過量級",   "#ff003c", "🔥"),
    (99, "危險級",   "#990099", "☠️"),
]


def get_aqi_level_info(aqi: int) -> Dict[str, str]:
    """根據 AQI 數值回傳等級、顏色與表情."""
    for threshold, label, color, emoji in AQI_LEVELS:
        if aqi <= threshold:
            return {"status": label, "color": color, "emoji": emoji}
    return {"status": "危害", "color": "#7e0023", "emoji": "☠️"}


def get_uvi_level_info(uvi: float) -> Dict[str, str]:
    """根據 UVI 數值回傳等級、顏色與表情."""
    for threshold, label, color, emoji in UVI_LEVELS:
        if uvi <= threshold:
            return {"level": label, "color": color, "emoji": emoji}
    return {"level": "危險級", "color": "#990099", "emoji": "☠️"}


def fetch_aqi_data(region_name: str) -> Optional[AQIData]:
    """取得指定地區的 AQI 資料.

    ⚠️ 目前為 Mock Data 實作。
    TODO: 串接環境部 AQI OpenData API
    https://data.moenv.gov.tw/api/v2/aqx_p_432

    Args:
        region_name: 縣市名稱 (如「臺北市」)。

    Returns:
        AQIData 或 None。
    """
    # --- Mock Data ---
    # 依地區產生合理範圍的假資料（可直接替換為 API 呼叫）
    random.seed(hash(region_name) % 1000)  # 同一地區每次結果一致
    base_aqi = {
        "臺北市": 45, "新北市": 55, "桃園市": 60, "臺中市": 72,
        "臺南市": 68, "高雄市": 85, "基隆市": 38, "新竹市": 52,
        "新竹縣": 50, "苗栗縣": 48, "彰化縣": 70, "南投縣": 42,
        "雲林縣": 75, "嘉義市": 65, "嘉義縣": 63, "屏東縣": 58,
        "宜蘭縣": 35, "花蓮縣": 28, "臺東縣": 25, "澎湖縣": 30,
        "金門縣": 55, "連江縣": 32,
    }
    aqi_val = base_aqi.get(region_name, 50) + random.randint(-5, 10)
    aqi_val = max(0, min(aqi_val, 500))
    level_info = get_aqi_level_info(aqi_val)

    return AQIData(
        aqi=aqi_val,
        status=level_info["status"],
        pm25=round(aqi_val * 0.35 + random.uniform(-2, 5), 1),
        pm10=round(aqi_val * 0.55 + random.uniform(-3, 8), 1),
        o3=round(random.uniform(20, 80), 1),
        station=f"{region_name}測站",
        publish_time="2026-09-26 11:00 (模擬資料)",
    )


def fetch_uvi_data(region_name: str) -> Optional[UVIData]:
    """取得指定地區的紫外線指數資料.

    ⚠️ 目前為 Mock Data 實作。
    TODO: 串接氣象署 UVI OpenData API
    https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0005-001

    Args:
        region_name: 縣市名稱。

    Returns:
        UVIData 或 None。
    """
    # --- Mock Data ---
    random.seed(hash(region_name + "_uvi") % 1000)
    base_uvi = {
        "臺北市": 7.5, "新北市": 7.2, "桃園市": 7.8, "臺中市": 8.5,
        "臺南市": 9.2, "高雄市": 9.8, "基隆市": 6.5, "新竹市": 7.0,
        "新竹縣": 6.8, "苗栗縣": 7.5, "彰化縣": 8.0, "南投縣": 8.2,
        "雲林縣": 8.5, "嘉義市": 8.8, "嘉義縣": 8.6, "屏東縣": 9.5,
        "宜蘭縣": 6.8, "花蓮縣": 8.0, "臺東縣": 9.0, "澎湖縣": 10.5,
        "金門縣": 7.5, "連江縣": 5.8,
    }
    uvi_val = base_uvi.get(region_name, 7.0) + round(random.uniform(-1.5, 1.5), 1)
    uvi_val = max(0, round(uvi_val, 1))
    level_info = get_uvi_level_info(uvi_val)

    return UVIData(
        uvi=uvi_val,
        level=level_info["level"],
        county=region_name,
        publish_time="2026-09-26 11:00 (模擬資料)",
    )

"""數值與時間格式化工具模組 (Formatter).

提供氣象資訊展示的標準化時間字串、溫度、降雨機率等格式化轉換。
"""

from datetime import datetime
from typing import Optional


WEEKDAY_MAP = {
    0: "一",
    1: "二",
    2: "三",
    3: "四",
    4: "五",
    5: "六",
    6: "日",
}


def format_forecast_time_range(start_str: str, end_str: str) -> str:
    """將開始與結束時間格式化為易讀時段（例如：09/23 (三) 12:00 ~ 09/23 18:00）.

    Args:
        start_str: 開始時間字串 (YYYY-MM-DD HH:MM:SS)
        end_str: 結束時間字串 (YYYY-MM-DD HH:MM:SS)

    Returns:
        str: 友善時段描述。
    """
    try:
        dt_start = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
        dt_end = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
        weekday = WEEKDAY_MAP.get(dt_start.weekday(), "")

        # 如果同一天
        if dt_start.date() == dt_end.date():
            return f"{dt_start.strftime('%m/%d')} ({weekday}) {dt_start.strftime('%H:%M')} ~ {dt_end.strftime('%H:%M')}"
        else:
            end_weekday = WEEKDAY_MAP.get(dt_end.weekday(), "")
            return f"{dt_start.strftime('%m/%d')} ({weekday}) {dt_start.strftime('%H:%M')} ~ {dt_end.strftime('%m/%d')} ({end_weekday}) {dt_end.strftime('%H:%M')}"
    except Exception:
        return f"{start_str} ~ {end_str}"


def format_temperature(val: Optional[float]) -> str:
    """格式化溫度值（例如：28 °C）."""
    if val is None:
        return "-- °C"
    return f"{int(round(val))}°C" if val == round(val) else f"{val:.1f}°C"


def format_precipitation(val: Optional[float]) -> str:
    """格式化降雨機率百分比（例如：30%）."""
    if val is None:
        return "--%"
    return f"{int(round(val))}%"

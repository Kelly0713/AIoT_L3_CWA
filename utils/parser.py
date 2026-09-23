"""中央氣象署 (CWA) F-C0032-001 天氣預報 JSON 解析模組.

負責將 CWA API 回傳的原始巢狀 JSON 資料結構，提取、驗證並轉換為標準的
ForecastRecord 物件清單與 Pandas DataFrame。
完全將外部 API 資料格式與系統內部資料模型解耦。
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd

from database.models import ForecastRecord

logger = logging.getLogger(__name__)


def safe_float(value: Any, default: float = 0.0) -> float:
    """安全轉換數值為浮點數，遇到 None 或轉換失敗時使用預設值."""
    if value is None:
        return default
    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        return default


def parse_cwa_forecast_json(raw_json: Dict[str, Any]) -> List[ForecastRecord]:
    """解析 CWA F-C0032-001 原始 JSON.

    Args:
        raw_json: CWA API 回傳的字典資料。

    Returns:
        List[ForecastRecord]: 解析完成的標準預報物件清單。

    Raises:
        ValueError: 若資料格式非有效 JSON 字典或缺少必要 records 節點。
    """
    if not isinstance(raw_json, dict):
        raise ValueError("無效的 JSON 格式：預期為 dict 物件")

    records_node = raw_json.get("records")
    if not isinstance(records_node, dict):
        raise ValueError("JSON 資料中缺少 'records' 根節點")

    # 取得發布時間 (若 API 未提供則使用當前時間字串)
    issue_time = (
        records_node.get("datasetDescription")
        or raw_json.get("result", {}).get("resource_id")
        or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    fetched_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    location_list = records_node.get("location", [])
    if not isinstance(location_list, list):
        logger.warning("records 內無有效的 location 清單")
        return []

    parsed_records: List[ForecastRecord] = []

    for loc in location_list:
        if not isinstance(loc, dict):
            continue

        region_name = loc.get("locationName", "").strip()
        if not region_name:
            continue

        weather_elements = loc.get("weatherElement", [])
        if not isinstance(weather_elements, list):
            continue

        # 整理該地區各時段元素：(start_time, end_time) -> { 'Wx': ..., 'PoP': ..., ... }
        intervals_map: Dict[tuple, Dict[str, str]] = {}

        for elem in weather_elements:
            if not isinstance(elem, dict):
                continue
            elem_name = elem.get("elementName", "")
            time_entries = elem.get("time", [])

            for t_entry in time_entries:
                if not isinstance(t_entry, dict):
                    continue
                start_time = t_entry.get("startTime", "")
                end_time = t_entry.get("endTime", "")
                if not start_time or not end_time:
                    continue

                param = t_entry.get("parameter", {})
                param_name = param.get("parameterName", "") if isinstance(param, dict) else ""

                interval_key = (start_time, end_time)
                if interval_key not in intervals_map:
                    intervals_map[interval_key] = {}
                intervals_map[interval_key][elem_name] = param_name

        # 將整理出的各時段組合成 ForecastRecord
        for (start_t, end_t), val_dict in sorted(intervals_map.items()):
            weather_desc = val_dict.get("Wx", "多雲")
            pop_val = safe_float(val_dict.get("PoP", 0.0))
            min_temp_val = safe_float(val_dict.get("MinT", 20.0))
            max_temp_val = safe_float(val_dict.get("MaxT", 28.0))
            comfort_desc = val_dict.get("CI", "舒適")

            record = ForecastRecord(
                region_name=region_name,
                forecast_start=start_t,
                forecast_end=end_t,
                weather=weather_desc,
                min_temp=min_temp_val,
                max_temp=max_temp_val,
                precipitation=pop_val,
                comfort=comfort_desc,
                issue_time=str(issue_time),
                fetched_at=fetched_at,
            )
            parsed_records.append(record)

    logger.info("成功解析 %d 筆天氣預報紀錄 (涵蓋 %d 個地區)", len(parsed_records), len(location_list))
    return parsed_records


def records_to_dataframe(records: List[ForecastRecord]) -> pd.DataFrame:
    """將 ForecastRecord 清單轉換為 Pandas DataFrame 供分析與繪圖使用."""
    if not records:
        return pd.DataFrame(
            columns=[
                "region_name",
                "forecast_start",
                "forecast_end",
                "weather",
                "min_temp",
                "max_temp",
                "precipitation",
                "comfort",
                "issue_time",
                "fetched_at",
            ]
        )

    data = [r.to_dict() for r in records]
    df = pd.DataFrame(data)
    # 確保數值型別正確
    df["min_temp"] = pd.to_numeric(df["min_temp"], errors="coerce")
    df["max_temp"] = pd.to_numeric(df["max_temp"], errors="coerce")
    df["precipitation"] = pd.to_numeric(df["precipitation"], errors="coerce")
    return df

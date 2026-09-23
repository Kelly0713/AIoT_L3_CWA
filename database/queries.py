"""SQLite 資料庫查詢與更新模組 (Queries).

實作對 weather_forecasts 與 api_logs 資料表的各項 SQL 操作。
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from database.db import get_db_context
from database.models import ForecastRecord

logger = logging.getLogger(__name__)


def upsert_forecasts(records: List[ForecastRecord], db_path: Optional[Path] = None) -> int:
    """批次寫入或更新預報資料（利用 UNIQUE 限制防重複寫入）.

    Args:
        records: 預報資料物件清單。
        db_path: 資料庫檔案路徑。

    Returns:
        int: 寫入/更新的筆數。
    """
    if not records:
        return 0

    sql = """
    INSERT INTO weather_forecasts (
        region_name, forecast_start, forecast_end, weather,
        min_temp, max_temp, precipitation, comfort,
        issue_time, fetched_at
    ) VALUES (
        :region_name, :forecast_start, :forecast_end, :weather,
        :min_temp, :max_temp, :precipitation, :comfort,
        :issue_time, :fetched_at
    )
    ON CONFLICT(region_name, forecast_start, forecast_end) DO UPDATE SET
        weather = excluded.weather,
        min_temp = excluded.min_temp,
        max_temp = excluded.max_temp,
        precipitation = excluded.precipitation,
        comfort = excluded.comfort,
        issue_time = excluded.issue_time,
        fetched_at = excluded.fetched_at;
    """

    with get_db_context(db_path) as conn:
        cursor = conn.cursor()
        cursor.executemany(sql, [r.to_dict() for r in records])
        affected = cursor.rowcount
        logger.info("已成功寫入/更新 %d 筆氣象預報資料", len(records))
        return affected


def get_forecasts_by_region(region_name: str, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """根據縣市名稱查詢該地區未來的時段預報（依 forecast_start 排序）.

    Args:
        region_name: 縣市名稱（例如：臺北市、高雄市）。
        db_path: 資料庫檔案路徑。

    Returns:
        List[Dict[str, Any]]: 該縣市各預報時段資料字典清單。
    """
    sql = """
    SELECT id, region_name, forecast_start, forecast_end, weather,
           min_temp, max_temp, precipitation, comfort, issue_time, fetched_at
    FROM weather_forecasts
    WHERE region_name = ?
    ORDER BY forecast_start ASC
    LIMIT 10;
    """
    with get_db_context(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (region_name,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_all_regions(db_path: Optional[Path] = None) -> List[str]:
    """取得資料庫中所有具備預報資料的縣市清單.

    Args:
        db_path: 資料庫檔案路徑。

    Returns:
        List[str]: 縣市名稱清單。
    """
    sql = """
    SELECT DISTINCT region_name
    FROM weather_forecasts
    ORDER BY region_name ASC;
    """
    with get_db_context(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        return [row["region_name"] for row in rows]


def get_latest_summary_all_regions(db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """取得全台各縣市最新時段之天氣概況（供全島地圖與概覽使用）.

    每個縣市僅取 forecast_start 最早（當前）的一筆。

    Returns:
        List[Dict[str, Any]]: 各縣市當前時段資料清單。
    """
    sql = """
    WITH RankedForecasts AS (
        SELECT id, region_name, forecast_start, forecast_end, weather,
               min_temp, max_temp, precipitation, comfort, issue_time, fetched_at,
               ROW_NUMBER() OVER (PARTITION BY region_name ORDER BY forecast_start ASC) as rn
        FROM weather_forecasts
    )
    SELECT id, region_name, forecast_start, forecast_end, weather,
           min_temp, max_temp, precipitation, comfort, issue_time, fetched_at
    FROM RankedForecasts
    WHERE rn = 1;
    """
    with get_db_context(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_latest_fetch_time(db_path: Optional[Path] = None) -> Optional[str]:
    """取得資料庫中最新一筆資料的取得時間 (fetched_at)."""
    sql = "SELECT MAX(fetched_at) as latest_fetch FROM weather_forecasts;"
    with get_db_context(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        return row["latest_fetch"] if row and row["latest_fetch"] else None


def log_api_call(status: str, message: str, issue_time: Optional[str] = None, db_path: Optional[Path] = None) -> None:
    """記錄 API 呼叫結果至 api_logs 資料表."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = """
    INSERT INTO api_logs (issue_time, fetched_at, status, message)
    VALUES (?, ?, ?, ?);
    """
    try:
        with get_db_context(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (issue_time or "", now_str, status, message))
    except Exception as e:
        logger.error("無法寫入 API 日誌: %s", e)


def get_recent_api_logs(limit: int = 5, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """取得最近的 API 呼叫日誌."""
    sql = """
    SELECT id, issue_time, fetched_at, status, message
    FROM api_logs
    ORDER BY id DESC
    LIMIT ?;
    """
    try:
        with get_db_context(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error("無法讀取 API 日誌: %s", e)
        return []

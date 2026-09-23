"""單元測試：SQLite 資料庫操作與模型 (test_database.py)."""

import pytest
from pathlib import Path
from database.db import init_db, get_db_context
from database.models import ForecastRecord
from database.queries import (
    upsert_forecasts,
    get_forecasts_by_region,
    get_all_regions,
    get_latest_summary_all_regions,
    get_latest_fetch_time,
    log_api_call,
    get_recent_api_logs,
)


@pytest.fixture
def temp_db(tmp_path: Path):
    """建立臨時 SQLite 資料庫 fixture."""
    db_file = tmp_path / "test_weather.db"
    init_db(db_file)
    return db_file


def test_db_initialization(temp_db):
    """測試資料表結構建立."""
    with get_db_context(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row["name"] for row in cursor.fetchall()]
        assert "weather_forecasts" in tables
        assert "api_logs" in tables


def test_upsert_and_unique_constraint(temp_db):
    """測試資料寫入與防重複 (ON CONFLICT DO UPDATE) 約束機制."""
    r1 = ForecastRecord(
        region_name="新北市",
        forecast_start="2026-09-23 12:00:00",
        forecast_end="2026-09-23 18:00:00",
        weather="陰天",
        min_temp=24.0,
        max_temp=30.0,
        precipitation=20.0,
        comfort="舒適",
        issue_time="2026-09-23 11:00:00",
        fetched_at="2026-09-23 11:30:00",
    )
    upsert_forecasts([r1], temp_db)

    results = get_forecasts_by_region("新北市", temp_db)
    assert len(results) == 1
    assert results[0]["weather"] == "陰天"
    assert results[0]["max_temp"] == 30.0

    # 再次寫入相同時段但更新氣象內容
    r1_updated = ForecastRecord(
        region_name="新北市",
        forecast_start="2026-09-23 12:00:00",
        forecast_end="2026-09-23 18:00:00",
        weather="雷雨",
        min_temp=23.0,
        max_temp=29.0,
        precipitation=80.0,
        comfort="潮濕",
        issue_time="2026-09-23 11:30:00",
        fetched_at="2026-09-23 12:00:00",
    )
    upsert_forecasts([r1_updated], temp_db)

    # 筆數仍應為 1，但數值已更新
    results_after = get_forecasts_by_region("新北市", temp_db)
    assert len(results_after) == 1
    assert results_after[0]["weather"] == "雷雨"
    assert results_after[0]["max_temp"] == 29.0
    assert results_after[0]["precipitation"] == 80.0


def test_get_all_regions_and_summary(temp_db):
    """測試多地區與概況摘要查詢."""
    records = [
        ForecastRecord(
            region_name="臺中市",
            forecast_start="2026-09-23 12:00:00",
            forecast_end="2026-09-23 18:00:00",
            weather="晴",
            min_temp=26.0,
            max_temp=33.0,
            precipitation=10.0,
            comfort="熱",
            issue_time="2026-09-23 10:00:00",
            fetched_at="2026-09-23 10:30:00",
        ),
        ForecastRecord(
            region_name="高雄市",
            forecast_start="2026-09-23 12:00:00",
            forecast_end="2026-09-23 18:00:00",
            weather="多雲",
            min_temp=27.0,
            max_temp=32.0,
            precipitation=15.0,
            comfort="悶熱",
            issue_time="2026-09-23 10:00:00",
            fetched_at="2026-09-23 10:30:00",
        ),
    ]
    upsert_forecasts(records, temp_db)

    regions = get_all_regions(temp_db)
    assert "臺中市" in regions
    assert "高雄市" in regions

    summary = get_latest_summary_all_regions(temp_db)
    assert len(summary) == 2

    latest_time = get_latest_fetch_time(temp_db)
    assert latest_time == "2026-09-23 10:30:00"


def test_api_logs(temp_db):
    """測試 API 呼叫日誌紀錄與讀取."""
    log_api_call("SUCCESS", "已成功更新 22 縣市資料", "2026-09-23 12:00", temp_db)
    log_api_call("ERROR", "API 連線逾時", None, temp_db)

    logs = get_recent_api_logs(limit=10, db_path=temp_db)
    assert len(logs) == 2
    assert logs[0]["status"] == "ERROR"
    assert logs[1]["status"] == "SUCCESS"

"""SQLite 資料庫連線與結構管理模組.

負責資料庫的建立、連線管理與 Schema 初始化。
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from config import DB_PATH

logger = logging.getLogger(__name__)


def get_db_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """建立並取得 SQLite 資料庫連線.

    Args:
        db_path: 資料庫檔案路徑，預設使用 config.DB_PATH。

    Returns:
        sqlite3.Connection: 資料庫連線物件。

    Raises:
        sqlite3.Error: 當資料庫無法連線時拋出。
    """
    target_path = db_path or DB_PATH
    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(target_path), timeout=10.0)
        conn.row_factory = sqlite3.Row  # 允許使用欄位名稱存取
        conn.execute("PRAGMA journal_mode = WAL;")  # 提升高並發讀寫效能
        return conn
    except sqlite3.Error as e:
        logger.error("無法建立 SQLite 連線: %s, 錯誤: %s", target_path, e)
        raise


@contextmanager
def get_db_context(db_path: Optional[Path] = None):
    """上下文管理器：安全管理 SQLite 連線與交易 commit/rollback.

    Args:
        db_path: 資料庫檔案路徑。
    """
    conn = get_db_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error("資料庫交易異常執行 rollback: %s", e)
        raise
    finally:
        conn.close()


def init_db(db_path: Optional[Path] = None) -> None:
    """初始化 SQLite 資料表結構.

    建立：
    1. weather_forecasts：儲存 36 小時預報，具備 UNIQUE(region_name, forecast_start, forecast_end)
    2. api_logs：儲存 API 請求紀錄
    """
    create_forecasts_table = """
    CREATE TABLE IF NOT EXISTS weather_forecasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        region_name TEXT NOT NULL,
        forecast_start TEXT NOT NULL,
        forecast_end TEXT NOT NULL,
        weather TEXT,
        min_temp REAL,
        max_temp REAL,
        precipitation REAL,
        comfort TEXT,
        issue_time TEXT,
        fetched_at TEXT,
        CONSTRAINT uq_region_forecast UNIQUE (region_name, forecast_start, forecast_end)
    );
    """

    create_indices = """
    CREATE INDEX IF NOT EXISTS idx_forecasts_region ON weather_forecasts (region_name);
    CREATE INDEX IF NOT EXISTS idx_forecasts_time ON weather_forecasts (forecast_start);
    """

    create_logs_table = """
    CREATE TABLE IF NOT EXISTS api_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        issue_time TEXT,
        fetched_at TEXT,
        status TEXT,
        message TEXT
    );
    """

    with get_db_context(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(create_forecasts_table)
        cursor.executescript(create_indices)
        cursor.execute(create_logs_table)
        logger.info("SQLite 資料庫初始化完成: %s", db_path or DB_PATH)

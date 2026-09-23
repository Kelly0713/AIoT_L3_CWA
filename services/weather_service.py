"""天氣業務邏輯服務層 (Weather Service).

協調整合 CWA API 客戶端、JSON 解析器與 SQLite 資料庫。
實作資料快取策略、自動刷新機制、異常降級與示範資料產生。
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from config import DB_PATH, CACHE_TTL_SECONDS, CITY_COORDINATES
from database.db import init_db
from database.models import ForecastRecord
from database.queries import (
    upsert_forecasts,
    get_forecasts_by_region,
    get_all_regions,
    get_latest_summary_all_regions,
    get_latest_fetch_time,
    log_api_call,
)
from services.cwa_api import CWAApiClient
from utils.parser import parse_cwa_forecast_json

logger = logging.getLogger(__name__)


class WeatherService:
    """氣象資訊服務層."""

    def __init__(self, db_path: Optional[Path] = None, api_client: Optional[CWAApiClient] = None):
        self.db_path = db_path or DB_PATH
        self.api_client = api_client or CWAApiClient()
        # 初始化資料庫
        self._ensure_db_ready()

    def _ensure_db_ready(self) -> None:
        """確保資料庫已初始化."""
        try:
            init_db(self.db_path)
        except Exception as e:
            logger.error("初始化資料庫失敗: %s", e)

    def is_cache_expired(self) -> bool:
        """檢查資料庫中快取資料是否已逾時或不存在.

        Returns:
            bool: True 表示需要向 API 重新獲取資料。
        """
        try:
            latest_fetch = get_latest_fetch_time(self.db_path)
            if not latest_fetch:
                return True

            fetch_time = datetime.strptime(latest_fetch, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            # 若超過快取設定時間則判定為過期
            return (now - fetch_time).total_seconds() > CACHE_TTL_SECONDS
        except Exception as e:
            logger.warning("檢查快取時效失敗，預設需刷新: %s", e)
            return True

    def refresh_weather_data(self, force: bool = False) -> Tuple[bool, str]:
        """從 CWA API 更新天氣預報資料並寫入 SQLite 資料庫.

        Args:
            force: 是否忽略快取強制更新。

        Returns:
            Tuple[bool, str]: (是否成功, 狀態或錯誤說明)
        """
        # 若非強制且快取仍有效，直接略過
        if not force and not self.is_cache_expired():
            return True, "快取有效，無需重複請求 API。"

        # 呼叫 CWA API
        response = self.api_client.fetch_forecasts()
        if not response.success:
            err = response.error_message or "API 請求失敗"
            log_api_call(status="ERROR", message=err, db_path=self.db_path)
            # 若無 API Key 且資料庫完全無資料，自動載入示範資料避免網頁空白
            if "未偵測到 CWA API Key" in err:
                existing_regions = self.get_available_regions()
                if not existing_regions:
                    self._load_sample_data()
                    return True, "已載入展示用示範預報資料（未設定 CWA_API_KEY）"
            return False, err

        # 解析 JSON
        try:
            records = parse_cwa_forecast_json(response.data)
            if not records:
                err = "解析 CWA JSON 成功但未取得任何預報紀錄"
                log_api_call(status="WARNING", message=err, db_path=self.db_path)
                return False, err

            # 寫入 SQLite
            upsert_forecasts(records, self.db_path)
            log_api_call(
                status="SUCCESS",
                message=f"成功更新 {len(records)} 筆預報紀錄",
                issue_time=records[0].issue_time if records else None,
                db_path=self.db_path,
            )
            return True, f"成功更新 {len(records)} 筆最新預報資料！"

        except Exception as e:
            err = f"解析或儲存預報資料時發生錯誤: {e}"
            logger.error(err)
            log_api_call(status="ERROR", message=err, db_path=self.db_path)
            return False, err

    def get_forecasts_for_region(self, region_name: str) -> List[Dict[str, Any]]:
        """取得指定縣市的 36 小時預報清單.

        若資料庫無資料，會自動嘗試取得一次。
        """
        records = get_forecasts_by_region(region_name, self.db_path)
        if not records:
            # 嘗試更新
            self.refresh_weather_data(force=False)
            records = get_forecasts_by_region(region_name, self.db_path)
        return records

    def get_available_regions(self) -> List[str]:
        """取得所有已儲存的縣市清單."""
        return get_all_regions(self.db_path)

    def get_all_regions_summary(self) -> List[Dict[str, Any]]:
        """取得全台各縣市最新即時概況（供全島地圖與總覽使用）."""
        summary = get_latest_summary_all_regions(self.db_path)
        if not summary:
            self.refresh_weather_data(force=False)
            summary = get_latest_summary_all_regions(self.db_path)
        return summary

    def get_last_updated_time(self) -> Optional[str]:
        """取得最後資料同步更新時間."""
        return get_latest_fetch_time(self.db_path)

    def _load_sample_data(self) -> None:
        """建立逼真的展示用預報資料（當使用者未提供 API Key 時使用）."""
        now = datetime.now()
        t1_start = now.strftime("%Y-%m-%d %H:00:00")
        t1_end = (now + timedelta(hours=12)).strftime("%Y-%m-%d %H:00:00")
        t2_start = t1_end
        t2_end = (now + timedelta(hours=24)).strftime("%Y-%m-%d %H:00:00")
        t3_start = t2_end
        t3_end = (now + timedelta(hours=36)).strftime("%Y-%m-%d %H:00:00")

        sample_weather = [
            ("晴時多雲", 24.0, 32.0, 10.0, "舒適至悶熱"),
            ("多雲午後短暫雷陣雨", 25.0, 31.0, 60.0, "悶熱"),
            ("多雲時晴", 23.0, 29.0, 20.0, "舒適"),
        ]

        records: List[ForecastRecord] = []
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")

        # 為所有縣市產生標準資料
        base_temp_offset = {
            "基隆市": -1.0, "臺北市": 0.0, "新北市": 0.0, "桃園市": -0.5,
            "新竹市": -0.5, "新竹縣": -0.5, "苗栗縣": 0.0, "臺中市": 1.0,
            "彰化縣": 1.0, "南投縣": -0.5, "雲林縣": 1.0, "嘉義市": 1.5,
            "嘉義縣": 1.5, "臺南市": 2.0, "高雄市": 2.5, "屏東縣": 2.5,
            "宜蘭縣": -1.0, "花蓮縣": 0.5, "臺東縣": 1.0, "澎湖縣": 0.5,
            "金門縣": -1.5, "連江縣": -3.0
        }

        for region in CITY_COORDINATES.keys():
            offset = base_temp_offset.get(region, 0.0)
            times = [(t1_start, t1_end), (t2_start, t2_end), (t3_start, t3_end)]
            for i, (st, et) in enumerate(times):
                w_desc, min_t, max_t, pop, ci = sample_weather[i]
                records.append(
                    ForecastRecord(
                        region_name=region,
                        forecast_start=st,
                        forecast_end=et,
                        weather=w_desc,
                        min_temp=round(min_t + offset, 1),
                        max_temp=round(max_t + offset, 1),
                        precipitation=pop,
                        comfort=ci,
                        issue_time=f"展示預報資料 - {now_str}",
                        fetched_at=now_str,
                    )
                )

        upsert_forecasts(records, self.db_path)
        logger.info("已成功寫入全台 22 縣市展示用預報資料")

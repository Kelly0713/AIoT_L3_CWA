"""資料庫實體模型 (Data Models) 模組.

定義天氣預報與 API 呼叫日誌的資料結構。
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class ForecastRecord:
    """單筆縣市時段天氣預報資料實體."""

    region_name: str
    forecast_start: str
    forecast_end: str
    weather: str
    min_temp: float
    max_temp: float
    precipitation: float
    comfort: str
    issue_time: str
    fetched_at: str
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式."""
        return asdict(self)


@dataclass
class ApiLogRecord:
    """API 請求紀錄實體."""

    status: str
    message: str
    issue_time: Optional[str] = None
    fetched_at: Optional[str] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式."""
        return asdict(self)

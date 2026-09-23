"""單元測試：CWA JSON 解析器與格式化工具 (test_parser.py)."""

import pytest
from utils.parser import parse_cwa_forecast_json, safe_float, records_to_dataframe
from utils.weather_icon import get_weather_icon
from utils.formatter import format_forecast_time_range, format_temperature, format_precipitation


def test_safe_float():
    assert safe_float("25.5") == 25.5
    assert safe_float(30) == 30.0
    assert safe_float("invalid", default=0.0) == 0.0
    assert safe_float(None, default=10.0) == 10.0


def test_weather_icon_mapping():
    assert get_weather_icon("晴時多雲") == "☀️"
    assert get_weather_icon("多雲時陰") == "⛅"
    assert get_weather_icon("陰天") == "☁️"
    assert get_weather_icon("短暫雨") == "🌧️"
    assert get_weather_icon("午後雷陣雨") == "⛈️"
    assert get_weather_icon("") == "🌤️"
    assert get_weather_icon(None) == "🌤️"


def test_formatters():
    formatted_time = format_forecast_time_range("2026-09-23 12:00:00", "2026-09-23 18:00:00")
    assert "12:00 ~ 18:00" in formatted_time
    assert format_temperature(28.0) == "28°C"
    assert format_temperature(None) == "-- °C"
    assert format_precipitation(30.0) == "30%"
    assert format_precipitation(None) == "--%"


def test_parse_cwa_forecast_json_success():
    sample_json = {
        "success": "true",
        "result": {"resource_id": "F-C0032-001"},
        "records": {
            "datasetDescription": "三十六小時天氣預報",
            "location": [
                {
                    "locationName": "臺北市",
                    "weatherElement": [
                        {
                            "elementName": "Wx",
                            "time": [
                                {
                                    "startTime": "2026-09-23 12:00:00",
                                    "endTime": "2026-09-23 18:00:00",
                                    "parameter": {"parameterName": "多雲午後雷陣雨", "parameterValue": "22"},
                                }
                            ],
                        },
                        {
                            "elementName": "PoP",
                            "time": [
                                {
                                    "startTime": "2026-09-23 12:00:00",
                                    "endTime": "2026-09-23 18:00:00",
                                    "parameter": {"parameterName": "40", "parameterUnit": "百分比"},
                                }
                            ],
                        },
                        {
                            "elementName": "MinT",
                            "time": [
                                {
                                    "startTime": "2026-09-23 12:00:00",
                                    "endTime": "2026-09-23 18:00:00",
                                    "parameter": {"parameterName": "25", "parameterUnit": "C"},
                                }
                            ],
                        },
                        {
                            "elementName": "MaxT",
                            "time": [
                                {
                                    "startTime": "2026-09-23 12:00:00",
                                    "endTime": "2026-09-23 18:00:00",
                                    "parameter": {"parameterName": "33", "parameterUnit": "C"},
                                }
                            ],
                        },
                        {
                            "elementName": "CI",
                            "time": [
                                {
                                    "startTime": "2026-09-23 12:00:00",
                                    "endTime": "2026-09-23 18:00:00",
                                    "parameter": {"parameterName": "悶熱"},
                                }
                            ],
                        },
                    ],
                }
            ],
        },
    }

    records = parse_cwa_forecast_json(sample_json)
    assert len(records) == 1
    r = records[0]
    assert r.region_name == "臺北市"
    assert r.weather == "多雲午後雷陣雨"
    assert r.min_temp == 25.0
    assert r.max_temp == 33.0
    assert r.precipitation == 40.0
    assert r.comfort == "悶熱"

    df = records_to_dataframe(records)
    assert len(df) == 1
    assert df["region_name"].iloc[0] == "臺北市"


def test_parse_cwa_forecast_invalid_json():
    with pytest.raises(ValueError):
        parse_cwa_forecast_json([])  # type: ignore

    with pytest.raises(ValueError):
        parse_cwa_forecast_json({"success": "true"})

"""未來 36 小時預報卡片元件 (Forecast Cards).

以 3 張並排的深色科技風卡片取代原有表格，每張卡片包含：
時間區段、天氣現象、最高/最低溫、降雨機率、舒適度。
"""

from typing import List, Dict, Any
import streamlit as st

from utils.formatter import format_forecast_time_range
from utils.weather_icon import get_weather_icon


def _get_precipitation_color(pop: float) -> str:
    """依降雨機率回傳對應的霓虹色彩."""
    if pop >= 70:
        return "#ff003c"  # 高降雨 → 紅
    elif pop >= 40:
        return "#ffaa00"  # 中降雨 → 橙
    else:
        return "#00ff88"  # 低降雨 → 綠


def _get_period_label(index: int) -> str:
    """依序號回傳時段名稱 (第 1~3 時段)."""
    labels = ["▸ 近期預報", "▸ 中期預報", "▸ 後期預報"]
    return labels[index] if index < len(labels) else f"▸ 時段 {index + 1}"


def render_forecast_cards_36h(records: List[Dict[str, Any]]) -> None:
    """渲染 36 小時預報為 3 張並排的 Cyberpunk 風格卡片.

    Args:
        records: 預報資料清單 (通常為 3 筆)。
    """
    if not records:
        st.info("無預報資料可顯示。")
        return

    # 注入卡片專用 CSS (使用唯一 class 名稱避免衝突)
    st.markdown("""
    <style>
    .fc36-card {
        background: rgba(5, 5, 20, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 24px 20px 20px 20px;
        border: 1px solid rgba(0, 255, 255, 0.35);
        box-shadow:
            0 0 15px rgba(0, 255, 255, 0.15),
            0 0 30px rgba(255, 0, 255, 0.08),
            inset 0 0 20px rgba(0, 255, 255, 0.05);
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        min-height: 340px;
    }
    .fc36-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, #00ffff, #ff00ff, #00ffff, transparent);
        opacity: 0.8;
    }
    .fc36-card::after {
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, #ff00ff44, transparent);
    }
    .fc36-card:hover {
        transform: translateY(-4px) scale(1.015);
        border-color: #ff00ff;
        box-shadow:
            0 0 25px rgba(255, 0, 255, 0.3),
            0 0 50px rgba(0, 255, 255, 0.15),
            inset 0 0 25px rgba(255, 0, 255, 0.08);
    }

    .fc36-period-label {
        font-size: 0.72rem;
        color: #ff00ff;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-bottom: 4px;
        font-family: 'Share Tech Mono', monospace;
        text-shadow: 0 0 4px rgba(255, 0, 255, 0.6);
    }
    .fc36-time {
        font-size: 0.82rem;
        color: #88ddff;
        margin-bottom: 16px;
        font-family: 'Share Tech Mono', monospace;
        line-height: 1.4;
        opacity: 0.9;
    }
    .fc36-weather-icon {
        font-size: 3rem;
        margin: 8px 0 4px 0;
        filter: drop-shadow(0 0 8px rgba(0, 255, 255, 0.5));
        animation: fc36-float 3s ease-in-out infinite;
    }
    @keyframes fc36-float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-4px); }
    }
    .fc36-weather-text {
        font-size: 1.05rem;
        color: #ffffff;
        font-weight: 700;
        margin-bottom: 18px;
        text-shadow: 0 0 6px rgba(255, 255, 255, 0.3);
        font-family: 'Share Tech Mono', monospace;
    }
    .fc36-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #00ffff44, transparent);
        margin: 12px 0;
    }
    .fc36-stat-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 8px;
        margin: 4px 0;
        border-radius: 6px;
        background: rgba(0, 255, 255, 0.03);
        font-family: 'Share Tech Mono', monospace;
    }
    .fc36-stat-label {
        font-size: 0.78rem;
        color: #00ffff;
        opacity: 0.85;
    }
    .fc36-stat-value {
        font-size: 0.95rem;
        font-weight: 700;
        color: #ffffff;
        text-shadow: 0 0 4px rgba(255, 255, 255, 0.2);
    }
    .fc36-temp-high { color: #ff4d6a !important; text-shadow: 0 0 6px rgba(255, 0, 60, 0.4) !important; }
    .fc36-temp-low { color: #00d4ff !important; text-shadow: 0 0 6px rgba(0, 212, 255, 0.4) !important; }
    </style>
    """, unsafe_allow_html=True)

    # 取最多 3 筆
    display_records = records[:3]
    cols = st.columns(len(display_records))

    for idx, (col, rec) in enumerate(zip(cols, display_records)):
        with col:
            time_desc = format_forecast_time_range(
                rec.get("forecast_start", ""), rec.get("forecast_end", "")
            )
            weather = rec.get("weather", "")
            icon = get_weather_icon(weather)
            max_t = rec.get("max_temp", "--")
            min_t = rec.get("min_temp", "--")
            pop = rec.get("precipitation", 0)
            comfort = rec.get("comfort", "")
            period_label = _get_period_label(idx)
            pop_color = _get_precipitation_color(float(pop) if pop else 0)

            st.markdown(f"""
            <div class="fc36-card">
                <div class="fc36-period-label">{period_label}</div>
                <div class="fc36-time">{time_desc}</div>
                <div class="fc36-weather-icon">{icon}</div>
                <div class="fc36-weather-text">{weather}</div>
                <div class="fc36-divider"></div>
                <div class="fc36-stat-row">
                    <span class="fc36-stat-label">🔥 最高溫</span>
                    <span class="fc36-stat-value fc36-temp-high">{max_t}°C</span>
                </div>
                <div class="fc36-stat-row">
                    <span class="fc36-stat-label">❄️ 最低溫</span>
                    <span class="fc36-stat-value fc36-temp-low">{min_t}°C</span>
                </div>
                <div class="fc36-stat-row">
                    <span class="fc36-stat-label">💧 降雨機率</span>
                    <span class="fc36-stat-value" style="color: {pop_color}; text-shadow: 0 0 6px {pop_color}40;">{pop}%</span>
                </div>
                <div class="fc36-stat-row">
                    <span class="fc36-stat-label">🌿 舒適度</span>
                    <span class="fc36-stat-value" style="font-size: 0.85rem;">{comfort}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

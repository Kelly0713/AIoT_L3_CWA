"""天氣指標資訊卡片元件模組 (Weather Cards).

負責以現代感、直觀的卡片方式呈現目前選擇地區的天氣現象、氣溫、降雨機率與舒適度。
"""

from typing import Dict, Any
import streamlit as st
from utils.weather_icon import get_weather_icon
from utils.formatter import format_temperature, format_precipitation, format_forecast_time_range


def render_weather_cards(forecast_data: Dict[str, Any]) -> None:
    """渲染指定時段的天氣現象與各項指標卡片.

    Args:
        forecast_data: 包含 weather, min_temp, max_temp, precipitation, comfort 等欄位的字典。
    """
    if not forecast_data:
        st.warning("查無該時段之天氣預報資料。")
        return

    weather = forecast_data.get("weather", "多雲")
    icon = get_weather_icon(weather)
    min_t = forecast_data.get("min_temp")
    max_t = forecast_data.get("max_temp")
    pop = forecast_data.get("precipitation")
    comfort = forecast_data.get("comfort", "舒適")
    start_t = forecast_data.get("forecast_start", "")
    end_t = forecast_data.get("forecast_end", "")
    time_range_desc = format_forecast_time_range(start_t, end_t)

    # 顯示時段副標
    st.caption(f"📅 預報時段：{time_range_desc}")

    # 自訂 CSS 卡片樣式 (提升視覺質感)
    card_style = """
    <style>
    .metric-card {
        background: rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 8px;
        padding: 16px 20px;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.2), inset 0 0 10px rgba(255, 0, 255, 0.1);
        border: 1px solid rgba(0, 255, 255, 0.4);
        text-align: center;
        margin-bottom: 12px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, transparent, #00ffff, #ff00ff, transparent);
    }
    .metric-card:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 0 25px rgba(255, 0, 255, 0.4), inset 0 0 15px rgba(0, 255, 255, 0.3);
        border: 1px solid #ff00ff;
    }
    .metric-title {
        font-size: 0.88rem;
        color: #00ffff;
        margin-bottom: 6px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value {
        font-size: 1.55rem;
        font-weight: 700;
        color: #ffffff;
        text-shadow: 0 0 10px #ffffff, 0 0 20px #00ffff;
    }
    .metric-sub {
        font-size: 0.75rem;
        color: #ff00ff;
        margin-top: 4px;
        text-shadow: 0 0 5px #ff00ff;
    }
    </style>
    """
    st.markdown(card_style, unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">天氣現象</div>
                <div class="metric-value">{icon} {weather}</div>
                <div class="metric-sub">天候概況</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        max_str = format_temperature(max_t)
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">最高氣溫</div>
                <div class="metric-value">🔥 {max_str}</div>
                <div class="metric-sub">日間預測高溫</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        min_str = format_temperature(min_t)
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">最低氣溫</div>
                <div class="metric-value">❄️ {min_str}</div>
                <div class="metric-sub">夜間/清晨低溫</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        pop_str = format_precipitation(pop)
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">降雨機率</div>
                <div class="metric-value">💧 {pop_str}</div>
                <div class="metric-sub">PoP 機率</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col5:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">舒適度</div>
                <div class="metric-value" style="font-size: 1.25rem;">🌿 {comfort}</div>
                <div class="metric-sub">人體感受</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

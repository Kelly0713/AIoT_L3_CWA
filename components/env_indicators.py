"""環境指標 UI 元件 (AQI & UVI Indicators).

以深色科技風格的自訂 CSS 卡片呈現空氣品質 (AQI) 與紫外線 (UVI) 數值。
此元件純粹負責渲染，不修改任何原有元件或服務。
"""

import streamlit as st

from services.env_api import (
    fetch_aqi_data,
    fetch_uvi_data,
    get_aqi_level_info,
    get_uvi_level_info,
)


def render_env_indicators(region_name: str) -> None:
    """渲染 AQI + UVI 環境指標卡片區塊.

    Args:
        region_name: 當前選擇的縣市名稱。
    """
    aqi_data = fetch_aqi_data(region_name)
    uvi_data = fetch_uvi_data(region_name)

    if not aqi_data and not uvi_data:
        return

    # 注入環境指標專用 CSS
    st.markdown("""
    <style>
    .env-section-title {
        font-family: 'Share Tech Mono', monospace;
        color: #00ffff;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-bottom: 12px;
        text-shadow: 0 0 4px rgba(0, 255, 255, 0.5);
    }
    .env-card {
        background: rgba(5, 5, 20, 0.8);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 14px;
        padding: 20px;
        border: 1px solid rgba(0, 255, 255, 0.3);
        box-shadow:
            0 0 12px rgba(0, 255, 255, 0.1),
            inset 0 0 15px rgba(0, 255, 255, 0.03);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    .env-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--env-accent, #00ffff), transparent);
    }
    .env-card:hover {
        transform: translateY(-2px);
        box-shadow:
            0 0 20px rgba(0, 255, 255, 0.2),
            inset 0 0 20px rgba(0, 255, 255, 0.05);
    }
    .env-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    .env-card-label {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.82rem;
        color: #00ffff;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    .env-card-badge {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.7rem;
        padding: 3px 10px;
        border-radius: 20px;
        font-weight: 600;
        letter-spacing: 1px;
    }
    .env-main-value {
        font-family: 'Share Tech Mono', monospace;
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        margin: 8px 0;
        line-height: 1;
    }
    .env-sub-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 4px 0;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.75rem;
        color: #aaaacc;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
    }
    .env-sub-val {
        color: #ffffff;
        font-weight: 600;
    }
    .env-source {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.65rem;
        color: #555577;
        text-align: right;
        margin-top: 8px;
    }

    /* AQI 圓環動畫 */
    @keyframes env-pulse {
        0%, 100% { opacity: 0.7; }
        50% { opacity: 1; }
    }
    .env-main-value .env-pulse-glow {
        animation: env-pulse 2s ease-in-out infinite;
    }
    </style>
    """, unsafe_allow_html=True)

    col_aqi, col_uvi = st.columns(2)

    # ── AQI 卡片 ──
    if aqi_data:
        aqi_info = get_aqi_level_info(aqi_data.aqi)
        aqi_color = aqi_info["color"]
        aqi_emoji = aqi_info["emoji"]

        with col_aqi:
            st.markdown(f"""
            <div class="env-card" style="--env-accent: {aqi_color};">
                <div class="env-card-header">
                    <span class="env-card-label">🏭 空氣品質 AQI</span>
                    <span class="env-card-badge" style="background: {aqi_color}22; color: {aqi_color}; border: 1px solid {aqi_color}66;">
                        {aqi_data.status}
                    </span>
                </div>
                <div class="env-main-value" style="color: {aqi_color}; text-shadow: 0 0 20px {aqi_color}55, 0 0 40px {aqi_color}22;">
                    <span class="env-pulse-glow">{aqi_emoji}</span> {aqi_data.aqi}
                </div>
                <div class="env-sub-row">
                    <span>PM2.5</span>
                    <span class="env-sub-val">{aqi_data.pm25} μg/m³</span>
                </div>
                <div class="env-sub-row">
                    <span>PM10</span>
                    <span class="env-sub-val">{aqi_data.pm10} μg/m³</span>
                </div>
                <div class="env-sub-row">
                    <span>O₃ 臭氧</span>
                    <span class="env-sub-val">{aqi_data.o3} ppb</span>
                </div>
                <div class="env-sub-row">
                    <span>監測站</span>
                    <span class="env-sub-val">{aqi_data.station}</span>
                </div>
                <div class="env-source">📡 {aqi_data.publish_time}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── UVI 卡片 ──
    if uvi_data:
        uvi_info = get_uvi_level_info(uvi_data.uvi)
        uvi_color = uvi_info["color"]
        uvi_emoji = uvi_info["emoji"]

        with col_uvi:
            # UVI 進度條寬度 (0~15 映射到 0~100%)
            uvi_pct = min(100, int(uvi_data.uvi / 15 * 100))

            st.markdown(f"""
            <div class="env-card" style="--env-accent: {uvi_color};">
                <div class="env-card-header">
                    <span class="env-card-label">☀️ 紫外線 UVI</span>
                    <span class="env-card-badge" style="background: {uvi_color}22; color: {uvi_color}; border: 1px solid {uvi_color}66;">
                        {uvi_data.level}
                    </span>
                </div>
                <div class="env-main-value" style="color: {uvi_color}; text-shadow: 0 0 20px {uvi_color}55, 0 0 40px {uvi_color}22;">
                    <span class="env-pulse-glow">{uvi_emoji}</span> {uvi_data.uvi}
                </div>
                <div style="margin: 12px 0 8px 0;">
                    <div style="
                        background: rgba(255,255,255,0.08);
                        border-radius: 6px;
                        height: 8px;
                        overflow: hidden;
                        position: relative;
                    ">
                        <div style="
                            width: {uvi_pct}%;
                            height: 100%;
                            background: linear-gradient(90deg, #00ff88, #ffff00, #ff8c00, #ff003c);
                            border-radius: 6px;
                            box-shadow: 0 0 8px {uvi_color}88;
                            transition: width 0.5s ease;
                        "></div>
                    </div>
                    <div style="
                        display: flex;
                        justify-content: space-between;
                        font-family: 'Share Tech Mono', monospace;
                        font-size: 0.6rem;
                        color: #555577;
                        margin-top: 3px;
                    ">
                        <span>0</span>
                        <span>低</span>
                        <span>中</span>
                        <span>高</span>
                        <span>過量</span>
                        <span>15</span>
                    </div>
                </div>
                <div class="env-sub-row">
                    <span>曝曬建議</span>
                    <span class="env-sub-val" style="font-size: 0.72rem;">{"需防護" if uvi_data.uvi > 5 else "一般活動"}</span>
                </div>
                <div class="env-sub-row">
                    <span>觀測地區</span>
                    <span class="env-sub-val">{uvi_data.county}</span>
                </div>
                <div class="env-source">📡 {uvi_data.publish_time}</div>
            </div>
            """, unsafe_allow_html=True)

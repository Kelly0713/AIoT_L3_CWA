"""Taiwan Weather Forecast - 台灣天氣預報網站.

課程專題主程式 (Streamlit UI Layer)。
遵循分層架構設計，僅負責 UI 互動與渲染，業務邏輯交由 WeatherService 處理。
"""

import pandas as pd
import streamlit as st

from config import DEFAULT_REGION, CITY_COORDINATES
from services.weather_service import WeatherService
from components.weather_card import render_weather_cards
from components.charts import (
    render_temperature_trend_chart,
    render_precipitation_bar_chart,
    render_forecast_table,
)
from components.forecast_cards import render_forecast_cards_36h
from components.env_indicators import render_env_indicators
from components.map import render_taiwan_weather_map
from components.cyberpunk_css import inject_cyberpunk_styles

# 1. 頁面全域設定
st.set_page_config(
    page_title="Taiwan Weather Forecast - 中央氣象署 36 小時天氣預報",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 任務 3-1：自動更新 (每 30 分鐘 = 1,800,000 毫秒) ──
# 使用純 HTML/JS 實現自動重整，無需額外套件
st.markdown(
    """
    <script>
        // 每 30 分鐘自動重整頁面
        setTimeout(function(){ window.location.reload(); }, 1800000);
    </script>
    """,
    unsafe_allow_html=True,
)

# 注入 Cyberpunk 全域樣式
inject_cyberpunk_styles()


@st.cache_resource
def get_service() -> WeatherService:
    """快取取得 WeatherService 實例，確保單例與連線重複使用."""
    return WeatherService()


def main() -> None:
    service = get_service()

    # 2. 側邊欄 (Sidebar)
    st.sidebar.title("🌦️ 天氣控制台")
    st.sidebar.markdown("---")

    # 取得可用縣市清單 (優先以全台標準清單展示)
    all_city_list = list(CITY_COORDINATES.keys())
    saved_regions = service.get_available_regions()
    region_options = all_city_list if all_city_list else saved_regions

    # 地區下拉選單
    default_idx = (
        region_options.index(DEFAULT_REGION) if DEFAULT_REGION in region_options else 0
    )
    selected_region = st.sidebar.selectbox(
        "📍 選擇預報地區：",
        options=region_options,
        index=default_idx,
        help="請選擇欲查詢之台灣縣市",
    )

    # ── 任務 3-2：手動即時更新（保留原有按鈕，增強 cache 清除邏輯） ──
    st.sidebar.markdown("### 🔄 資料同步")
    if st.sidebar.button("🔄 更新天氣資料", width="stretch", type="primary"):
        # 清除所有 Streamlit 快取，確保重新發送 API 請求
        st.cache_data.clear()
        st.cache_resource.clear()
        with st.spinner("正在向中央氣象署 API 同步最新預報..."):
            # 重新取得 service 實例 (因 cache_resource 已清除)
            fresh_service = WeatherService()
            success, msg = fresh_service.refresh_weather_data(force=True)
            if success:
                st.sidebar.success(msg)
            else:
                st.sidebar.warning(f"更新注意: {msg}")
        st.rerun()

    # 資料狀態資訊
    last_update = service.get_last_updated_time()
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"⏱ **最後更新時間：**\n`{last_update or '尚未同步'}`")

    # 自動更新狀態提示
    st.sidebar.markdown("---")
    st.sidebar.markdown("🔁 **自動更新：** `每 30 分鐘`")

    # 3. 主畫面 Header
    st.title("🌤 Taiwan Weather Forecast")
    st.markdown("##### 中央氣象署 36 小時天氣預報")
    st.caption("資料來源：中央氣象署 Open Data (F-C0032-001)")
    st.markdown("---")

    # 4. 讀取所選地區之預報資料
    forecast_records = service.get_forecasts_for_region(selected_region)
    if not forecast_records:
        st.error(f"目前尚無 {selected_region} 的氣象預報資料，請點擊側邊欄「🔄 更新天氣資料」。")
        return

    # 轉為 DataFrame 供圖表繪製
    forecast_df = pd.DataFrame(forecast_records)

    # ----------------------------------------------------
    # 第一區：目前選擇地區 Weather Cards
    # ----------------------------------------------------
    st.subheader(f"📍 {selected_region} 預報概況")
    # 當前即最新時段 (第一筆)
    current_forecast = forecast_records[0]
    render_weather_cards(current_forecast)
    st.markdown("---")

    # ----------------------------------------------------
    # 新增區：環境指標 (AQI + UVI) — 任務 2
    # ----------------------------------------------------
    st.subheader("🌍 環境監測指標")
    st.caption("空氣品質 (AQI) 與紫外線 (UVI) 即時監測 ── 📌 目前為模擬資料，後續可串接環境部 OpenData")
    render_env_indicators(selected_region)
    st.markdown("---")

    # ----------------------------------------------------
    # 第二區 & 第三區：未來 36 小時氣溫趨勢與降雨機率
    # ----------------------------------------------------
    st.subheader("📈 趨勢分析")
    chart_col1, chart_col2 = st.columns([3, 2])

    with chart_col1:
        st.markdown("##### 🌡️ 未來 36 小時氣溫趨勢")
        render_temperature_trend_chart(forecast_df)

    with chart_col2:
        st.markdown("##### 💧 降雨機率分析")
        render_precipitation_bar_chart(forecast_df)

    st.markdown("---")

    # ----------------------------------------------------
    # 第四區：未來 36 小時詳細預報 (卡片取代表格) — 任務 1
    # ----------------------------------------------------
    st.subheader("📋 未來 36 小時詳細預報")
    render_forecast_cards_36h(forecast_records)
    st.markdown("---")

    # ----------------------------------------------------
    # 第五區：台灣天氣概況 (Folium 地圖)
    # ----------------------------------------------------
    st.subheader("🗺️ 台灣各縣市天氣概況地圖")
    st.caption("點選地圖上的縣市標記，即可檢視該縣市當前時段最高溫、低溫與天候資訊。")
    all_summary = service.get_all_regions_summary()
    render_taiwan_weather_map(all_summary)

    # ----------------------------------------------------
    # (Footer removed)


if __name__ == "__main__":
    main()

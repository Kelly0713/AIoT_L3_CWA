"""台灣天氣概況互動地圖元件 (Map).

使用 Folium 與 streamlit-folium 呈現全台灣各縣市當前氣溫與天候分佈。
底圖採用 CARTO Voyager raster tile。
"""

from typing import List, Dict, Any
import folium
from streamlit_folium import st_folium
import streamlit as st

from config import CITY_COORDINATES, CARTO_TILE_URL, CARTO_ATTR, get_map_api_key
from utils.weather_icon import get_weather_icon


def get_marker_color(max_temp: float) -> str:
    """根據最高氣溫決定地圖標記顏色."""
    if max_temp >= 33.0:
        return "red"
    elif max_temp >= 30.0:
        return "orange"
    elif max_temp >= 26.0:
        return "green"
    elif max_temp >= 22.0:
        return "blue"
    else:
        return "purple"


def render_taiwan_weather_map(summary_records: List[Dict[str, Any]]) -> None:
    """渲染全台天氣概況互動地圖 (Folium).

    Args:
        summary_records: 各縣市最新時段之預報資訊清單。
    """
    if not summary_records:
        st.info("尚無全台概況資料可供繪製地圖。")
        return

    # 建立空白底圖 (不帶預設 tile，由 TileLayer 自行指定)
    tw_map = folium.Map(
        location=[23.85, 120.95],
        zoom_start=7,
        tiles=None,
        control_scale=True,
    )

    # 使用 CARTO Voyager raster tile 作為底圖
    map_api_key = get_map_api_key()
    tile_url = CARTO_TILE_URL.format(key=map_api_key)

    folium.TileLayer(
        tiles=tile_url,
        attr=CARTO_ATTR,
        name="CARTO Voyager",
        overlay=False,
        control=True,
    ).add_to(tw_map)

    # 將 summary 轉為以 region_name 為 key 的字典
    summary_dict = {r["region_name"]: r for r in summary_records}

    for region_name, coords in CITY_COORDINATES.items():
        data = summary_dict.get(region_name)
        if not data:
            continue

        weather = data.get("weather", "多雲")
        icon = get_weather_icon(weather)
        max_t = data.get("max_temp", 28.0)
        min_t = data.get("min_temp", 22.0)
        pop = data.get("precipitation", 0.0)
        comfort = data.get("comfort", "舒適")

        color = get_marker_color(float(max_t))

        popup_html = f"""
        <div style="font-family: sans-serif; min-width: 150px; font-size: 13px;">
            <h4 style="margin: 0 0 6px 0; color: #1e293b;">{region_name} {icon}</h4>
            <div style="color: #475569; margin-bottom: 3px;">天氣：<b>{weather}</b></div>
            <div style="color: #e11d48; margin-bottom: 3px;">最高溫：<b>{max_t}°C</b></div>
            <div style="color: #0284c7; margin-bottom: 3px;">最低溫：<b>{min_t}°C</b></div>
            <div style="color: #2563eb; margin-bottom: 3px;">降雨機率：<b>{pop}%</b></div>
            <div style="color: #0d9488;">舒適度：{comfort}</div>
        </div>
        """

        folium.CircleMarker(
            location=coords,
            radius=9,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{region_name}：{icon} {max_t}°C / 降雨 {pop}%",
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            weight=2,
        ).add_to(tw_map)

    # 嵌入至 Streamlit 畫面
    st_folium(
        tw_map,
        width="100%",
        height=480,
        returned_objects=[],
    )

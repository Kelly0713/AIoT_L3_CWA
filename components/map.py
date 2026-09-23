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
    """根據最高氣溫決定地圖標記顏色 (Neon Colors)."""
    if max_temp >= 33.0:
        return "#ff003c"  # Neon Red
    elif max_temp >= 30.0:
        return "#ff8c00"  # Neon Orange
    elif max_temp >= 26.0:
        return "#00ff00"  # Neon Green
    elif max_temp >= 22.0:
        return "#00f0ff"  # Neon Blue
    else:
        return "#d900ff"  # Neon Purple


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

    # 使用 CARTO Dark Matter raster tile 作為底圖
    map_api_key = get_map_api_key()
    tile_url = CARTO_TILE_URL.format(key=map_api_key)

    folium.TileLayer(
        tiles=tile_url,
        attr=CARTO_ATTR,
        name="CARTO Dark Matter",
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
        <div style="font-family: 'Share Tech Mono', monospace; background-color: rgba(5,5,16,0.9); border: 1px solid #00ffff; box-shadow: 0 0 15px #00ffff; padding: 12px; border-radius: 8px; color: #00ffff; min-width: 160px; font-size: 13px;">
            <h4 style="margin: 0 0 8px 0; color: #ff00ff; text-shadow: 0 0 8px #ff00ff; font-size: 16px;">{region_name} {icon}</h4>
            <div style="margin-bottom: 4px;">天氣概況：<b style="color: #fff;">{weather}</b></div>
            <div style="color: #ff003c; margin-bottom: 4px;">最高溫：<b style="color: #fff; text-shadow: 0 0 5px #ff003c;">{max_t}°C</b></div>
            <div style="color: #00f0ff; margin-bottom: 4px;">最低溫：<b style="color: #fff; text-shadow: 0 0 5px #00f0ff;">{min_t}°C</b></div>
            <div style="color: #d900ff; margin-bottom: 4px;">降雨機率：<b style="color: #fff; text-shadow: 0 0 5px #d900ff;">{pop}%</b></div>
            <div style="color: #00ff00;">人體舒適：<b style="color: #fff; text-shadow: 0 0 5px #00ff00;">{comfort}</b></div>
        </div>
        """

        node_html = f"""
        <div style="
            width: 12px; 
            height: 12px; 
            background-color: {color}; 
            border-radius: 50%; 
            box-shadow: 0 0 10px {color}, 0 0 20px {color}, 0 0 30px {color}; 
            border: 1px solid #fff;
            animation: pulse-node 1.5s infinite alternate;
        "></div>
        <style>
        @keyframes pulse-node {{
            from {{ opacity: 0.6; transform: scale(0.8); }}
            to {{ opacity: 1; transform: scale(1.3); box-shadow: 0 0 15px {color}, 0 0 30px {color}; }}
        }}
        </style>
        """

        folium.Marker(
            location=coords,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{region_name}：{max_t}°C / 降雨 {pop}%",
            icon=folium.DivIcon(html=node_html, icon_size=(12, 12), icon_anchor=(6, 6))
        ).add_to(tw_map)

    # 嵌入至 Streamlit 畫面
    st_folium(
        tw_map,
        width="100%",
        height=480,
        returned_objects=[],
    )

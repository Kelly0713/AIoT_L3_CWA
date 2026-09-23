"""視覺化圖表與預報資料表格元件 (Charts).

實作第二區（氣溫趨勢折線圖）、第三區（降雨機率長條圖）與第四區（詳細預報表格）。
使用 Plotly 與 Streamlit DataFrame。
"""

from typing import List, Dict, Any
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.formatter import format_forecast_time_range
from utils.weather_icon import get_weather_icon


def render_temperature_trend_chart(df: pd.DataFrame) -> None:
    """渲染未來 36 小時氣溫趨勢折線圖 (Plotly).

    X axis: forecast_start
    Y axis: temperature
    顯示：Max Temperature 與 Min Temperature
    """
    if df.empty:
        st.info("無足夠資料繪製氣溫趨勢圖。")
        return

    # 製作可讀的 X 軸時間標籤
    x_labels = [
        format_forecast_time_range(row["forecast_start"], row["forecast_end"])
        for _, row in df.iterrows()
    ]

    fig = go.Figure()

    # 最高溫折線 (暖紅)
    fig.add_trace(
        go.Scatter(
            x=x_labels,
            y=df["max_temp"],
            mode="lines+markers+text",
            name="最高氣溫 (MaxT)",
            line=dict(color="#ef4444", width=3, shape="spline"),
            marker=dict(size=9, color="#ef4444"),
            text=[f"{t}°C" for t in df["max_temp"]],
            textposition="top center",
            textfont=dict(size=12, color="#b91c1c", family="sans-serif"),
            hovertemplate="時段: %{x}<br>最高溫: <b>%{y}°C</b><extra></extra>",
        )
    )

    # 最低溫折線 (清爽藍)
    fig.add_trace(
        go.Scatter(
            x=x_labels,
            y=df["min_temp"],
            mode="lines+markers+text",
            name="最低氣溫 (MinT)",
            line=dict(color="#3b82f6", width=3, shape="spline"),
            marker=dict(size=9, color="#3b82f6"),
            text=[f"{t}°C" for t in df["min_temp"]],
            textposition="bottom center",
            textfont=dict(size=12, color="#1d4ed8", family="sans-serif"),
            hovertemplate="時段: %{x}<br>最低溫: <b>%{y}°C</b><extra></extra>",
        )
    )

    # 動態設定 Y 軸範圍
    y_min = max(0, int(df["min_temp"].min() - 3))
    y_max = int(df["max_temp"].max() + 4)

    fig.update_layout(
        title=dict(text="未來 36 小時氣溫趨勢 (°C)", font=dict(size=16, color="#334155")),
        xaxis=dict(
            title="",
            tickangle=-15,
            showgrid=True,
            gridcolor="#f1f5f9",
        ),
        yaxis=dict(
            title="溫度 (°C)",
            range=[y_min, y_max],
            showgrid=True,
            gridcolor="#e2e8f0",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(l=40, r=40, t=60, b=60),
        hovermode="x unified",
        template="plotly_white",
        height=360,
    )

    st.plotly_chart(fig, use_container_width=True)


def render_precipitation_bar_chart(df: pd.DataFrame) -> None:
    """渲染降雨機率長條圖 (Plotly).

    X: forecast_start
    Y: precipitation
    """
    if df.empty:
        st.info("無足夠資料繪製降雨機率圖。")
        return

    x_labels = [
        format_forecast_time_range(row["forecast_start"], row["forecast_end"])
        for _, row in df.iterrows()
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=x_labels,
            y=df["precipitation"],
            text=[f"{p}%" for p in df["precipitation"]],
            textposition="auto",
            marker=dict(
                color=df["precipitation"],
                colorscale=[[0, "#93c5fd"], [0.5, "#3b82f6"], [1, "#1d4ed8"]],
                cmin=0,
                cmax=100,
                showscale=False,
                line=dict(color="#1e40af", width=1),
            ),
            hovertemplate="時段: %{x}<br>降雨機率: <b>%{y}%</b><extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text="降雨機率預測 (%)", font=dict(size=16, color="#334155")),
        xaxis=dict(title="", tickangle=-15, showgrid=False),
        yaxis=dict(
            title="降雨機率 (%)",
            range=[0, 105],
            showgrid=True,
            gridcolor="#e2e8f0",
            dtick=20,
        ),
        margin=dict(l=40, r=40, t=60, b=60),
        template="plotly_white",
        height=320,
    )

    st.plotly_chart(fig, use_container_width=True)


def render_forecast_table(records: List[Dict[str, Any]]) -> None:
    """渲染第四區：未來 36 小時詳細預報表格.

    欄位：
    時間、天氣、最低溫、最高溫、降雨機率、舒適度
    """
    if not records:
        st.info("無預報表格資料。")
        return

    table_data = []
    for r in records:
        time_desc = format_forecast_time_range(r["forecast_start"], r["forecast_end"])
        w_text = r.get("weather", "")
        icon = get_weather_icon(w_text)
        table_data.append(
            {
                "預報時間區段": time_desc,
                "天氣現象": f"{icon} {w_text}",
                "最低溫": f"{r.get('min_temp')} °C",
                "最高溫": f"{r.get('max_temp')} °C",
                "降雨機率": f"{r.get('precipitation')} %",
                "舒適度": r.get("comfort", ""),
            }
        )

    display_df = pd.DataFrame(table_data)
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

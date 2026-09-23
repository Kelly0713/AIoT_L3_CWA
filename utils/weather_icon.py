"""天氣現象文字轉 Emoji 圖示模組.

依據中央氣象署 Wx 天氣現象描述關鍵字，轉換為適當的 Emoji 圖示供 UI 呈現。
不修改原始天氣字串。
"""


def get_weather_icon(weather_desc: str) -> str:
    """根據天氣現象描述文字回傳對應的 Emoji 圖示.

    規則：
    - 雷 (包含雷陣雨、雷雨等) -> ⛈️
    - 雨 (包含短暫雨、陰短暫雨、陣雨等) -> 🌧️
    - 雪 -> ❄️
    - 霧 -> 🌫️
    - 依氣象局主要天候特徵判斷：
        - 以「晴」為主（如晴、晴時多雲）-> ☀️
        - 以「多雲」為主（如多雲、多雲時晴、多雲時陰）-> ⛅
        - 以「陰」為主（如陰、陰時多雲）-> ☁️
    - 其他包含陰 -> ☁️
    - 其他包含多雲 -> ⛅
    - 其他包含晴 -> ☀️
    - 如果無法判斷，顯示 🌤️

    Args:
        weather_desc: 天氣現象描述（例如："晴時多雲"、"午後短暫雷陣雨"）。

    Returns:
        str: 代表該天氣的 Emoji 圖示。
    """
    if not weather_desc or not isinstance(weather_desc, str):
        return "🌤️"

    desc = weather_desc.strip()

    # 1. 優先判斷降水與劇烈天氣
    if "雷" in desc:
        return "⛈️"
    if "雨" in desc:
        return "🌧️"
    if "雪" in desc:
        return "❄️"
    if "霧" in desc:
        return "🌫️"

    # 2. 依氣象局命名原則，前詞代表主要雲量型態
    if desc.startswith("晴"):
        return "☀️"
    if desc.startswith("多雲"):
        return "⛅"
    if desc.startswith("陰"):
        return "☁️"

    # 3. 備援關鍵字判斷
    if "陰" in desc:
        return "☁️"
    if "多雲" in desc:
        return "⛅"
    if "晴" in desc:
        return "☀️"

    return "🌤️"

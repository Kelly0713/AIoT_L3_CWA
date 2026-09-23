import streamlit as st

def inject_cyberpunk_styles():
    css = """
    <style>
    /* Global Fonts & Backgrounds */
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Share+Tech+Mono&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Share Tech Mono', 'Fira Code', monospace !important;
        background-color: #050510 !important;
        color: #00ffff !important;
    }

    /* Fix Material Icons overridden by global font */
    .stIcon, .material-symbols-rounded, [data-testid="stSidebarCollapseButton"] * {
        font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
    }

    /* Streamlit Main App */
    .stApp {
        background-color: #050510;
        background-image: linear-gradient(0deg, transparent 24%, rgba(0, 255, 255, .05) 25%, rgba(0, 255, 255, .05) 26%, transparent 27%, transparent 74%, rgba(0, 255, 255, .05) 75%, rgba(0, 255, 255, .05) 76%, transparent 77%, transparent), linear-gradient(90deg, transparent 24%, rgba(0, 255, 255, .05) 25%, rgba(0, 255, 255, .05) 26%, transparent 27%, transparent 74%, rgba(0, 255, 255, .05) 75%, rgba(0, 255, 255, .05) 76%, transparent 77%, transparent);
        background-size: 50px 50px;
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #00ffff !important;
        text-shadow: 0 0 3px rgba(0, 255, 255, 0.6);
        font-family: 'Share Tech Mono', monospace !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #020205 !important;
        border-right: 2px solid #ff00ff;
        box-shadow: inset -5px 0 15px rgba(255, 0, 255, 0.2);
        background-image: radial-gradient(circle at 10% 20%, rgba(0, 255, 255, 0.05) 0%, transparent 20%);
    }

    /* Sidebar Title */
    [data-testid="stSidebar"] h1 {
        color: #00ffff !important;
        text-shadow: 0 0 5px rgba(0, 255, 255, 0.8);
    }

    /* Selectbox */
    div[data-baseweb="select"] > div {
        background-color: #050510;
        border: 1px solid #00ffff;
        box-shadow: 0 0 5px rgba(0, 255, 255, 0.3);
        color: #00ffff;
    }

    /* Buttons */
    button[kind="primary"] {
        background: transparent !important;
        border: 2px solid #ff00ff !important;
        color: #ff00ff !important;
        text-shadow: 0 0 3px #ff00ff;
        box-shadow: 0 0 5px #ff00ff, inset 0 0 5px #ff00ff;
        transition: all 0.2s ease-in-out;
        position: relative;
        overflow: hidden;
    }
    
    button[kind="primary"]:hover {
        background: #ff00ff !important;
        color: #000 !important;
        box-shadow: 0 0 15px #ff00ff, inset 0 0 15px #ff00ff;
    }

    /* Button Glitch Hover Effect */
    @keyframes glitch {
        0% { transform: translate(0) }
        20% { transform: translate(-1px, 1px) }
        40% { transform: translate(-1px, -1px) }
        60% { transform: translate(1px, 1px) }
        80% { transform: translate(1px, -1px) }
        100% { transform: translate(0) }
    }
    button[kind="primary"]:hover span {
        animation: glitch 0.3s cubic-bezier(.25, .46, .45, .94) both infinite;
    }

    /* Success / Alerts */
    [data-testid="stAlert"] {
        background-color: rgba(0, 255, 0, 0.1);
        border-left: 4px solid #00ff00;
        color: #00ff00;
        text-shadow: 0 0 3px #00ff00;
    }
    [data-testid="stAlert"] p {
        color: #00ff00 !important;
    }
    [data-testid="stAlert"] svg {
        fill: #00ff00 !important;
    }

    /* Dataframe / Tables */
    [data-testid="stDataFrame"] {
        border: 1px solid #00ffff;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.2);
    }
    [data-testid="stDataFrame"] table {
        background-color: transparent !important;
    }
    [data-testid="stDataFrame"] th {
        background-color: rgba(0, 255, 255, 0.1) !important;
        color: #00ffff !important;
        border-bottom: 1px solid #00ffff !important;
    }
    [data-testid="stDataFrame"] tr:nth-child(even) {
        background-color: rgba(255, 0, 255, 0.05) !important;
    }
    [data-testid="stDataFrame"] tr:nth-child(odd) {
        background-color: rgba(0, 255, 0, 0.05) !important;
    }
    [data-testid="stDataFrame"] td {
        color: #e0e0e0 !important;
        border-bottom: 1px solid rgba(0, 255, 255, 0.2) !important;
    }

    /* Custom Terminal Footer */
    .terminal-footer {
        position: relative;
        margin-top: 50px;
        padding: 20px;
        background-color: #020205;
        border-top: 1px solid #ffff00;
        border-bottom: 1px solid #ffff00;
        color: #ffff00;
        font-family: 'Fira Code', monospace;
        text-align: center;
        text-shadow: 0 0 3px rgba(255, 255, 0, 0.8);
        box-shadow: 0 -3px 10px rgba(255, 255, 0, 0.1);
    }
    
    .typewriter-effect {
        display: inline-block;
        overflow: hidden;
        border-right: .15em solid #ffff00;
        white-space: nowrap;
        margin: 0 auto;
        letter-spacing: .15em;
        animation: typing 3.5s steps(40, end), blink-caret .75s step-end infinite;
    }

    @keyframes typing {
        from { width: 0 }
        to { width: 100% }
    }
    @keyframes blink-caret {
        from, to { border-color: transparent }
        50% { border-color: #ffff00; }
    }

    /* Global Glitch on Load (Reduced opacity to make text clearer) */
    @keyframes scanline {
        0% { transform: translateY(-100%); }
        100% { transform: translateY(100vh); }
    }
    body::after {
        content: " ";
        display: block;
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.03));
        z-index: 20000;
        background-size: 100% 2px, 3px 100%;
        pointer-events: none;
    }
    
    /* Scrollbars */
    ::-webkit-scrollbar {
        width: 10px;
    }
    ::-webkit-scrollbar-track {
        background: #020205;
    }
    ::-webkit-scrollbar-thumb {
        background: #00ffff;
        box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.3);
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #ff00ff;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

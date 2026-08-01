"""
styling.py — injects custom CSS into the Streamlit app to give it a
professional, branded look (matching the SmartMart ledger/receipt theme).
"""

import streamlit as st

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600;700&display=swap');

:root{
    --ink:#14322A;
    --register:#2F6B4F;
    --gold:#C08829;
    --paper:#FBF7EE;
    --mist:#F3F5F2;
    --danger:#A8452B;
    --line:#DDE3DD;
    --grey:#66756D;
}

/* ---- hide default Streamlit chrome ---- */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ---- global font ---- */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #20251F;
}
h1, h2, h3 {
    font-family: 'Fraunces', serif !important;
    color: var(--ink) !important;
}

/* ---- app background ---- */
.stApp {
    background-color: var(--mist);
}

/* ---- sidebar ---- */
[data-testid="stSidebar"] {
    background-color: var(--ink);
}
[data-testid="stSidebar"] * {
    color: var(--paper) !important;
}
[data-testid="stSidebar"] h3 {
    font-family: 'Fraunces', serif !important;
    color: var(--paper) !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.15);
}

/* ---- radio nav in sidebar styled like nav items ---- */
[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: rgba(255,255,255,0.04);
    padding: 10px 14px;
    border-radius: 8px;
    margin-bottom: 6px;
    transition: background .15s;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.1);
}

/* ---- buttons ---- */
.stButton > button, .stFormSubmitButton > button {
    background-color: var(--ink);
    color: var(--paper);
    border: none;
    border-radius: 8px;
    padding: 0.55em 1.4em;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    transition: background .15s;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background-color: var(--register);
    color: white;
}
[data-testid="stSidebar"] .stButton > button {
    background-color: var(--danger);
    width: 100%;
}

/* ---- download button as gold accent ---- */
.stDownloadButton > button {
    background-color: var(--gold);
    color: var(--ink);
    border: none;
    border-radius: 8px;
    font-weight: 700;
}
.stDownloadButton > button:hover {
    background-color: #a97620;
    color: white;
}

/* ---- tabs ---- */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    border-bottom: 1.5px solid var(--line);
}
.stTabs [data-baseweb="tab"] {
    font-weight: 600;
    color: var(--grey);
    padding: 10px 4px;
}
.stTabs [aria-selected="true"] {
    color: var(--ink) !important;
    border-bottom: 2.5px solid var(--gold) !important;
}

/* ---- inputs ---- */
.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
    border-radius: 7px !important;
    border: 1.5px solid var(--line) !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--register) !important;
}

/* ---- dataframes ---- */
[data-testid="stDataFrame"] {
    border: 1px solid var(--line);
    border-radius: 10px;
    overflow: hidden;
}

/* ---- metric replacement cards (used via st.markdown) ---- */
.kpi-card {
    background: white;
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
}
.kpi-card .accent {
    position: absolute; left:0; top:0; bottom:0; width:5px;
}
.kpi-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--grey);
    text-transform: uppercase;
    letter-spacing: .5px;
    font-weight: 600;
}
.kpi-value {
    font-family: 'Fraunces', serif;
    font-size: 26px;
    font-weight: 700;
    color: var(--ink);
    margin-top: 6px;
}
.kpi-delta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    margin-top: 4px;
    font-weight: 600;
}

/* ---- auth card ---- */
.auth-title {
    text-align: center;
    font-family: 'Fraunces', serif;
    font-size: 30px;
    color: var(--ink);
    font-weight: 700;
    margin-bottom: 0px;
}
.auth-sub {
    text-align: center;
    color: var(--grey);
    font-size: 14px;
    margin-bottom: 24px;
}

/* ---- alerts ---- */
div[data-testid="stAlert"] {
    border-radius: 10px;
}
</style>
"""


def inject_custom_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def kpi_card(label, value, delta=None, delta_color="#2F6B4F", accent="#2F6B4F"):
    """Renders a styled KPI card (replacement for st.metric)."""
    delta_html = f'<div class="kpi-delta" style="color:{delta_color};">{delta}</div>' if delta else ""
    st.markdown(f"""
        <div class="kpi-card">
            <div class="accent" style="background:{accent};"></div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)

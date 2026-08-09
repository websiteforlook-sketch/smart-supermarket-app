"""
styling.py — Custom CSS for Smart Supermarket Inventory & Sales Analytics System.

Design tokens
-------------
Colors:
  --ink        #0B3B2E   deep ledger green (primary)
  --ink-light  #14543F   secondary green (hover/accents)
  --gold       #C9973E   receipt-stamp gold (highlight/CTA)
  --paper      #FAF7F0   warm paper background
  --card       #FFFFFF   card surface
  --line       #E7E1D3   hairline / dividers
  --ink-text   #1F2A24   primary text
  --muted      #6B7368   secondary text
  --danger     #B3432B   out-of-stock / error
  --success    #2E7D4F   in-stock / success

Type:
  Display  — 'Fraunces'      (headings, KPI numbers)
  Body     — 'Inter'         (all UI text)
  Mono     — 'JetBrains Mono' (barcodes, prices, table figures)

Signature: KPI cards styled like little receipt stubs (dashed perforation edge)
"""

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --ink: #0B3B2E;
    --ink-light: #14543F;
    --gold: #C9973E;
    --paper: #FAF7F0;
    --card: #FFFFFF;
    --line: #E7E1D3;
    --ink-text: #1F2A24;
    --muted: #6B7368;
    --danger: #B3432B;
    --success: #2E7D4F;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--ink-text);
}

.stApp {
    background:
        radial-gradient(circle at 12% 8%, rgba(201,151,62,0.07) 0%, transparent 42%),
        radial-gradient(circle at 88% 92%, rgba(11,59,46,0.06) 0%, transparent 45%),
        var(--paper);
}

h1, h2, h3 {
    font-family: 'Fraunces', serif !important;
    color: var(--ink) !important;
    letter-spacing: -0.01em;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: var(--ink);
    border-right: 1px solid var(--line);
}
section[data-testid="stSidebar"] * {
    color: #F4F1E8 !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
}

/* ---------- Brand header ---------- */
.brand-header {
    display: flex;
    align-items: baseline;
    gap: 10px;
    padding: 4px 0 18px 0;
    border-bottom: 2px dashed var(--line);
    margin-bottom: 22px;
}
.brand-header .mark {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 1.9rem;
    color: var(--ink);
}
.brand-header .tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--gold);
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ---------- KPI receipt-stub cards ---------- */
.kpi-row { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 8px; }
.kpi-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 18px 20px 16px 20px;
    flex: 1 1 190px;
    position: relative;
    box-shadow: 0 1px 2px rgba(11,59,46,0.04), 0 6px 16px rgba(11,59,46,0.05);
    border-bottom: 3px solid var(--gold);
}
.kpi-card .kpi-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    display: flex;
    align-items: center;
    gap: 6px;
}
.kpi-card .kpi-value {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 2rem;
    color: var(--ink);
    margin-top: 4px;
}
.kpi-card .kpi-sub {
    font-size: 0.78rem;
    color: var(--muted);
    margin-top: 2px;
}

/* ---------- Generic content card ---------- */
.panel {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 22px 24px;
    box-shadow: 0 1px 2px rgba(11,59,46,0.04), 0 6px 16px rgba(11,59,46,0.04);
    margin-bottom: 18px;
}

/* ---------- Badges ---------- */
.badge {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    padding: 3px 9px;
    border-radius: 20px;
    letter-spacing: 0.03em;
}
.badge-in { background: rgba(46,125,79,0.12); color: var(--success); }
.badge-low { background: rgba(201,151,62,0.16); color: #8A6417; }
.badge-out { background: rgba(179,67,43,0.12); color: var(--danger); }

/* ---------- Buttons ---------- */
.stButton > button {
    background: var(--ink);
    color: #FAF7F0;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.2rem;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    transition: all 0.15s ease;
}
.stButton > button:hover {
    background: var(--ink-light);
    color: #fff;
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(11,59,46,0.25);
}
.stButton > button[kind="primary"] {
    background: var(--gold);
    color: var(--ink);
}
.stButton > button[kind="primary"]:hover {
    background: #b7862f;
    color: #fff;
}

/* ---------- Inputs ---------- */
.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
    border-radius: 8px !important;
    border: 1px solid var(--line) !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 1px var(--gold) !important;
}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    color: var(--muted);
    border-radius: 8px 8px 0 0;
}
.stTabs [aria-selected="true"] {
    color: var(--ink) !important;
    border-bottom: 3px solid var(--gold) !important;
}

/* ---------- Dataframes ---------- */
[data-testid="stDataFrame"] {
    border: 1px solid var(--line);
    border-radius: 10px;
    overflow: hidden;
}

/* ---------- Barcode field ---------- */
.barcode-scan-box {
    font-family: 'JetBrains Mono', monospace;
    background: repeating-linear-gradient(90deg, var(--ink) 0 6px, transparent 6px 12px);
    height: 4px;
    border-radius: 2px;
    margin: 6px 0 16px 0;
    opacity: 0.5;
}

/* ---------- Auth screen ---------- */
.auth-wrap {
    max-width: 440px;
    margin: 48px auto 0 auto;
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 38px 36px 30px 36px;
    box-shadow: 0 12px 40px rgba(11,59,46,0.10), 0 2px 8px rgba(11,59,46,0.06);
    position: relative;
    overflow: hidden;
}
.auth-wrap::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 5px;
    background: linear-gradient(90deg, var(--ink) 0%, var(--gold) 55%, var(--ink) 100%);
}
.auth-brand {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 26px;
    padding-bottom: 20px;
    border-bottom: 1px dashed var(--line);
}
.auth-icon {
    width: 46px;
    height: 46px;
    min-width: 46px;
    border-radius: 12px;
    background: var(--ink);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.35rem;
    box-shadow: 0 4px 12px rgba(11,59,46,0.25);
}
.auth-brand .mark {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 1.55rem;
    color: var(--ink);
    line-height: 1.15;
}
.auth-wrap h2 { margin-bottom: 2px; }
.auth-sub { color: var(--muted); font-size: 0.85rem; margin-top: 2px; }

/* ---------- Misc ---------- */
hr { border-color: var(--line) !important; }
.small-muted { color: var(--muted); font-size: 0.82rem; }
footer, #MainMenu { visibility: hidden; }
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def brand_header(subtitle: str):
    st.markdown(
        f"""
        <div class="brand-header">
            <span class="mark">SmartMart</span>
            <span class="tag">{subtitle}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card_html(label: str, value: str, sub: str = "", icon: str = "") -> str:
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{icon} {label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """


def stock_badge(stock: int) -> str:
    if stock <= 0:
        return '<span class="badge badge-out">OUT OF STOCK</span>'
    elif stock <= 5:
        return f'<span class="badge badge-low">LOW · {stock} left</span>'
    return f'<span class="badge badge-in">IN STOCK · {stock}</span>'

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

Signature: KPI cards look like little torn-off receipt stubs (perforated top
edge via a radial-gradient mask); content panels carry a faint ledger-rule
texture. Cards are real st.container(key=...) elements (see app.py's panel()
helper) rather than raw markdown divs, so the styling actually wraps the
content instead of floating as an empty box beside it.
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

.block-container {
    padding-top: 2.2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1180px;
}

h1, h2, h3 {
    font-family: 'Fraunces', serif !important;
    color: var(--ink) !important;
    letter-spacing: -0.01em;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--ink) 0%, #0E4535 100%);
    border-right: 1px solid var(--line);
}
section[data-testid="stSidebar"] * {
    color: #F4F1E8 !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 6px 0 18px 0;
}
.sidebar-brand-mark {
    width: 40px;
    height: 40px;
    min-width: 40px;
    border-radius: 10px;
    background: rgba(244,241,232,0.08);
    border: 1px solid rgba(244,241,232,0.15);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
}
.sidebar-brand-name {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 1.35rem;
    letter-spacing: -0.01em;
}
.sidebar-shop {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 0.98rem;
    margin-top: -6px;
    color: #F4F1E8 !important;
}
.sidebar-owner {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.03em;
    color: rgba(244,241,232,0.55) !important;
    margin-top: 1px;
}
.sidebar-divider {
    border-top: 1px dashed rgba(244,241,232,0.2);
    margin: 16px 0 14px 0;
}
.sidebar-spacer { margin-top: 14px; }

/* ---------- Sidebar nav pills ---------- */
section[data-testid="stSidebar"] .stRadio > div {
    gap: 3px;
}
section[data-testid="stSidebar"] .stRadio label {
    padding: 10px 12px;
    border-radius: 10px;
    transition: background 0.15s ease;
    margin-bottom: 1px;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(244,241,232,0.08);
}
section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: rgba(201,151,62,0.18);
}
section[data-testid="stSidebar"] .stRadio label:has(input:checked) p {
    color: var(--gold) !important;
    font-weight: 700 !important;
}

/* Sidebar buttons (Log out) — the default solid-ink button is invisible
   against the ink-green sidebar background, so give it its own treatment. */
section[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: 1px solid rgba(244,241,232,0.28);
    color: #F4F1E8 !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(244,241,232,0.1);
    border-color: var(--gold);
    color: #fff !important;
    transform: none;
    box-shadow: none;
}

/* ---------- Brand header ---------- */
.brand-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    padding: 4px 0 16px 0;
    border-bottom: 2px dashed var(--line);
    margin-bottom: 26px;
}
.brand-header .mark {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 2.05rem;
    color: var(--ink);
    letter-spacing: -0.015em;
}
.brand-header .tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--gold);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    background: rgba(201,151,62,0.12);
    padding: 3px 9px;
    border-radius: 20px;
}

/* ---------- KPI row (real container — see app.py panel/kpi_row) ---------- */
div[class*="st-key-kpi_row"] > div {
    gap: 18px;
}
div[class*="st-key-kpi_row"] {
    margin-bottom: 8px;
}

/* ---------- KPI receipt-stub cards ---------- */
.kpi-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 22px 20px 16px 20px;
    position: relative;
    box-shadow: 0 1px 2px rgba(11,59,46,0.04), 0 6px 16px rgba(11,59,46,0.05);
    border-bottom: 2px solid var(--gold);
    margin-top: 10px;
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.kpi-card:hover {
    box-shadow: 0 2px 4px rgba(11,59,46,0.06), 0 14px 28px rgba(11,59,46,0.10);
    transform: translateY(-2px);
}
/* torn-perforation edge along the top, like a receipt stub */
.kpi-card::before {
    content: "";
    position: absolute;
    top: -7px;
    left: 6px;
    right: 6px;
    height: 14px;
    background-image: radial-gradient(circle at 7px 7px, var(--paper) 6px, transparent 6.5px);
    background-size: 14px 14px;
    background-repeat: repeat-x;
    background-position: 0 0;
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
    font-size: 2.1rem;
    color: var(--ink);
    margin-top: 6px;
}
.kpi-card .kpi-sub {
    font-size: 0.78rem;
    color: var(--muted);
    margin-top: 2px;
}

/* ---------- Generic content panels (real st.container(key="panel_*")) ---------- */
div[class*="st-key-panel_"],
div[class*="st-key-auth_wrap"] {
    background:
        repeating-linear-gradient(to bottom, transparent, transparent 27px, rgba(11,59,46,0.028) 28px),
        var(--card);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 24px 26px;
    box-shadow: 0 1px 2px rgba(11,59,46,0.04), 0 6px 16px rgba(11,59,46,0.04);
    margin-bottom: 18px;
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}
div[class*="st-key-panel_"]:hover {
    box-shadow: 0 2px 4px rgba(11,59,46,0.06), 0 14px 28px rgba(11,59,46,0.10);
}
.panel-title {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 1.15rem;
    color: var(--ink);
    margin-bottom: 14px;
}

/* ---------- Empty states ---------- */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 30px 10px 18px 10px;
    color: var(--muted);
}
.empty-icon {
    font-size: 1.7rem;
    margin-bottom: 8px;
    opacity: 0.65;
}
.empty-text {
    font-size: 0.88rem;
}

/* ---------- Sale total readout ---------- */
.sale-total {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--ink);
    margin: 6px 0 4px 0;
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
.stDownloadButton > button {
    background: var(--gold);
    color: var(--ink);
    border: none;
    border-radius: 8px;
    font-weight: 700;
    font-family: 'Inter', sans-serif;
    transition: all 0.15s ease;
}
.stDownloadButton > button:hover {
    background: #b7862f;
    color: #fff;
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(11,59,46,0.2);
}

/* ---------- Link-style buttons (auth screen navigation) ---------- */
div[class*="st-key-link_"] .stButton > button {
    background: transparent !important;
    color: var(--muted) !important;
    font-weight: 500 !important;
    padding: 0 !important;
    text-decoration: underline;
    box-shadow: none !important;
}
div[class*="st-key-link_"] .stButton > button:hover {
    background: transparent !important;
    color: var(--ink) !important;
    transform: none !important;
    box-shadow: none !important;
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
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    color: var(--muted);
    border-radius: 8px 8px 0 0;
    padding: 8px 4px;
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
@keyframes authRise {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}

div[class*="st-key-auth_wrap"] {
    max-width: 440px;
    margin: 24px auto 0 auto;
    border-radius: 18px;
    padding: 40px 38px 32px 38px;
    box-shadow: 0 1px 2px rgba(11,59,46,0.04), 0 24px 60px rgba(11,59,46,0.12);
    animation: authRise 0.45s ease-out;
}
div[class*="st-key-auth_wrap"] h3 { margin-bottom: 2px; }
.auth-sub { color: var(--muted); font-size: 0.92rem; margin-bottom: 24px; }

.auth-hero {
    background: linear-gradient(155deg, var(--ink) 0%, #0E4A38 55%, var(--ink-light) 100%);
    border-radius: 18px;
    padding: 44px 34px;
    height: 100%;
    min-height: 420px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 24px 60px rgba(11,59,46,0.25);
}
.auth-hero::before {
    content: "";
    position: absolute;
    inset: 0;
    background-image: repeating-linear-gradient(
        transparent, transparent 27px, rgba(244,241,232,0.05) 28px
    );
    pointer-events: none;
}
.auth-hero .hero-mark {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 2.4rem;
    color: #F4F1E8;
    margin-bottom: 6px;
    position: relative;
}
.auth-hero .hero-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 26px;
    position: relative;
}
.auth-hero .hero-line {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    color: rgba(244,241,232,0.88);
    font-size: 0.94rem;
    margin-bottom: 14px;
    position: relative;
    line-height: 1.4;
}
.auth-hero .hero-line .dot {
    color: var(--gold);
    font-size: 1.1rem;
    line-height: 1;
    margin-top: 1px;
}
.auth-hero .hero-receipt {
    margin-top: 30px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.76rem;
    color: rgba(244,241,232,0.55);
    border-top: 1px dashed rgba(244,241,232,0.25);
    padding-top: 16px;
    position: relative;
}

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

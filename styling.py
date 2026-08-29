"""
styling.py — Custom CSS for Smart Supermarket Inventory & Sales Analytics System.

Design tokens
-------------
Colors:
  --ink        #0B3B2E   deep ledger green (primary)
  --ink-light  #14543F   secondary green (hover/accents)
  --ink-deep   #06201A   near-black green — dramatic bands (sidebar, auth hero)
  --gold       #C9973E   receipt-stamp gold (highlight/CTA — used as a pinpoint
                          accent, never as a large fill, so it stays a stamp
                          rather than becoming the page's dominant color)
  --gold-bright #E7C077  hover / glow variant of gold
  --paper      #FAF7F0   warm paper background
  --card       #FFFFFF   card surface
  --line       #DED5BE   hairline / dividers
  --ink-text   #14201A   primary text (darkened for higher contrast)
  --muted      #63705F   secondary text
  --danger     #B3432B   out-of-stock / error
  --success    #2E7D4F   in-stock / success

Type:
  Display  — 'Fraunces'      (headings, KPI numbers, receipt totals)
  Body     — 'Inter'         (all UI text)
  Mono     — 'JetBrains Mono' (barcodes, prices, table figures — this is the
             loudest voice in the system, not a quiet caption face, because
             the whole product is about reading numbers fast)

Signature: this is a point-of-sale system, so the UI borrows its vocabulary
from an actual thermal receipt — perforated KPI stubs, a dashed "tear line"
under every panel title, a printed-ledger rule texture on every card, and a
sidebar that reads like the spine of a till roll. The goal is for every
surface to look like it was punched out of the same roll of receipt paper.

Cards are real st.container(key=...) elements (see app.py's panel() helper,
which prefixes every key with "panel_") rather than raw markdown divs, so the
styling actually wraps the content instead of floating as an empty box
beside it.
"""

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700;9..144,900&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700;800&display=swap');

:root {
    --ink: #0B3B2E;
    --ink-light: #14543F;
    --ink-deep: #06201A;
    --gold: #C9973E;
    --gold-bright: #E7C077;
    --paper: #FAF7F0;
    --card: #FFFFFF;
    --line: #DED5BE;
    --ink-text: #14201A;
    --muted: #63705F;
    --danger: #B3432B;
    --success: #2E7D4F;
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation-duration: 0.001ms !important; transition-duration: 0.001ms !important; }
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--ink-text);
}

.stApp {
    background:
        radial-gradient(circle at 12% 8%, rgba(201,151,62,0.08) 0%, transparent 42%),
        radial-gradient(circle at 88% 92%, rgba(11,59,46,0.07) 0%, transparent 45%),
        var(--paper);
}

/* branded top accent bar across the whole app, like a masthead rule */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 5px;
    background: linear-gradient(90deg, var(--ink-deep) 0%, var(--gold) 50%, var(--ink-deep) 100%);
    z-index: 999999;
}

.block-container {
    padding-top: 2.2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1180px;
}

h1, h2, h3 {
    font-family: 'Fraunces', serif !important;
    font-weight: 700 !important;
    color: var(--ink) !important;
    letter-spacing: -0.015em;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background:
        repeating-linear-gradient(
            180deg, rgba(255,255,255,0.025) 0px, rgba(255,255,255,0.025) 1px,
            transparent 1px, transparent 28px
        ),
        linear-gradient(180deg, var(--ink-deep) 0%, var(--ink) 100%);
    border-right: 1px solid rgba(0,0,0,0.2);
}
section[data-testid="stSidebar"] * {
    color: #F4F1E8 !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 6px 0 18px 0;
}
.sidebar-brand-mark {
    width: 42px;
    height: 42px;
    min-width: 42px;
    border-radius: 10px;
    background: rgba(201,151,62,0.14);
    border: 1px solid rgba(201,151,62,0.35);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
}
.sidebar-brand-name {
    font-family: 'Fraunces', serif;
    font-weight: 800;
    font-size: 1.45rem;
    letter-spacing: -0.01em;
}
.sidebar-shop {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 1.02rem;
    margin-top: -6px;
    color: #F4F1E8 !important;
}
.sidebar-owner {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: var(--gold-bright) !important;
    margin-top: 2px;
}
.sidebar-divider {
    border-top: 1px dashed rgba(244,241,232,0.22);
    margin: 16px 0 14px 0;
}
.sidebar-spacer { margin-top: 14px; }

/* ---------- Sidebar nav pills ---------- */
section[data-testid="stSidebar"] .stRadio > div {
    gap: 4px;
}
section[data-testid="stSidebar"] .stRadio label {
    padding: 11px 14px;
    border-radius: 10px;
    transition: background 0.15s ease, transform 0.15s ease;
    margin-bottom: 1px;
    border-left: 3px solid transparent;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(244,241,232,0.08);
    transform: translateX(2px);
}
section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: rgba(201,151,62,0.16);
    border-left: 3px solid var(--gold);
}
section[data-testid="stSidebar"] .stRadio label:has(input:checked) p {
    color: var(--gold-bright) !important;
    font-weight: 800 !important;
}

/* Sidebar buttons (Log out) */
section[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: 1px solid rgba(244,241,232,0.3);
    color: #F4F1E8 !important;
    font-weight: 600;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(201,151,62,0.15);
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
    padding: 4px 0 18px 0;
    border-bottom: 3px dashed var(--line);
    margin-bottom: 28px;
    position: relative;
}
.brand-header .mark {
    font-family: 'Fraunces', serif;
    font-weight: 800;
    font-size: 2.3rem;
    color: var(--ink);
    letter-spacing: -0.02em;
}
.brand-header .tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--ink-deep);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    background: var(--gold-bright);
    padding: 4px 11px;
    border-radius: 3px;
}

/* ---------- KPI row (real container — see app.py panel/kpi_row) ---------- */
div[class*="st-key-kpi_row"] > div {
    gap: 18px;
}
div[class*="st-key-kpi_row"] {
    margin-bottom: 10px;
}

/* ---------- KPI receipt-stub cards ---------- */
.kpi-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 4px;
    padding: 24px 20px 18px 20px;
    position: relative;
    box-shadow: 0 1px 2px rgba(6,32,26,0.05), 0 8px 20px rgba(6,32,26,0.06);
    border-bottom: 3px solid var(--gold);
    margin-top: 12px;
    transition: box-shadow 0.2s ease, transform 0.2s ease;
    overflow: hidden;
}
.kpi-card::after {
    /* faint corner "stamp" — reinforces the stationery/ledger vocabulary */
    content: "";
    position: absolute;
    top: 10px; right: 10px;
    width: 26px; height: 26px;
    border: 1.5px dashed rgba(201,151,62,0.35);
    border-radius: 50%;
}
.kpi-card:hover {
    box-shadow: 0 2px 4px rgba(6,32,26,0.07), 0 16px 32px rgba(6,32,26,0.12);
    transform: translateY(-3px);
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
    z-index: 2;
}
.kpi-card .kpi-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: var(--muted);
    display: flex;
    align-items: center;
    gap: 6px;
}
.kpi-card .kpi-value {
    font-family: 'Fraunces', serif;
    font-weight: 800;
    font-size: 2.35rem;
    color: var(--ink);
    margin-top: 6px;
    letter-spacing: -0.02em;
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
        repeating-linear-gradient(to bottom, transparent, transparent 27px, rgba(11,59,46,0.035) 28px),
        var(--card);
    border: 1px solid var(--line);
    border-radius: 6px;
    padding: 26px 28px;
    box-shadow: 0 1px 2px rgba(6,32,26,0.05), 0 8px 20px rgba(6,32,26,0.05);
    margin-bottom: 20px;
    transition: box-shadow 0.2s ease;
    border-top: 3px solid var(--ink);
}
div[class*="st-key-panel_"]:hover {
    box-shadow: 0 2px 4px rgba(6,32,26,0.07), 0 16px 32px rgba(6,32,26,0.11);
}
.panel-title {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 1.22rem;
    color: var(--ink);
    margin-bottom: 6px;
    padding-bottom: 12px;
    border-bottom: 1px dashed var(--line);
}

/* ---------- Empty states ---------- */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 34px 10px 20px 10px;
    color: var(--muted);
}
.empty-icon {
    font-size: 1.8rem;
    margin-bottom: 8px;
    opacity: 0.6;
}
.empty-text {
    font-size: 0.9rem;
    font-weight: 500;
}

/* ---------- Sale total readout ---------- */
.sale-total {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.9rem;
    font-weight: 800;
    color: var(--ink);
    margin: 10px 0 4px 0;
    padding-top: 10px;
    border-top: 1px dashed var(--line);
}

/* ---------- Badges ---------- */
.badge {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 3px 9px;
    border-radius: 3px;
    letter-spacing: 0.03em;
}
.badge-in { background: rgba(46,125,79,0.12); color: var(--success); }
.badge-low { background: rgba(201,151,62,0.18); color: #8A6417; }
.badge-out { background: rgba(179,67,43,0.12); color: var(--danger); }

/* ---------- Buttons ---------- */
.stButton > button {
    background: var(--ink);
    color: #FAF7F0;
    border: none;
    border-radius: 6px;
    padding: 0.55rem 1.3rem;
    font-weight: 700;
    font-family: 'Inter', sans-serif;
    transition: all 0.15s ease;
}
.stButton > button:hover {
    background: var(--ink-light);
    color: #fff;
    transform: translateY(-1px);
    box-shadow: 0 6px 14px rgba(11,59,46,0.3);
}
.stButton > button[kind="primary"] {
    background: var(--gold);
    color: var(--ink-deep);
}
.stButton > button[kind="primary"]:hover {
    background: var(--gold-bright);
    color: var(--ink-deep);
    box-shadow: 0 6px 14px rgba(201,151,62,0.4);
}
.stDownloadButton > button {
    background: var(--gold);
    color: var(--ink-deep);
    border: none;
    border-radius: 6px;
    font-weight: 800;
    font-family: 'Inter', sans-serif;
    transition: all 0.15s ease;
}
.stDownloadButton > button:hover {
    background: var(--gold-bright);
    color: var(--ink-deep);
    transform: translateY(-1px);
    box-shadow: 0 6px 14px rgba(201,151,62,0.35);
}

/* ---------- Link-style buttons (auth screen navigation) ---------- */
div[class*="st-key-link_"] .stButton > button {
    background: transparent !important;
    color: var(--muted) !important;
    font-weight: 600 !important;
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
    border-radius: 6px !important;
    border: 1px solid var(--line) !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 2px rgba(201,151,62,0.35) !important;
}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif;
    font-weight: 700;
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
    border-radius: 8px;
    overflow: hidden;
}

/* ---------- Barcode field ---------- */
.barcode-scan-box {
    font-family: 'JetBrains Mono', monospace;
    background: repeating-linear-gradient(90deg, var(--ink) 0 6px, transparent 6px 12px);
    height: 5px;
    border-radius: 2px;
    margin: 8px 0 18px 0;
    opacity: 0.55;
}

/* ---------- Auth screen ---------- */
@keyframes authRise {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

div[class*="st-key-auth_wrap"] {
    max-width: 440px;
    margin: 24px auto 0 auto;
    border-radius: 10px;
    padding: 42px 38px 32px 38px;
    box-shadow: 0 1px 2px rgba(6,32,26,0.05), 0 28px 70px rgba(6,32,26,0.16);
    animation: authRise 0.5s ease-out;
    border-top: 4px solid var(--gold);
}
div[class*="st-key-auth_wrap"] h3 { margin-bottom: 2px; font-size: 1.5rem; }
.auth-sub { color: var(--muted); font-size: 0.94rem; margin-bottom: 26px; }

.auth-hero {
    background:
        repeating-linear-gradient(transparent, transparent 27px, rgba(244,241,232,0.05) 28px),
        linear-gradient(160deg, var(--ink-deep) 0%, var(--ink) 60%, var(--ink-light) 100%);
    border-radius: 10px;
    padding: 50px 42px;
    height: 100%;
    min-height: 580px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 28px 70px rgba(6,32,26,0.3);
    border-left: 5px solid var(--gold);
}
/* floating decorative orbs — pure CSS, no JS */
.hero-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(2px);
    opacity: 0.55;
    pointer-events: none;
}
.hero-orb-1 {
    width: 240px; height: 240px;
    background: radial-gradient(circle, rgba(201,151,62,0.4) 0%, transparent 70%);
    top: -70px; right: -70px;
}
.hero-orb-2 {
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(244,241,232,0.1) 0%, transparent 70%);
    bottom: -100px; left: -80px;
}
.hero-topline {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    color: var(--gold-bright);
    margin-bottom: 24px;
    position: relative;
}
.hero-topline-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--gold);
    display: inline-block;
    box-shadow: 0 0 8px var(--gold);
}
.hero-mark {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 1.55rem;
    color: rgba(244,241,232,0.8);
    margin-bottom: 16px;
    position: relative;
}
.hero-headline {
    font-family: 'Fraunces', serif;
    font-weight: 800;
    font-size: 2.9rem;
    line-height: 1.1;
    color: #F4F1E8;
    margin-bottom: 18px;
    position: relative;
    letter-spacing: -0.02em;
}
.hero-sub {
    color: rgba(244,241,232,0.78);
    font-size: 1.02rem;
    line-height: 1.6;
    max-width: 420px;
    margin-bottom: 36px;
    position: relative;
}
.hero-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    position: relative;
    margin-bottom: 32px;
}
.hero-feature {
    background: rgba(244,241,232,0.06);
    border: 1px solid rgba(244,241,232,0.14);
    border-radius: 8px;
    padding: 17px 16px 15px 16px;
    transition: background 0.2s ease, transform 0.2s ease, border-color 0.2s ease;
}
.hero-feature:hover {
    background: rgba(244,241,232,0.1);
    border-color: rgba(201,151,62,0.4);
    transform: translateY(-3px);
}
.hero-feature-icon {
    font-size: 1.35rem;
    margin-bottom: 9px;
}
.hero-feature-title {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 0.97rem;
    color: #F4F1E8;
    margin-bottom: 4px;
}
.hero-feature-desc {
    font-size: 0.79rem;
    line-height: 1.45;
    color: rgba(244,241,232,0.62);
}
.hero-receipt {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.73rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    color: rgba(244,241,232,0.5);
    border-top: 1px dashed rgba(244,241,232,0.28);
    padding-top: 16px;
    position: relative;
}

/* ---------- Misc ---------- */
hr { border-color: var(--line) !important; }
.small-muted { color: var(--muted); font-size: 0.82rem; }
footer, #MainMenu { visibility: hidden; }

/* Visible keyboard focus for accessibility */
button:focus-visible, input:focus-visible, [role="radio"]:focus-visible {
    outline: 2px solid var(--gold) !important;
    outline-offset: 2px;
}
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

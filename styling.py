"""
styling.py — Custom CSS for Smart Supermarket Inventory & Sales Analytics System.

Design tokens (v2 — "storefront admin" identity)
-------------------------------------------------
Colors:
  --navy       #131A2B   header / sidebar (deep, trustworthy, e-commerce admin)
  --navy-2     #1C2438   secondary navy (hover/panels on dark)
  --amber      #F5A623   primary accent — CTAs, prices, active states
  --amber-dark #C9840F   amber hover/pressed
  --bg         #F4F6F9   page background (light neutral, not cream/paper)
  --card       #FFFFFF   card surface
  --line       #E3E7EE   hairline / dividers
  --text       #1B2430   primary text
  --muted      #6B7688   secondary text
  --success    #1E8E5A
  --danger     #D64545

Type:
  Display  — 'Sora'   (headings — geometric, confident, modern SaaS/e-commerce)
  Body     — 'Inter'  (all UI text)
  Mono     — 'JetBrains Mono' (barcodes, prices in tables, SKUs)

Signature: real product cards. Every product gets an image tile (or a
generated placeholder if none is set), a price badge, and a stock pill —
the same visual grammar as a marketplace seller dashboard. Cards are real
st.container(key=...) elements (see app.py's panel() helper, which prefixes
every key with "panel_") so the styling wraps the content instead of
floating as an empty box beside it.
"""

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --navy: #131A2B;
    --navy-2: #1C2438;
    --amber: #F5A623;
    --amber-dark: #C9840F;
    --bg: #F4F6F9;
    --card: #FFFFFF;
    --line: #E3E7EE;
    --text: #1B2430;
    --muted: #6B7688;
    --success: #1E8E5A;
    --danger: #D64545;
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation-duration: 0.001ms !important; transition-duration: 0.001ms !important; }
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--text);
}

.stApp {
    background: var(--bg);
}

/* branded top accent bar */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: var(--amber);
    z-index: 999999;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1240px;
}

h1, h2, h3 {
    font-family: 'Sora', sans-serif !important;
    font-weight: 700 !important;
    color: var(--navy) !important;
    letter-spacing: -0.01em;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: var(--navy);
    border-right: 1px solid rgba(0,0,0,0.2);
}
section[data-testid="stSidebar"] * {
    color: #EDEFF3 !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 11px;
    padding: 6px 0 18px 0;
}
.sidebar-brand-mark {
    width: 38px;
    height: 38px;
    min-width: 38px;
    border-radius: 9px;
    background: var(--amber);
    color: var(--navy);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
}
.sidebar-brand-name {
    font-family: 'Sora', sans-serif;
    font-weight: 800;
    font-size: 1.28rem;
    letter-spacing: -0.01em;
}
.sidebar-shop {
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: 0.98rem;
    margin-top: -6px;
    color: #EDEFF3 !important;
}
.sidebar-owner {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--amber) !important;
    margin-top: 2px;
}
.sidebar-divider {
    border-top: 1px solid rgba(237,239,243,0.14);
    margin: 16px 0 14px 0;
}
.sidebar-spacer { margin-top: 14px; }

/* ---------- Sidebar nav pills ---------- */
section[data-testid="stSidebar"] .stRadio > div { gap: 4px; }
section[data-testid="stSidebar"] .stRadio label {
    padding: 10px 13px;
    border-radius: 8px;
    transition: background 0.15s ease;
    margin-bottom: 1px;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(237,239,243,0.07);
}
section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: var(--amber);
}
section[data-testid="stSidebar"] .stRadio label:has(input:checked) p {
    color: var(--navy) !important;
    font-weight: 800 !important;
}

section[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: 1px solid rgba(237,239,243,0.25);
    color: #EDEFF3 !important;
    font-weight: 600;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(245,166,35,0.14);
    border-color: var(--amber);
    color: #fff !important;
    transform: none;
    box-shadow: none;
}
.sidebar-link {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: var(--amber) !important;
    font-size: 0.84rem;
    font-weight: 600;
    text-decoration: none;
}
.sidebar-link:hover { text-decoration: underline; }

/* ---------- Brand header ---------- */
.brand-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 4px 0 18px 0;
    border-bottom: 1px solid var(--line);
    margin-bottom: 28px;
}
.brand-header .mark {
    font-family: 'Sora', sans-serif;
    font-weight: 800;
    font-size: 1.9rem;
    color: var(--navy);
    letter-spacing: -0.02em;
}
.brand-header .tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--navy);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    background: rgba(245,166,35,0.18);
    padding: 4px 11px;
    border-radius: 20px;
}

/* ---------- KPI row ---------- */
div[class*="st-key-kpi_row"] > div { gap: 16px; }
div[class*="st-key-kpi_row"] { margin-bottom: 8px; }

.kpi-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 20px 20px 18px 20px;
    position: relative;
    box-shadow: 0 1px 2px rgba(19,26,43,0.04), 0 6px 16px rgba(19,26,43,0.04);
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.kpi-card:hover {
    box-shadow: 0 4px 8px rgba(19,26,43,0.06), 0 14px 28px rgba(19,26,43,0.09);
    transform: translateY(-2px);
}
.kpi-card .kpi-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--muted);
    display: flex;
    align-items: center;
    gap: 6px;
}
.kpi-card .kpi-value {
    font-family: 'Sora', sans-serif;
    font-weight: 800;
    font-size: 2rem;
    color: var(--navy);
    margin-top: 6px;
    letter-spacing: -0.02em;
}
.kpi-card .kpi-sub {
    font-size: 0.78rem;
    color: var(--muted);
    margin-top: 2px;
}

/* ---------- Generic content panels ---------- */
div[class*="st-key-panel_"],
div[class*="st-key-auth_wrap"] {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 24px 26px;
    box-shadow: 0 1px 2px rgba(19,26,43,0.04), 0 6px 16px rgba(19,26,43,0.04);
    margin-bottom: 18px;
}
.panel-title {
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: 1.1rem;
    color: var(--navy);
    margin-bottom: 14px;
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
.empty-icon { font-size: 1.8rem; margin-bottom: 8px; opacity: 0.55; }
.empty-text { font-size: 0.9rem; font-weight: 500; }

/* ---------- Sale total readout ---------- */
.sale-total {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--navy);
    margin: 8px 0 4px 0;
}

/* ---------- Badges ---------- */
.badge {
    display: inline-block;
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
}
.badge-in { background: rgba(30,142,90,0.12); color: var(--success); }
.badge-low { background: rgba(245,166,35,0.18); color: #935E0A; }
.badge-out { background: rgba(214,69,69,0.12); color: var(--danger); }

/* ---------- Product card grid (Shopify/Amazon-style catalogue) ---------- */
.product-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 18px;
    margin-top: 4px;
}
.product-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 12px;
    overflow: hidden;
    transition: box-shadow 0.2s ease, transform 0.2s ease;
    display: flex;
    flex-direction: column;
}
.product-card:hover {
    box-shadow: 0 10px 24px rgba(19,26,43,0.1);
    transform: translateY(-3px);
}
.product-card .thumb {
    width: 100%;
    aspect-ratio: 1 / 1;
    background: #EEF1F6;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    position: relative;
}
.product-card .thumb img {
    width: 100%; height: 100%; object-fit: cover;
}
.product-card .thumb .placeholder {
    font-size: 2.1rem; opacity: 0.35;
}
.product-card .stock-pill {
    position: absolute; top: 8px; right: 8px;
    font-family: 'Inter', sans-serif; font-size: 0.65rem; font-weight: 700;
    padding: 3px 9px; border-radius: 20px; backdrop-filter: blur(2px);
}
.product-card .body { padding: 13px 14px 15px 14px; flex: 1; display: flex; flex-direction: column; }
.product-card .cat {
    font-size: 0.65rem; font-weight: 700; color: var(--amber-dark);
    text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;
}
.product-card .name {
    font-family: 'Sora', sans-serif; font-weight: 700; font-size: 0.94rem;
    color: var(--navy); line-height: 1.3; margin-bottom: 8px;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.product-card .price-row {
    margin-top: auto; display: flex; align-items: baseline; justify-content: space-between;
}
.product-card .price {
    font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 1.05rem; color: var(--navy);
}
.product-card .barcode {
    font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; color: var(--muted);
}

/* ---------- Buttons ---------- */
.stButton > button {
    background: var(--navy);
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.2rem;
    font-weight: 700;
    font-family: 'Inter', sans-serif;
    transition: all 0.15s ease;
}
.stButton > button:hover {
    background: var(--navy-2);
    transform: translateY(-1px);
    box-shadow: 0 6px 14px rgba(19,26,43,0.25);
}
.stButton > button[kind="primary"] {
    background: var(--amber);
    color: var(--navy);
}
.stButton > button[kind="primary"]:hover {
    background: var(--amber-dark);
    color: #fff;
    box-shadow: 0 6px 14px rgba(245,166,35,0.4);
}
.stDownloadButton > button {
    background: var(--amber);
    color: var(--navy);
    border: none;
    border-radius: 8px;
    font-weight: 800;
    font-family: 'Inter', sans-serif;
    transition: all 0.15s ease;
}
.stDownloadButton > button:hover {
    background: var(--amber-dark);
    color: #fff;
    transform: translateY(-1px);
    box-shadow: 0 6px 14px rgba(245,166,35,0.35);
}

/* ---------- Link-style buttons ---------- */
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
    color: var(--navy) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ---------- Inputs ---------- */
.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
    border-radius: 8px !important;
    border: 1px solid var(--line) !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 2px rgba(245,166,35,0.3) !important;
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
    color: var(--navy) !important;
    border-bottom: 3px solid var(--amber) !important;
}

/* ---------- Dataframes ---------- */
[data-testid="stDataFrame"] {
    border: 1px solid var(--line);
    border-radius: 10px;
    overflow: hidden;
}

/* ---------- Barcode field ---------- */
.barcode-scan-box {
    background: repeating-linear-gradient(90deg, var(--navy) 0 6px, transparent 6px 12px);
    height: 4px;
    border-radius: 2px;
    margin: 6px 0 16px 0;
    opacity: 0.4;
}

/* ---------- Auth screen ---------- */
@keyframes authRise {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}
div[class*="st-key-auth_wrap"] {
    max-width: 440px;
    margin: 24px auto 0 auto;
    border-radius: 14px;
    padding: 40px 38px 32px 38px;
    box-shadow: 0 1px 2px rgba(19,26,43,0.04), 0 24px 60px rgba(19,26,43,0.1);
    animation: authRise 0.45s ease-out;
}
div[class*="st-key-auth_wrap"] h3 { margin-bottom: 2px; }
.auth-sub { color: var(--muted); font-size: 0.92rem; margin-bottom: 24px; }

.auth-hero {
    background: linear-gradient(155deg, var(--navy) 0%, var(--navy-2) 100%);
    border-radius: 14px;
    padding: 48px 40px;
    height: 100%;
    min-height: 560px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 24px 60px rgba(19,26,43,0.25);
}
.hero-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(2px);
    opacity: 0.5;
    pointer-events: none;
}
.hero-orb-1 {
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(245,166,35,0.32) 0%, transparent 70%);
    top: -60px; right: -60px;
}
.hero-orb-2 {
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(237,239,243,0.08) 0%, transparent 70%);
    bottom: -90px; left: -70px;
}
.hero-topline {
    display: flex; align-items: center; gap: 8px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
    letter-spacing: 0.1em; color: var(--amber); margin-bottom: 22px; position: relative;
}
.hero-topline-dot {
    width: 6px; height: 6px; border-radius: 50%; background: var(--amber); display: inline-block;
}
.hero-mark {
    font-family: 'Sora', sans-serif; font-weight: 700; font-size: 1.4rem;
    color: rgba(237,239,243,0.8); margin-bottom: 14px; position: relative;
}
.hero-headline {
    font-family: 'Sora', sans-serif; font-weight: 800; font-size: 2.5rem; line-height: 1.14;
    color: #F4F6F9; margin-bottom: 16px; position: relative; letter-spacing: -0.01em;
}
.hero-sub {
    color: rgba(244,246,249,0.75); font-size: 1rem; line-height: 1.55;
    max-width: 420px; margin-bottom: 34px; position: relative;
}
.hero-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; position: relative; margin-bottom: 30px; }
.hero-feature {
    background: rgba(244,246,249,0.06); border: 1px solid rgba(244,246,249,0.12);
    border-radius: 10px; padding: 16px 16px 14px 16px; transition: background 0.2s ease, transform 0.2s ease;
}
.hero-feature:hover { background: rgba(244,246,249,0.1); transform: translateY(-2px); }
.hero-feature-icon { font-size: 1.3rem; margin-bottom: 8px; }
.hero-feature-title { font-family: 'Sora', sans-serif; font-weight: 700; font-size: 0.94rem; color: #F4F6F9; margin-bottom: 4px; }
.hero-feature-desc { font-size: 0.78rem; line-height: 1.4; color: rgba(244,246,249,0.6); }
.hero-receipt {
    font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; letter-spacing: 0.03em;
    color: rgba(244,246,249,0.45); border-top: 1px dashed rgba(244,246,249,0.22); padding-top: 14px; position: relative;
}

/* ---------- Dashboard welcome hero ---------- */
.welcome-hero {
    background:
        repeating-linear-gradient(115deg, rgba(244,241,232,0.04) 0 2px, transparent 2px 26px),
        linear-gradient(135deg, var(--ink-deep) 0%, var(--ink) 55%, var(--ink-light) 100%);
    border-radius: 10px;
    padding: 30px 32px;
    margin-bottom: 24px;
    border-left: 5px solid var(--gold);
    box-shadow: 0 16px 40px rgba(6,32,26,0.18);
}
.welcome-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    color: var(--gold-bright);
    margin-bottom: 8px;
}
.welcome-title {
    font-family: 'Fraunces', serif;
    font-weight: 800;
    font-size: 1.7rem;
    color: #F6F3EA;
    letter-spacing: -0.01em;
}
.welcome-shop {
    font-weight: 500;
    color: rgba(246,243,234,0.7);
    font-size: 1.15rem;
}
.welcome-sub {
    color: rgba(246,243,234,0.68);
    font-size: 0.92rem;
    margin-top: 6px;
}

/* ---------- Product card grid (Products > All products) ---------- */
.product-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 6px;
    transition: box-shadow 0.2s ease, transform 0.2s ease;
    box-shadow: 0 1px 2px rgba(6,32,26,0.04);
}
.product-card:hover {
    box-shadow: 0 14px 30px rgba(6,32,26,0.12);
    transform: translateY(-3px);
}
.product-thumb {
    width: 100%;
    aspect-ratio: 1 / 1;
    background-size: cover;
    background-position: center;
    background-color: var(--paper-dim, #EFE7D3);
    border-bottom: 1px solid var(--line);
}
.product-thumb-empty {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.2rem;
    opacity: 0.35;
}
.product-body { padding: 14px 14px 16px 14px; }
.product-cat {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--muted);
    margin-bottom: 4px;
}
.product-name {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 0.98rem;
    color: var(--ink-text);
    margin-bottom: 10px;
    min-height: 2.4em;
    line-height: 1.2;
}
.product-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
}
.product-price {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 800;
    font-size: 1.02rem;
    color: var(--ink);
}

/* ---------- Mini product card (Sales page selection preview) ---------- */
.mini-card {
    display: flex;
    align-items: center;
    gap: 12px;
    background: var(--paper-dim, #EFE7D3);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 10px 12px;
    margin: 4px 0 16px 0;
}
.mini-thumb {
    width: 46px; height: 46px; min-width: 46px;
    border-radius: 6px;
    background-size: cover;
    background-position: center;
    background-color: var(--card);
    border: 1px solid var(--line);
}
.mini-thumb-empty {
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; opacity: 0.4;
}
.mini-cat {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.06em; color: var(--muted);
}
.mini-name {
    font-family: 'Fraunces', serif;
    font-weight: 700; font-size: 0.92rem; color: var(--ink-text);
}

/* ---------- Misc ---------- */
hr { border-color: var(--line) !important; }
.small-muted { color: var(--muted); font-size: 0.82rem; }
footer, #MainMenu { visibility: hidden; }

button:focus-visible, input:focus-visible, [role="radio"]:focus-visible {
    outline: 2px solid var(--amber) !important;
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


def _safe_url(url: str) -> str:
    """Strip characters that could break out of a CSS url('...') or HTML attribute."""
    return url.replace("'", "").replace('"', "").replace("(", "").replace(")", "")


def product_card_html(name: str, category: str, price: float, image_url, stock_badge: str) -> str:
    if image_url:
        thumb = f'<div class="product-thumb" style="background-image:url(\'{_safe_url(image_url)}\');"></div>'
    else:
        thumb = '<div class="product-thumb product-thumb-empty">📦</div>'
    return f"""
    <div class="product-card">
        {thumb}
        <div class="product-body">
            <div class="product-cat">{category}</div>
            <div class="product-name">{name}</div>
            <div class="product-row">
                <span class="product-price">₹{price:,.2f}</span>
                {stock_badge}
            </div>
        </div>
    </div>
    """


def product_mini_card_html(name: str, category: str, image_url) -> str:
    if image_url:
        thumb = f'<div class="mini-thumb" style="background-image:url(\'{_safe_url(image_url)}\');"></div>'
    else:
        thumb = '<div class="mini-thumb mini-thumb-empty">📦</div>'
    return f"""
    <div class="mini-card">
        {thumb}
        <div>
            <div class="mini-cat">{category}</div>
            <div class="mini-name">{name}</div>
        </div>
    </div>
    """


def stock_badge(stock: int) -> str:
    if stock <= 0:
        return '<span class="badge badge-out">OUT OF STOCK</span>'
    elif stock <= 5:
        return f'<span class="badge badge-low">LOW · {stock} left</span>'
    return f'<span class="badge badge-in">IN STOCK · {stock}</span>'


def product_card_html(name: str, category: str, price: float, stock: int,
                       barcode: str = None, image_url: str = None) -> str:
    """Render one Shopify/Amazon-style product tile for the catalogue grid."""
    if stock <= 0:
        pill_style = "background:rgba(214,69,69,0.85);color:#fff;"
        pill_text = "OUT"
    elif stock <= 5:
        pill_style = "background:rgba(245,166,35,0.92);color:#1B2430;"
        pill_text = f"LOW · {stock}"
    else:
        pill_style = "background:rgba(30,142,90,0.88);color:#fff;"
        pill_text = f"{stock} in stock"

    if image_url:
        thumb = f'<img src="{image_url}" alt="{name}" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\';" /><div class="placeholder" style="display:none;">🛒</div>'
    else:
        thumb = '<div class="placeholder">🛒</div>'

    barcode_html = f'<span class="barcode">{barcode}</span>' if barcode else '<span></span>'

    return f"""
    <div class="product-card">
        <div class="thumb">
            {thumb}
            <span class="stock-pill" style="{pill_style}">{pill_text}</span>
        </div>
        <div class="body">
            <div class="cat">{category or "General"}</div>
            <div class="name">{name}</div>
            <div class="price-row">
                <span class="price">₹{price:,.2f}</span>
                {barcode_html}
            </div>
        </div>
    </div>
    """

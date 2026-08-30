"""
styling.py — Custom CSS for Smart Supermarket Inventory & Sales Analytics System.

Design tokens (v3 — "editorial ledger")
----------------------------------------
Same brand colors as before, executed with much more restraint and scale,
inspired by editorial/hospitality sites: oversized confident typography,
generous whitespace, a panoramic photographic hero on the dashboard, and
accents used sparingly (a thin rule or a single label) instead of scattered
badges and decorative stationery textures.

Colors:
  --ink        #0B3B2E   deep ledger green (primary)
  --ink-light  #14543F   secondary green (hover/accents)
  --ink-deep   #06201A   near-black green — hero bands
  --gold       #C9973E   accent — used sparingly (rules, labels, one CTA)
  --gold-bright #E7C077  hover / glow variant of gold
  --paper      #FAF7F0   warm paper background
  --paper-dim  #EFE7D3   slightly deeper cream for alternating surfaces
  --card       #FFFFFF   card surface
  --line       #E7DFC9   hairline / dividers (lighter than v2 — quieter)
  --ink-text   #14201A   primary text
  --muted      #6B7566   secondary text
  --danger     #B3432B   out-of-stock / error
  --success    #2E7D4F   in-stock / success

Type:
  Display  — 'Fraunces'  (oversized wordmark, hero headline, KPI numbers —
             pushed much bigger and looser than v2 for an editorial feel)
  Body     — 'Inter'     (all UI text)
  Mono     — 'JetBrains Mono' (barcodes, prices, category labels)

Cards are real st.container(key=...) elements (see app.py's panel() helper,
which prefixes every key with "panel_") so the styling wraps the content
instead of floating as an empty box beside it.
"""

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700;9..144,900&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&family=Parisienne&display=swap');

:root {
    --ink: #0B3B2E;
    --ink-light: #14543F;
    --ink-deep: #06201A;
    --gold: #C9973E;
    --gold-bright: #E7C077;
    --paper: #FAF7F0;
    --paper-dim: #EFE7D3;
    --card: #FFFFFF;
    --line: #E7DFC9;
    --ink-text: #14201A;
    --muted: #6B7566;
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

.stApp { background: var(--paper); }

[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--gold);
    z-index: 999999;
}

.block-container {
    padding-top: 2.6rem !important;
    padding-bottom: 4rem !important;
    max-width: 1220px;
}

h1, h2, h3 {
    font-family: 'Fraunces', serif !important;
    font-weight: 700 !important;
    color: var(--ink) !important;
    letter-spacing: -0.02em;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: var(--ink-deep);
    border-right: 1px solid rgba(0,0,0,0.2);
}
section[data-testid="stSidebar"] * { color: #F4F1E8 !important; }
section[data-testid="stSidebar"] .stRadio label {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
}

.sidebar-brand { display: flex; align-items: center; gap: 12px; padding: 8px 0 22px 0; }
.sidebar-brand-mark {
    width: 40px; height: 40px; min-width: 40px;
    border-radius: 9px;
    background: rgba(201,151,62,0.14);
    border: 1px solid rgba(201,151,62,0.3);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem;
}
.sidebar-brand-name {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 1.3rem;
    letter-spacing: -0.01em;
}
.sidebar-shop {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 0.98rem;
    margin-top: -4px;
    color: rgba(244,241,232,0.92) !important;
}
.sidebar-owner {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--gold-bright) !important;
    margin-top: 3px;
}
.sidebar-divider { border-top: 1px solid rgba(244,241,232,0.12); margin: 20px 0 16px 0; }
.sidebar-spacer { margin-top: 16px; }

section[data-testid="stSidebar"] .stRadio > div { gap: 2px; }
section[data-testid="stSidebar"] .stRadio label {
    padding: 12px 14px;
    border-radius: 8px;
    transition: background 0.15s ease;
    margin-bottom: 1px;
}
section[data-testid="stSidebar"] .stRadio label:hover { background: rgba(244,241,232,0.06); }
section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: rgba(244,241,232,0.08);
    border-left: 2px solid var(--gold);
}
section[data-testid="stSidebar"] .stRadio label:has(input:checked) p {
    color: var(--gold-bright) !important;
    font-weight: 700 !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: 1px solid rgba(244,241,232,0.22);
    color: #F4F1E8 !important;
    font-weight: 500;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(201,151,62,0.12);
    border-color: var(--gold);
    color: #fff !important;
    transform: none;
    box-shadow: none;
}
.sidebar-link {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: var(--gold-bright) !important;
    font-size: 0.84rem;
    font-weight: 500;
    text-decoration: none;
}
.sidebar-link:hover { text-decoration: underline; }

/* ---------- Brand header — oversized editorial wordmark ---------- */
.brand-header {
    padding: 6px 0 30px 0;
    margin-bottom: 8px;
}
.brand-header .mark {
    display: block;
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: clamp(2.6rem, 5vw, 4rem);
    color: var(--ink);
    letter-spacing: -0.03em;
    line-height: 1;
}
.brand-header .tag {
    display: block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--muted);
    letter-spacing: 0.22em;
    text-transform: uppercase;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid var(--line);
}

/* ---------- KPI row ---------- */
div[class*="st-key-kpi_row"] > div { gap: 20px; }
div[class*="st-key-kpi_row"] { margin-bottom: 12px; }

.kpi-card {
    background: transparent;
    border: none;
    border-top: 1px solid var(--line);
    border-radius: 0;
    padding: 18px 0 0 0;
    position: relative;
    transition: opacity 0.2s ease;
}
.kpi-card:hover { opacity: 0.82; }
.kpi-card .kpi-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.66rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    display: flex;
    align-items: center;
    gap: 6px;
}
.kpi-card .kpi-value {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: clamp(2rem, 3vw, 2.6rem);
    color: var(--ink);
    margin-top: 8px;
    letter-spacing: -0.02em;
}
.kpi-card .kpi-sub { font-size: 0.78rem; color: var(--muted); margin-top: 4px; }

/* ---------- Generic content panels ---------- */
div[class*="st-key-panel_"],
div[class*="st-key-auth_wrap"] {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 4px;
    padding: 36px 38px;
    box-shadow: 0 1px 2px rgba(6,32,26,0.03);
    margin-bottom: 28px;
}
.panel-title {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 1.4rem;
    color: var(--ink);
    margin-bottom: 22px;
}

/* ---------- Empty states ---------- */
.empty-state {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    text-align: center; padding: 44px 10px 26px 10px; color: var(--muted);
}
.empty-icon { font-size: 1.7rem; margin-bottom: 10px; opacity: 0.5; }
.empty-text { font-size: 0.92rem; font-weight: 400; }

/* ---------- Sale total ---------- */
.sale-total {
    font-family: 'Fraunces', serif;
    font-size: 2.1rem;
    font-weight: 600;
    color: var(--ink);
    margin: 14px 0 6px 0;
    padding-top: 14px;
    border-top: 1px solid var(--line);
}

/* ---------- Badges ---------- */
.badge {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.66rem;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 20px;
    letter-spacing: 0.03em;
}
.badge-in { background: rgba(46,125,79,0.1); color: var(--success); }
.badge-low { background: rgba(201,151,62,0.16); color: #8A6417; }
.badge-out { background: rgba(179,67,43,0.1); color: var(--danger); }

/* ---------- Buttons ---------- */
.stButton > button {
    background: var(--ink) !important;
    color: #FAF7F0 !important;
    border: none !important;
    border-radius: 4px;
    padding: 0.6rem 1.4rem;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    transition: all 0.15s ease;
}
.stButton > button:hover { background: var(--ink-light) !important; color: #fff !important; }
.stButton > button[kind="primary"] { background: var(--gold) !important; color: var(--ink-deep) !important; }
.stButton > button[kind="primary"]:hover { background: var(--gold-bright) !important; color: var(--ink-deep) !important; }
.stDownloadButton > button {
    background: var(--gold) !important; color: var(--ink-deep) !important; border: none !important;
    border-radius: 4px; font-weight: 700; font-family: 'Inter', sans-serif;
}
.stDownloadButton > button:hover { background: var(--gold-bright) !important; color: var(--ink-deep) !important; }

div[class*="st-key-link_"] .stButton > button {
    background: transparent !important; color: var(--muted) !important;
    font-weight: 500 !important; padding: 0 !important; text-decoration: underline; box-shadow: none !important;
}
div[class*="st-key-link_"] .stButton > button:hover { background: transparent !important; color: var(--ink) !important; }

/* ---------- Inputs ---------- */
.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
    border-radius: 4px !important; border: 1px solid var(--line) !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--gold) !important; box-shadow: 0 0 0 2px rgba(201,151,62,0.28) !important;
}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif; font-weight: 600; color: var(--muted);
    border-radius: 0; padding: 10px 4px;
}
.stTabs [aria-selected="true"] { color: var(--ink) !important; border-bottom: 2px solid var(--gold) !important; }

/* ---------- Dataframes ---------- */
[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 4px; overflow: hidden; }

/* ---------- Barcode field ---------- */
.barcode-scan-box {
    background: repeating-linear-gradient(90deg, var(--ink) 0 6px, transparent 6px 12px);
    height: 3px; border-radius: 2px; margin: 10px 0 22px 0; opacity: 0.4;
}

/* ---------- Auth screen ---------- */
@keyframes authRise { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }

div[class*="st-key-auth_wrap"] {
    max-width: 440px; margin: 20px auto 0 auto;
    border-radius: 4px; padding: 46px 40px 34px 40px;
    box-shadow: 0 1px 2px rgba(6,32,26,0.04), 0 24px 60px rgba(6,32,26,0.1);
    animation: authRise 0.5s ease-out;
}
div[class*="st-key-auth_wrap"] h3 { margin-bottom: 4px; font-size: 1.5rem; }
.auth-sub { color: var(--muted); font-size: 0.94rem; margin-bottom: 28px; }

.auth-hero {
    background:
        linear-gradient(180deg, rgba(6,32,26,0.5) 0%, rgba(6,32,26,0.62) 45%, rgba(6,32,26,0.92) 100%),
        url('https://images.unsplash.com/photo-1604719312566-8912e9227c6a?auto=format&fit=crop&w=1600&q=70');
    background-size: cover;
    background-position: center;
    border-radius: 4px;
    padding: 44px 46px 32px 46px;
    height: 100%;
    min-height: 660px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}
.hero-orb { position: absolute; border-radius: 50%; filter: blur(2px); opacity: 0.35; pointer-events: none; }
.hero-orb-1 { width: 260px; height: 260px; background: radial-gradient(circle, rgba(201,151,62,0.3) 0%, transparent 70%); top: -80px; right: -80px; }
.hero-orb-2 { width: 300px; height: 300px; background: radial-gradient(circle, rgba(244,241,232,0.06) 0%, transparent 70%); bottom: -110px; left: -90px; }
.hero-top {
    display: flex; align-items: center; justify-content: space-between; position: relative; gap: 16px;
}
.hero-topline {
    display: flex; align-items: center; gap: 9px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; font-weight: 600;
    letter-spacing: 0.16em; color: var(--gold-bright); position: relative;
}
.hero-topline-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--gold); display: inline-block; }
.hero-mark {
    font-family: 'Fraunces', serif; font-weight: 500; font-size: 1.3rem;
    color: rgba(244,241,232,0.85); position: relative;
}
.hero-mid { position: relative; margin: auto 0; padding: 28px 0; }
.hero-script {
    font-family: 'Parisienne', cursive; font-weight: 400;
    font-size: clamp(1.9rem, 3.2vw, 2.5rem); line-height: 1;
    color: var(--gold-bright); margin-bottom: 4px; position: relative;
}
.hero-headline {
    font-family: 'Fraunces', serif; font-weight: 700; font-size: clamp(2.1rem, 3.8vw, 3.1rem);
    line-height: 1.08; color: #F6F3EA; margin-bottom: 20px; position: relative;
    letter-spacing: 0.01em; text-transform: uppercase;
}
.hero-sub {
    color: rgba(246,243,234,0.72); font-size: 1.02rem; line-height: 1.65;
    max-width: 420px; margin-bottom: 34px; position: relative; font-weight: 300;
}
.hero-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; position: relative; }
.hero-feature {
    background: rgba(15,26,22,0.38); border: 1px solid rgba(244,241,232,0.16);
    backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
    border-radius: 4px; padding: 18px 17px 16px 17px; transition: background 0.2s ease;
}
.hero-feature:hover { background: rgba(15,26,22,0.55); }
.hero-feature-icon { font-size: 1.3rem; margin-bottom: 10px; }
.hero-feature-title { font-family: 'Fraunces', serif; font-weight: 600; font-size: 0.96rem; color: #F4F1E8; margin-bottom: 4px; }
.hero-feature-desc { font-size: 0.79rem; line-height: 1.45; color: rgba(244,241,232,0.6); font-weight: 300; }
.hero-bottom-bar {
    display: flex; align-items: flex-end; justify-content: space-between; gap: 24px; flex-wrap: wrap;
    border-top: 1px solid rgba(244,241,232,0.22); padding-top: 18px; position: relative;
}
.hero-bottom-left {
    font-size: 0.82rem; line-height: 1.5; color: rgba(244,241,232,0.65); max-width: 320px; font-weight: 300;
}
.hero-bottom-right {
    font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; letter-spacing: 0.08em;
    color: rgba(244,241,232,0.5); text-align: right; line-height: 1.7; white-space: nowrap;
}

/* ---------- Dashboard panoramic welcome hero ---------- */
.welcome-hero {
    background:
        radial-gradient(circle at 85% 10%, rgba(201,151,62,0.14) 0%, transparent 45%),
        linear-gradient(120deg, rgba(6,32,26,0.78) 0%, rgba(11,59,46,0.74) 55%, rgba(20,84,63,0.7) 100%),
        url('https://images.unsplash.com/photo-1612819052787-618023ea329f?auto=format&fit=crop&w=1600&q=70');
    background-size: cover;
    background-position: center 40%;
    border-radius: 4px;
    padding: 64px 56px;
    margin-bottom: 40px;
    position: relative;
    overflow: hidden;
    min-height: 240px;
    display: flex;
    align-items: center;
}
.welcome-hero::after {
    /* subtle grain/texture so the photo doesn't feel flat under the overlay */
    content: "";
    position: absolute; inset: 0;
    background-image: repeating-linear-gradient(120deg, rgba(255,255,255,0.02) 0 2px, transparent 2px 5px);
    pointer-events: none;
}
.welcome-hero-text {
    position: relative;
    max-width: 600px;
}
.welcome-script {
    font-family: 'Parisienne', cursive;
    font-weight: 400;
    font-size: clamp(1.8rem, 2.8vw, 2.3rem);
    line-height: 1;
    color: var(--gold-bright);
    margin-bottom: 6px;
    position: relative;
}
.welcome-title {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: clamp(2rem, 3.6vw, 2.9rem);
    color: #F8F5EC;
    letter-spacing: 0.01em;
    line-height: 1.15;
    position: relative;
    text-transform: uppercase;
}
.welcome-shop {
    font-weight: 300;
    text-transform: none;
    color: rgba(248,245,236,0.6);
    font-size: 0.5em;
    display: block;
    margin-top: 6px;
}
.welcome-sub {
    color: rgba(248,245,236,0.62);
    font-size: 1.02rem;
    font-weight: 300;
    margin-top: 16px;
    position: relative;
    max-width: 440px;
}

/* ---------- Product card grid ---------- */
.product-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 8px;
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.product-card:hover { box-shadow: 0 18px 36px rgba(6,32,26,0.1); transform: translateY(-3px); }
.product-thumb {
    width: 100%; aspect-ratio: 1 / 1;
    background-size: cover; background-position: center;
    background-color: var(--paper-dim);
    border-bottom: 1px solid var(--line);
}
.product-thumb-empty { display: flex; align-items: center; justify-content: center; font-size: 2.2rem; opacity: 0.3; }
.product-body { padding: 16px 16px 18px 16px; }
.product-cat {
    font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); margin-bottom: 6px;
}
.product-name {
    font-family: 'Fraunces', serif; font-weight: 600; font-size: 1.02rem;
    color: var(--ink-text); margin-bottom: 12px; min-height: 2.4em; line-height: 1.25;
}
.product-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.product-price { font-family: 'Fraunces', serif; font-weight: 600; font-size: 1.08rem; color: var(--ink); }

/* ---------- Mini product card (Sales page) ---------- */
.mini-card {
    display: flex; align-items: center; gap: 14px;
    background: var(--paper-dim); border: 1px solid var(--line);
    border-radius: 4px; padding: 12px 14px; margin: 8px 0 20px 0;
}
.mini-thumb {
    width: 48px; height: 48px; min-width: 48px; border-radius: 4px;
    background-size: cover; background-position: center;
    background-color: var(--card); border: 1px solid var(--line);
}
.mini-thumb-empty { display: flex; align-items: center; justify-content: center; font-size: 1.2rem; opacity: 0.35; }
.mini-cat {
    font-family: 'JetBrains Mono', monospace; font-size: 0.6rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.07em; color: var(--muted);
}
.mini-name { font-family: 'Fraunces', serif; font-weight: 600; font-size: 0.95rem; color: var(--ink-text); }

/* ---------- Language toggle (pill-style radio) ---------- */
div[data-testid="stRadio"] div[role="radiogroup"] {
    background: rgba(0,0,0,0.04);
    border-radius: 20px;
    padding: 3px;
    display: inline-flex;
    gap: 0;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] {
    background: rgba(244,241,232,0.08);
}

/* ---------- Misc ---------- */
hr { border-color: var(--line) !important; }
.small-muted { color: var(--muted); font-size: 0.82rem; }
footer, #MainMenu { visibility: hidden; }
button:focus-visible, input:focus-visible, [role="radio"]:focus-visible {
    outline: 2px solid var(--gold) !important; outline-offset: 2px;
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

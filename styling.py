"""
styling.py — Custom CSS for Smart Supermarket Inventory & Sales Analytics System.

Design tokens (v5 — "ledger, quietly")
----------------------------------------
A deliberate move away from the earlier bold lime/orange "market ledger"
look toward the quieter, editorial register of boutique Squarespace
templates (Emmeline / Quinn / Condesa): warm ivory backgrounds, a single
restrained serif for display type, hairline rules instead of heavy borders
and drop shadows, near-zero border radius instead of pill shapes, and one
accent color used sparingly rather than several loud ones.

Colors:
  --ink        #1B1B18   warm near-black — primary text, ink fills
  --paper      #F7F3EC   ivory — page background
  --paper-alt  #EFE9DD   deeper ivory — alternating panel surface
  --card       #FFFFFF   card surface
  --line       #DDD5C7   hairline rule / divider
  --clay       #A8532E   single accent color (spice/terracotta) — used
               sparingly: primary buttons, active states, prices, links
  --clay-soft  #C98A65   hover/lighter variant of clay
  --muted      #6B6558   secondary text
  --success    #4B6B4F   in-stock / success (muted sage, not bright green)
  --danger     #9C4A3A   out-of-stock / error (muted brick)

Type:
  Display  — 'Fraunces'  (variable optical-size serif) at a light/normal
             weight and large size for headlines — the one deliberately
             editorial gesture on the page
  Body     — 'Inter'     all UI text, labels, numbers

No monospace face, no second display face — one serif, one sans, used
consistently. Shapes: hairline borders, 2–4px radius (not pill, not
heavily rounded), no drop shadows. Motion is minimal and never looping —
a page-load fade only, everything else responds to hover/focus.
"""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,400;1,9..144,500&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --ink: #1B1B18;
    --paper: #F7F3EC;
    --paper-alt: #EFE9DD;
    --card: #FFFFFF;
    --line: #DDD5C7;
    --clay: #A8532E;
    --clay-soft: #C98A65;
    --muted: #6B6558;
    --success: #4B6B4F;
    --danger: #9C4A3A;

    /* legacy aliases so any leftover references keep working */
    --forest: var(--ink);
    --forest-deep: var(--ink);
    --forest-mid: var(--muted);
    --lime: var(--paper-alt);
    --lime-soft: var(--paper-alt);
    --orange: var(--clay);
    --orange-soft: var(--clay-soft);
    --gold: var(--clay);
    --gold-bright: var(--clay-soft);
    --cream: var(--paper);
    --cream-dim: var(--paper-alt);
    --paper-dim: var(--paper-alt);
    --ink-text: var(--ink);
    --ink-light: var(--muted);
    --ink-deep: var(--ink);
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation-duration: 0.001ms !important; transition-duration: 0.001ms !important; }
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--ink);
}
.stApp { background: var(--paper); }

/* ---------- Top hairline — replaces the old animated dashed stripe ---------- */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--clay);
    z-index: 999999;
}

.block-container {
    padding-top: 2.6rem !important;
    padding-bottom: 4rem !important;
    max-width: 1180px;
}

h1, h2, h3 {
    font-family: 'Fraunces', serif !important;
    font-weight: 500 !important;
    color: var(--ink) !important;
    letter-spacing: -0.01em;
}

/* ---------- Divider rule — a plain static hairline, not an animated squiggle ---------- */
@keyframes pageFade { from { opacity: 0; } to { opacity: 1; } }
.squiggle {
    width: 48px; height: 1px; margin: 0 0 16px 0;
    background: var(--clay);
    border: none;
}
.squiggle-lime { background: var(--line); }

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: var(--ink);
    border-right: 1px solid rgba(0,0,0,0.2);
}
section[data-testid="stSidebar"] * { color: #F2EDE1 !important; }
section[data-testid="stSidebar"] .stRadio label {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    letter-spacing: 0.02em;
}
.sidebar-brand { display: flex; align-items: center; gap: 12px; padding: 4px 0 26px 0; }
.sidebar-brand-mark {
    width: 34px; height: 34px; min-width: 34px;
    border: 1px solid rgba(242,237,225,0.4);
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
}
.sidebar-brand-name {
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-weight: 500;
    font-size: 1.4rem;
    letter-spacing: 0.01em;
    color: #F2EDE1 !important;
}
.sidebar-shop {
    font-family: 'Fraunces', serif;
    font-weight: 500;
    font-size: 1rem;
    margin-top: 2px;
    color: rgba(242,237,225,0.94) !important;
}
.sidebar-owner {
    font-family: 'Inter', sans-serif;
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--clay-soft) !important;
    margin-top: 4px;
    font-weight: 600;
}
.sidebar-divider {
    border-top: 1px solid rgba(242,237,225,0.16);
    margin: 22px 0 18px 0;
}
.sidebar-spacer { margin-top: 16px; }

section[data-testid="stSidebar"] .stRadio > div { gap: 2px; }
section[data-testid="stSidebar"] .stRadio label {
    padding: 11px 6px;
    border-bottom: 1px solid transparent;
    transition: border-color 0.15s ease, opacity 0.15s ease;
    margin-bottom: 0;
    opacity: 0.72;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    opacity: 1;
    border-bottom-color: rgba(242,237,225,0.3);
}
section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: transparent;
    opacity: 1;
    border-bottom-color: var(--clay);
}
section[data-testid="stSidebar"] .stRadio label:has(input:checked) p {
    color: #F2EDE1 !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: 1px solid rgba(242,237,225,0.32);
    border-radius: 2px;
    color: #F2EDE1 !important;
    font-weight: 500;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-size: 0.78rem;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--clay);
    border-color: var(--clay);
    color: #fff !important;
    transform: none;
    box-shadow: none;
}
.sidebar-link {
    display: inline-flex; align-items: center; gap: 6px;
    color: var(--clay-soft) !important; font-size: 0.84rem; font-weight: 500; text-decoration: none;
}
.sidebar-link:hover { text-decoration: underline; }

/* ---------- Brand header ---------- */
.brand-header { padding: 4px 0 28px 0; margin-bottom: 8px; }
.brand-header .mark {
    display: block;
    font-family: 'Fraunces', serif;
    font-weight: 400;
    font-style: italic;
    font-size: clamp(2rem, 4vw, 2.8rem);
    color: var(--ink);
    letter-spacing: -0.005em;
    line-height: 1;
}
.brand-header .tag {
    display: flex; align-items: center; gap: 10px;
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--muted);
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px solid var(--line);
}

/* ---------- KPI row ---------- */
div[class*="st-key-kpi_row"] > div { gap: 1px; background: var(--line); }
div[class*="st-key-kpi_row"] { margin-bottom: 12px; border: 1px solid var(--line); }
.kpi-card {
    background: var(--card);
    border: none;
    border-radius: 0;
    padding: 26px 24px;
    position: relative;
    height: 100%;
}
.kpi-card .kpi-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.68rem;
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
    font-weight: 500;
    font-size: clamp(1.9rem, 3vw, 2.4rem);
    color: var(--ink);
    margin-top: 10px;
    letter-spacing: -0.01em;
}
.kpi-card .kpi-sub { font-size: 0.78rem; color: var(--muted); margin-top: 6px; }

/* ---------- Generic content panels ---------- */
div[class*="st-key-panel_"] {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 2px;
    padding: 38px 40px;
    box-shadow: none;
    margin-bottom: 28px;
}
.panel-title {
    font-family: 'Fraunces', serif;
    font-weight: 500;
    font-size: 1.4rem;
    color: var(--ink);
    margin-bottom: 24px;
}

/* ---------- Empty states ---------- */
.empty-state {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    text-align: center; padding: 44px 10px 26px 10px; color: var(--muted);
}
.empty-icon { font-size: 1.5rem; margin-bottom: 10px; opacity: 0.5; }
.empty-text { font-size: 0.92rem; font-weight: 400; }

/* ---------- Sale total ---------- */
.sale-total {
    font-family: 'Fraunces', serif;
    font-size: 2rem;
    font-weight: 500;
    color: var(--ink);
    margin: 14px 0 6px 0;
    padding-top: 16px;
    border-top: 1px solid var(--line);
}

/* ---------- Badges — quiet text, not stickers ---------- */
.badge {
    display: inline-block;
    font-family: 'Inter', sans-serif;
    font-size: 0.68rem;
    font-weight: 600;
    padding: 3px 0;
    letter-spacing: 0.04em;
    border: none;
    border-left: 2px solid currentColor;
    padding-left: 8px;
}
.badge-in { color: var(--success); }
.badge-low { color: var(--clay); }
.badge-out { color: var(--danger); }

/* ---------- Buttons — rectangular, restrained ---------- */
.stButton > button {
    background: transparent !important;
    color: var(--ink) !important;
    border: 1px solid var(--ink) !important;
    border-radius: 2px !important;
    padding: 0.6rem 1.4rem;
    font-weight: 500;
    font-family: 'Inter', sans-serif;
    letter-spacing: 0.03em;
    transition: all 0.15s ease;
}
.stButton > button:hover { background: var(--ink) !important; color: var(--paper) !important; transform: none; }
.stButton > button[kind="primary"] { background: var(--clay) !important; color: #fff !important; border-color: var(--clay) !important; }
.stButton > button[kind="primary"]:hover { background: var(--ink) !important; border-color: var(--ink) !important; color: #fff !important; }
.stDownloadButton > button {
    background: var(--clay) !important; color: #fff !important; border: 1px solid var(--clay) !important;
    border-radius: 2px !important; font-weight: 500; font-family: 'Inter', sans-serif; letter-spacing: 0.03em;
}
.stDownloadButton > button:hover { background: var(--ink) !important; border-color: var(--ink) !important; color: #fff !important; }
div[class*="st-key-link_"] .stButton > button {
    background: transparent !important; color: var(--muted) !important; border: none !important;
    font-weight: 500 !important; padding: 0 !important; text-decoration: underline; box-shadow: none !important;
    letter-spacing: normal;
}
div[class*="st-key-link_"] .stButton > button:hover { background: transparent !important; color: var(--clay) !important; }

/* ---------- Inputs — thin rectangular, no pill radius ---------- */
.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
    border-radius: 2px !important; border: 1px solid var(--line) !important;
    background: var(--card) !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--clay) !important; box-shadow: 0 0 0 1px var(--clay) !important;
}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 28px; border-bottom: 1px solid var(--line); }
.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif; font-weight: 500; color: var(--muted);
    border-radius: 0; padding: 10px 0; letter-spacing: 0.01em;
}
.stTabs [aria-selected="true"] { color: var(--ink) !important; border-bottom: 2px solid var(--clay) !important; }

/* ---------- Dataframes ---------- */
[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 2px; overflow: hidden; }

/* ---------- Auth screen — quiet full-bleed ivory hero, no shapes ---------- */
@keyframes authRise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes authFade { from { opacity: 0; } to { opacity: 1; } }

.auth-hero {
    background: var(--paper-alt);
    width: 100vw;
    position: relative;
    left: 50%;
    right: 50%;
    margin-left: -50vw;
    margin-right: -50vw;
    margin-top: -2.6rem;
    margin-bottom: 64px;
    padding: 64px calc(50% - 470px) 68px calc(50% - 470px);
    overflow: hidden;
    animation: authFade 0.6s ease-out;
    border-bottom: 1px solid var(--line);
}
@media (max-width: 1040px) {
    .auth-hero { padding-left: 40px; padding-right: 40px; }
}
/* decorative shapes retired — hidden if any markup still references them */
.hero-orb, .hero-orb-1, .hero-orb-2 { display: none; }

.hero-top {
    display: flex; align-items: center; justify-content: space-between;
    position: relative; gap: 16px; max-width: 900px; margin: 0 auto 48px auto;
}
.hero-topline {
    display: flex; align-items: center; gap: 9px;
    font-family: 'Inter', sans-serif; font-size: 0.68rem; font-weight: 600;
    letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted); position: relative;
}
.hero-topline-dot { width: 4px; height: 4px; border-radius: 50%; background: var(--clay); display: inline-block; }
.hero-mark {
    font-family: 'Fraunces', serif; font-weight: 400; font-style: italic; font-size: 1.3rem;
    color: var(--ink); position: relative;
}
.hero-mid {
    position: relative; max-width: 780px; margin: 0 auto; text-align: center;
}
.hero-script {
    font-family: 'Fraunces', serif; font-style: italic; font-weight: 400;
    font-size: clamp(1.2rem, 2vw, 1.5rem); line-height: 1;
    color: var(--muted); margin-bottom: 10px; position: relative;
}
.hero-headline {
    font-family: 'Fraunces', serif; font-weight: 400; font-size: clamp(2.6rem, 5.5vw, 4.4rem);
    line-height: 1.02; color: var(--ink); margin-bottom: 26px; position: relative;
    letter-spacing: -0.01em;
}
.hero-sub {
    color: var(--muted); font-size: 1.02rem; line-height: 1.65;
    max-width: 480px; margin: 0 auto 46px auto; position: relative; font-weight: 400;
}
.hero-grid {
    display: flex; flex-wrap: wrap; justify-content: center; gap: 0;
    position: relative; max-width: 860px; margin: 0 auto;
    border-top: 1px solid var(--line);
}
.hero-feature {
    background: transparent; border: none;
    padding: 24px 28px 4px 28px; text-align: left;
    border-left: 1px solid var(--line);
    flex: 1 1 190px;
}
.hero-feature:first-child { border-left: none; }
.hero-feature-icon { display: none; }
.hero-feature-title { font-family: 'Fraunces', serif; font-weight: 500; font-size: 0.98rem; color: var(--ink); margin-bottom: 6px; }
.hero-feature-desc { font-size: 0.82rem; line-height: 1.5; color: var(--muted); font-weight: 400; }
.hero-bottom-bar { display: none; }

/* Login form: plain hairline card, no shadow, no stripe */
div[class*="st-key-auth_wrap"] {
    max-width: 400px; margin: 0 auto 40px auto;
    padding: 0;
    animation: authRise 0.5s ease-out;
    background: transparent;
    border: none;
    box-shadow: none;
}
div[class*="st-key-auth_wrap"] h3 {
    margin-bottom: 8px; font-size: 1.8rem;
    font-family: 'Fraunces', serif !important;
    font-style: italic;
    font-weight: 400 !important;
    text-align: center;
}
.auth-sub {
    color: var(--muted); font-size: 0.94rem; margin-bottom: 32px; text-align: center;
}
div[class*="st-key-auth_wrap"] div[data-testid="stForm"] {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 2px;
    padding: 32px 30px;
    position: relative;
    overflow: hidden;
    box-shadow: none;
}
div[class*="st-key-auth_wrap"] div[data-testid="stRadio"] {
    text-align: center; margin-bottom: 26px;
}
div[class*="st-key-auth_wrap"] div[data-testid="stRadio"] div[role="radiogroup"] {
    display: inline-flex;
}
div[class*="st-key-auth_wrap"] .stColumns { margin-top: 20px; }

/* ---------- Dashboard welcome hero — flat ink block, no orb shapes ---------- */
.welcome-hero {
    background: var(--ink);
    border: none;
    border-radius: 2px;
    padding: 56px 52px;
    margin-bottom: 40px;
    position: relative;
    overflow: hidden;
    min-height: 190px;
    display: flex;
    align-items: center;
}
.welcome-hero::before, .welcome-hero::after { content: none; }
.welcome-hero-text { position: relative; max-width: 620px; }
.welcome-script {
    font-family: 'Fraunces', serif; font-style: italic; font-weight: 400;
    font-size: clamp(1.15rem, 2vw, 1.4rem); line-height: 1;
    color: var(--clay-soft); margin-bottom: 10px; position: relative;
}
.welcome-title {
    font-family: 'Fraunces', serif; font-weight: 400;
    font-size: clamp(1.9rem, 3.4vw, 2.6rem);
    color: var(--paper); letter-spacing: -0.005em; line-height: 1.15;
    position: relative;
}
.welcome-shop {
    font-family: 'Fraunces', serif; font-style: italic;
    font-weight: 400;
    color: var(--clay-soft); font-size: 0.46em;
    display: block; margin-top: 10px;
}
.welcome-sub {
    color: var(--paper); opacity: 0.65; font-size: 1rem; font-weight: 400;
    margin-top: 18px; position: relative; max-width: 440px;
}

/* ---------- Product card grid — hairline, no arch, no shadow ---------- */
.product-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 2px;
    overflow: hidden;
    margin-bottom: 8px;
    transition: border-color 0.15s ease;
}
.product-card:hover { border-color: var(--ink); }
.product-thumb {
    width: 100%; aspect-ratio: 1 / 1;
    background-size: cover; background-position: center;
    background-color: var(--paper-alt);
    border-bottom: 1px solid var(--line);
}
.product-thumb-empty { display: flex; align-items: center; justify-content: center; font-size: 1.8rem; opacity: 0.3; }
.product-body { padding: 16px 16px 18px 16px; }
.product-cat {
    font-family: 'Inter', sans-serif; font-size: 0.64rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.09em; color: var(--muted); margin-bottom: 8px;
}
.product-name {
    font-family: 'Fraunces', serif; font-weight: 500; font-size: 1.02rem;
    color: var(--ink); margin-bottom: 14px; min-height: 2.4em; line-height: 1.28;
}
.product-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.product-price { font-family: 'Fraunces', serif; font-weight: 500; font-size: 1.05rem; color: var(--ink); }

/* ---------- Mini product card (Sales page) ---------- */
.mini-card {
    display: flex; align-items: center; gap: 14px;
    background: var(--paper-alt); border: 1px solid var(--line);
    border-radius: 2px; padding: 12px 14px; margin: 8px 0 20px 0;
}
.mini-thumb {
    width: 44px; height: 44px; min-width: 44px; border-radius: 2px;
    background-size: cover; background-position: center;
    background-color: var(--card); border: 1px solid var(--line);
}
.mini-thumb-empty { display: flex; align-items: center; justify-content: center; font-size: 1.05rem; opacity: 0.35; }
.mini-cat {
    font-family: 'Inter', sans-serif; font-size: 0.6rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted);
}
.mini-name { font-family: 'Fraunces', serif; font-weight: 500; font-size: 0.95rem; color: var(--ink); }

/* ---------- Language toggle ---------- */
div[data-testid="stRadio"] div[role="radiogroup"] {
    background: transparent;
    border: 1px solid var(--line);
    border-radius: 2px;
    padding: 2px;
    display: inline-flex;
    gap: 0;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] {
    background: transparent;
    border-color: rgba(242,237,225,0.22);
}

/* ---------- Misc ---------- */
hr { border-color: var(--line) !important; }
.small-muted { color: var(--muted); font-size: 0.82rem; }
footer, #MainMenu { visibility: hidden; }
button:focus-visible, input:focus-visible, [role="radio"]:focus-visible {
    outline: 2px solid var(--clay) !important; outline-offset: 2px;
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
            <span class="tag"><span class="squiggle" style="margin:0;"></span>{subtitle}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card_html(label: str, value: str, sub: str = "", icon: str = "") -> str:
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
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
        thumb = '<div class="product-thumb product-thumb-empty">—</div>'
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
        thumb = '<div class="mini-thumb mini-thumb-empty">—</div>'
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
        return '<span class="badge badge-out">Out of stock</span>'
    elif stock <= 5:
        return f'<span class="badge badge-low">Low · {stock} left</span>'
    return f'<span class="badge badge-in">In stock · {stock}</span>'

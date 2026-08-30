"""
styling.py — Custom CSS for Smart Supermarket Inventory & Sales Analytics System.

Design tokens (v4 — "market ledger")
----------------------------------------
Full visual redesign. Two references were blended:
  - a bold, playful restaurant brand: chunky rounded display type, a lime/
    yellow hero block, one punchy orange CTA color, a hand-drawn squiggle
    divider, and dashed/circled "badge" stickers
  - a boutique wellness brand: a dark forest nav bar, oversized elegant
    serif wordmarks, and arched (rounded-top) cards used for pricing/
    package tiles

Colors:
  --forest       #143427   deep forest green — sidebar, footer bands, ink
  --forest-deep  #0B2018   near-black green — darkest bands
  --forest-mid   #1E4A38   secondary green — hovers, mid bands
  --lime         #E7F17A   bright lime/yellow — primary accent, hero bg
  --lime-soft    #F2F6C9   pale lime — tints, chips
  --orange       #E2623B   single punchy CTA accent (sparingly)
  --orange-soft  #F3A583   hover variant of orange
  --cream        #FBF6E6   warm paper background
  --cream-dim    #F1E9CC   slightly deeper cream for alternating surfaces
  --card         #FFFFFF   card surface
  --line         #E7DFC0   hairline / dividers
  --ink          #16261F   primary text
  --muted        #62705F   secondary text
  --danger       #B3432B   out-of-stock / error
  --success      #2E7D4F   in-stock / success

Type:
  Display  — 'Lilita One'   (oversized chunky headlines — wordmark, hero
             copy, welcome banner — the "BITE ME" energy)
  Serif    — 'Fraunces'     (panel titles, KPI numbers, quieter elegant
             moments — the "Wellness Retreat" energy)
  Body     — 'Inter'        (all UI text)
  Mono     — 'JetBrains Mono' (barcodes, prices, category labels, tags)

Shapes: pill buttons, arched (big-radius-top) cards, a repeating squiggle
divider drawn with an inline SVG data-URI, and dashed circular "sticker"
badges — all reusable via CSS classes, no changes needed in app.py.
"""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Lilita+One&family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700;9..144,900&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap');

:root {
    --forest: #143427;
    --forest-deep: #0B2018;
    --forest-mid: #1E4A38;
    --lime: #E7F17A;
    --lime-soft: #F2F6C9;
    --orange: #E2623B;
    --orange-soft: #F3A583;
    --cream: #FBF6E6;
    --cream-dim: #F1E9CC;
    --card: #FFFFFF;
    --line: #E7DFC0;
    --ink: #16261F;
    --muted: #62705F;
    --danger: #B3432B;
    --success: #2E7D4F;

    /* legacy aliases so any leftover references keep working */
    --gold: var(--orange);
    --gold-bright: var(--orange-soft);
    --paper: var(--cream);
    --paper-dim: var(--cream-dim);
    --ink-text: var(--ink);
    --ink-light: var(--forest-mid);
    --ink-deep: var(--forest-deep);
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation-duration: 0.001ms !important; transition-duration: 0.001ms !important; }
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--ink);
}
.stApp { background: var(--cream); }

[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 6px;
    background: repeating-linear-gradient(90deg, var(--orange) 0 24px, var(--lime) 24px 48px);
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
    color: var(--forest) !important;
    letter-spacing: -0.02em;
}

/* ---------- Squiggle divider (inline SVG, reused everywhere) ---------- */
.squiggle {
    width: 92px; height: 18px; margin: 0 0 14px 0;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='92' height='18' viewBox='0 0 92 18'%3E%3Cpath d='M2 9c4-8 8-8 12 0s8 8 12 0 8-8 12 0 8 8 12 0 8-8 12 0 8 8 12 0 8-8 12 0' stroke='%23E2623B' stroke-width='3' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
}
.squiggle-lime {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='92' height='18' viewBox='0 0 92 18'%3E%3Cpath d='M2 9c4-8 8-8 12 0s8 8 12 0 8-8 12 0 8 8 12 0 8-8 12 0 8 8 12 0' stroke='%23E7F17A' stroke-width='3' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: var(--forest-deep);
    border-right: 1px solid rgba(0,0,0,0.25);
}
section[data-testid="stSidebar"] * { color: #F5F2E4 !important; }
section[data-testid="stSidebar"] .stRadio label {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
}
.sidebar-brand { display: flex; align-items: center; gap: 12px; padding: 8px 0 22px 0; }
.sidebar-brand-mark {
    width: 42px; height: 42px; min-width: 42px;
    border-radius: 14px 14px 6px 14px;
    background: var(--lime);
    border: 2px solid var(--forest-mid);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.25rem;
}
.sidebar-brand-name {
    font-family: 'Lilita One', 'Fraunces', serif;
    font-weight: 400;
    font-size: 1.5rem;
    letter-spacing: 0.01em;
    color: var(--lime) !important;
}
.sidebar-shop {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 1rem;
    margin-top: -2px;
    color: rgba(245,242,228,0.94) !important;
}
.sidebar-owner {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--lime) !important;
    margin-top: 3px;
}
.sidebar-divider {
    border-top: 2px dashed rgba(245,242,228,0.18);
    margin: 20px 0 16px 0;
}
.sidebar-spacer { margin-top: 16px; }

section[data-testid="stSidebar"] .stRadio > div { gap: 4px; }
section[data-testid="stSidebar"] .stRadio label {
    padding: 12px 14px;
    border-radius: 999px;
    transition: background 0.15s ease, transform 0.15s ease;
    margin-bottom: 1px;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(245,242,228,0.07);
    transform: translateX(2px);
}
section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: var(--lime);
}
section[data-testid="stSidebar"] .stRadio label:has(input:checked) p {
    color: var(--forest-deep) !important;
    font-weight: 800 !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: 2px solid rgba(245,242,228,0.28);
    border-radius: 999px;
    color: #F5F2E4 !important;
    font-weight: 700;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--orange);
    border-color: var(--orange);
    color: #fff !important;
    transform: none;
    box-shadow: none;
}
.sidebar-link {
    display: inline-flex; align-items: center; gap: 6px;
    color: var(--lime) !important; font-size: 0.84rem; font-weight: 600; text-decoration: none;
}
.sidebar-link:hover { text-decoration: underline; }

/* ---------- Brand header — chunky editorial wordmark ---------- */
.brand-header { padding: 6px 0 30px 0; margin-bottom: 8px; }
.brand-header .mark {
    display: block;
    font-family: 'Lilita One', cursive;
    font-weight: 400;
    font-size: clamp(2.4rem, 5vw, 3.6rem);
    color: var(--forest);
    letter-spacing: 0.01em;
    line-height: 1;
    text-transform: uppercase;
}
.brand-header .tag {
    display: flex; align-items: center; gap: 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--orange);
    letter-spacing: 0.22em;
    text-transform: uppercase;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 3px dashed var(--line);
}

/* ---------- KPI row ---------- */
div[class*="st-key-kpi_row"] > div { gap: 20px; }
div[class*="st-key-kpi_row"] { margin-bottom: 12px; }
.kpi-card {
    background: var(--card);
    border: 2px solid var(--forest);
    border-radius: 26px 26px 10px 10px;
    padding: 20px 18px 18px 18px;
    position: relative;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    box-shadow: 4px 4px 0 rgba(20,52,39,0.12);
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 6px 8px 0 rgba(20,52,39,0.16); }
.kpi-card .kpi-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.66rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    display: flex;
    align-items: center;
    gap: 6px;
}
.kpi-card .kpi-value {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: clamp(1.9rem, 3vw, 2.5rem);
    color: var(--forest);
    margin-top: 8px;
    letter-spacing: -0.02em;
}
.kpi-card .kpi-sub { font-size: 0.78rem; color: var(--muted); margin-top: 4px; }

/* ---------- Generic content panels ---------- */
div[class*="st-key-panel_"],
div[class*="st-key-auth_wrap"] {
    background: var(--card);
    border: 2px solid var(--forest);
    border-radius: 30px 30px 12px 12px;
    padding: 36px 38px;
    box-shadow: 5px 5px 0 rgba(20,52,39,0.1);
    margin-bottom: 28px;
}
.panel-title {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 1.5rem;
    color: var(--forest);
    margin-bottom: 22px;
}

/* ---------- Empty states ---------- */
.empty-state {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    text-align: center; padding: 44px 10px 26px 10px; color: var(--muted);
}
.empty-icon { font-size: 1.8rem; margin-bottom: 10px; opacity: 0.55; }
.empty-text { font-size: 0.92rem; font-weight: 500; }

/* ---------- Sale total ---------- */
.sale-total {
    font-family: 'Fraunces', serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: var(--forest);
    margin: 14px 0 6px 0;
    padding-top: 14px;
    border-top: 3px dashed var(--line);
}

/* ---------- Badges — dashed "sticker" style ---------- */
.badge {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 800;
    padding: 5px 12px;
    border-radius: 999px;
    letter-spacing: 0.03em;
    border: 1.5px dashed currentColor;
}
.badge-in { background: rgba(46,125,79,0.08); color: var(--success); }
.badge-low { background: rgba(226,98,59,0.1); color: var(--orange); }
.badge-out { background: rgba(179,67,43,0.08); color: var(--danger); }

/* ---------- Buttons — pill shaped ---------- */
.stButton > button {
    background: var(--forest) !important;
    color: var(--cream) !important;
    border: none !important;
    border-radius: 999px !important;
    padding: 0.62rem 1.5rem;
    font-weight: 700;
    font-family: 'Inter', sans-serif;
    transition: all 0.15s ease;
}
.stButton > button:hover { background: var(--forest-mid) !important; color: #fff !important; transform: translateY(-1px); }
.stButton > button[kind="primary"] { background: var(--orange) !important; color: #fff !important; }
.stButton > button[kind="primary"]:hover { background: var(--orange-soft) !important; color: var(--forest-deep) !important; }
.stDownloadButton > button {
    background: var(--orange) !important; color: #fff !important; border: none !important;
    border-radius: 999px !important; font-weight: 800; font-family: 'Inter', sans-serif;
}
.stDownloadButton > button:hover { background: var(--orange-soft) !important; color: var(--forest-deep) !important; }
div[class*="st-key-link_"] .stButton > button {
    background: transparent !important; color: var(--muted) !important;
    font-weight: 600 !important; padding: 0 !important; text-decoration: underline; box-shadow: none !important;
}
div[class*="st-key-link_"] .stButton > button:hover { background: transparent !important; color: var(--forest) !important; }

/* ---------- Inputs — pill / rounded ---------- */
.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
    border-radius: 14px !important; border: 2px solid var(--line) !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--orange) !important; box-shadow: 0 0 0 3px rgba(226,98,59,0.18) !important;
}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif; font-weight: 700; color: var(--muted);
    border-radius: 999px 999px 0 0; padding: 10px 6px;
}
.stTabs [aria-selected="true"] { color: var(--forest) !important; border-bottom: 3px solid var(--orange) !important; }

/* ---------- Dataframes ---------- */
[data-testid="stDataFrame"] { border: 2px solid var(--line); border-radius: 18px; overflow: hidden; }

/* ---------- Barcode field ---------- */
.barcode-scan-box {
    background: repeating-linear-gradient(90deg, var(--forest) 0 6px, transparent 6px 12px);
    height: 3px; border-radius: 2px; margin: 10px 0 22px 0; opacity: 0.4;
}

/* ---------- Auth screen — flat bold hero, no photo ---------- */
@keyframes authRise { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }

div[class*="st-key-auth_wrap"] {
    max-width: 440px; margin: 20px auto 0 auto;
    border-radius: 30px 30px 12px 12px; padding: 46px 40px 34px 40px;
    box-shadow: 6px 6px 0 rgba(20,52,39,0.1);
    animation: authRise 0.5s ease-out;
    background: var(--card);
    border: 2px solid var(--forest);
}
div[class*="st-key-auth_wrap"] h3 {
    margin-bottom: 4px; font-size: 1.7rem;
    font-family: 'Lilita One', cursive !important;
    text-transform: uppercase;
    letter-spacing: 0.01em;
    font-weight: 400 !important;
}
.auth-sub { color: var(--muted); font-size: 0.94rem; margin-bottom: 28px; }

.auth-hero {
    background: var(--lime);
    border: 2px solid var(--forest);
    border-radius: 30px 30px 12px 12px;
    padding: 44px 46px 32px 46px;
    height: 100%;
    min-height: 660px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}
.hero-orb {
    position: absolute; border-radius: 50%; pointer-events: none;
}
.hero-orb-1 {
    width: 220px; height: 220px; background: var(--orange); opacity: 0.9;
    top: -90px; right: -90px;
    clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%);
}
.hero-orb-2 {
    width: 240px; height: 240px; border-radius: 40% 60% 55% 45% / 55% 40% 60% 45%;
    background: var(--forest); opacity: 0.9;
    bottom: -100px; left: -90px;
}
.hero-top {
    display: flex; align-items: center; justify-content: space-between; position: relative; gap: 16px;
}
.hero-topline {
    display: flex; align-items: center; gap: 9px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; font-weight: 800;
    letter-spacing: 0.16em; color: var(--forest); position: relative;
    background: var(--cream); border: 1.5px dashed var(--forest);
    padding: 6px 14px; border-radius: 999px;
}
.hero-topline-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--orange); display: inline-block; }
.hero-mark {
    font-family: 'Lilita One', cursive; font-weight: 400; font-size: 1.5rem;
    color: var(--forest); position: relative; text-transform: uppercase;
}
.hero-mid { position: relative; margin: auto 0; padding: 28px 0; }
.hero-script {
    font-family: 'Fraunces', serif; font-style: italic; font-weight: 500;
    font-size: clamp(1.5rem, 2.6vw, 1.9rem); line-height: 1;
    color: var(--forest); margin-bottom: 6px; position: relative; opacity: 0.75;
}
.hero-headline {
    font-family: 'Lilita One', cursive; font-weight: 400; font-size: clamp(2.6rem, 4.6vw, 4rem);
    line-height: 0.98; color: var(--forest); margin-bottom: 20px; position: relative;
    letter-spacing: 0.005em; text-transform: uppercase;
    -webkit-text-stroke: 0.5px var(--forest);
}
.hero-sub {
    color: var(--forest); opacity: 0.78; font-size: 1.02rem; line-height: 1.6;
    max-width: 420px; margin-bottom: 34px; position: relative; font-weight: 500;
}
.hero-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; position: relative; }
.hero-feature {
    background: var(--cream); border: 2px solid var(--forest);
    border-radius: 20px 20px 8px 8px; padding: 18px 17px 16px 17px;
    transition: transform 0.15s ease; box-shadow: 3px 3px 0 rgba(20,52,39,0.14);
}
.hero-feature:hover { transform: translateY(-3px); }
.hero-feature-icon { font-size: 1.3rem; margin-bottom: 10px; }
.hero-feature-title { font-family: 'Fraunces', serif; font-weight: 700; font-size: 0.96rem; color: var(--forest); margin-bottom: 4px; }
.hero-feature-desc { font-size: 0.79rem; line-height: 1.45; color: var(--muted); font-weight: 500; }
.hero-bottom-bar {
    display: flex; align-items: flex-end; justify-content: space-between; gap: 24px; flex-wrap: wrap;
    border-top: 3px dashed var(--forest); padding-top: 18px; position: relative;
}
.hero-bottom-left {
    font-size: 0.82rem; line-height: 1.5; color: var(--forest); opacity: 0.75; max-width: 320px; font-weight: 600;
}
.hero-bottom-right {
    font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; letter-spacing: 0.08em;
    color: var(--forest); opacity: 0.65; text-align: right; line-height: 1.7; white-space: nowrap;
}

/* ---------- Dashboard welcome hero — flat forest block ---------- */
.welcome-hero {
    background: var(--forest);
    border: 2px solid var(--forest-deep);
    border-radius: 30px 30px 12px 12px;
    padding: 60px 56px;
    margin-bottom: 40px;
    position: relative;
    overflow: hidden;
    min-height: 220px;
    display: flex;
    align-items: center;
}
.welcome-hero::before {
    content: "";
    position: absolute; top: -70px; right: -70px;
    width: 200px; height: 200px; border-radius: 50%;
    background: var(--lime); opacity: 0.9;
    clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%);
}
.welcome-hero::after {
    content: "";
    position: absolute; bottom: -90px; left: -60px;
    width: 220px; height: 220px;
    border-radius: 42% 58% 60% 40% / 55% 45% 55% 45%;
    background: var(--orange); opacity: 0.5;
}
.welcome-hero-text { position: relative; max-width: 620px; }
.welcome-script {
    font-family: 'Fraunces', serif; font-style: italic; font-weight: 500;
    font-size: clamp(1.3rem, 2.2vw, 1.7rem); line-height: 1;
    color: var(--lime); margin-bottom: 8px; position: relative;
}
.welcome-title {
    font-family: 'Lilita One', cursive; font-weight: 400;
    font-size: clamp(2.1rem, 3.8vw, 3.1rem);
    color: var(--cream); letter-spacing: 0.01em; line-height: 1.1;
    position: relative; text-transform: uppercase;
}
.welcome-shop {
    font-family: 'Fraunces', serif; font-style: italic;
    font-weight: 500; text-transform: none;
    color: var(--lime); font-size: 0.42em;
    display: block; margin-top: 8px;
}
.welcome-sub {
    color: var(--cream); opacity: 0.75; font-size: 1.02rem; font-weight: 500;
    margin-top: 16px; position: relative; max-width: 440px;
}

/* ---------- Product card grid — arched top like retreat tiles ---------- */
.product-card {
    background: var(--cream-dim);
    border: 2px solid var(--forest);
    border-radius: 28px 28px 10px 10px;
    overflow: hidden;
    margin-bottom: 8px;
    transition: box-shadow 0.2s ease, transform 0.2s ease;
    box-shadow: 4px 4px 0 rgba(20,52,39,0.1);
}
.product-card:hover { box-shadow: 6px 8px 0 rgba(20,52,39,0.14); transform: translateY(-3px); }
.product-thumb {
    width: 100%; aspect-ratio: 1 / 1;
    background-size: cover; background-position: center;
    background-color: var(--lime-soft);
    border-bottom: 2px solid var(--forest);
}
.product-thumb-empty { display: flex; align-items: center; justify-content: center; font-size: 2.2rem; opacity: 0.35; }
.product-body { padding: 16px 16px 18px 16px; }
.product-cat {
    font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.08em; color: var(--orange); margin-bottom: 6px;
}
.product-name {
    font-family: 'Fraunces', serif; font-weight: 700; font-size: 1.05rem;
    color: var(--ink); margin-bottom: 12px; min-height: 2.4em; line-height: 1.25;
}
.product-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.product-price { font-family: 'Fraunces', serif; font-weight: 700; font-size: 1.1rem; color: var(--forest); }

/* ---------- Mini product card (Sales page) ---------- */
.mini-card {
    display: flex; align-items: center; gap: 14px;
    background: var(--lime-soft); border: 2px solid var(--forest);
    border-radius: 20px 20px 8px 8px; padding: 12px 14px; margin: 8px 0 20px 0;
}
.mini-thumb {
    width: 48px; height: 48px; min-width: 48px; border-radius: 12px 12px 4px 12px;
    background-size: cover; background-position: center;
    background-color: var(--card); border: 2px solid var(--forest);
}
.mini-thumb-empty { display: flex; align-items: center; justify-content: center; font-size: 1.2rem; opacity: 0.4; }
.mini-cat {
    font-family: 'JetBrains Mono', monospace; font-size: 0.6rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.07em; color: var(--orange);
}
.mini-name { font-family: 'Fraunces', serif; font-weight: 700; font-size: 0.95rem; color: var(--ink); }

/* ---------- Language toggle (pill-style radio) ---------- */
div[data-testid="stRadio"] div[role="radiogroup"] {
    background: var(--cream-dim);
    border: 1.5px solid var(--line);
    border-radius: 999px;
    padding: 3px;
    display: inline-flex;
    gap: 0;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] {
    background: rgba(245,242,228,0.08);
    border-color: rgba(245,242,228,0.18);
}

/* ---------- Misc ---------- */
hr { border-color: var(--line) !important; }
.small-muted { color: var(--muted); font-size: 0.82rem; }
footer, #MainMenu { visibility: hidden; }
button:focus-visible, input:focus-visible, [role="radio"]:focus-visible {
    outline: 2px solid var(--orange) !important; outline-offset: 2px;
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

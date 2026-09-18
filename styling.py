"""
styling.py — Custom CSS for Smart Supermarket Inventory & Sales Analytics System.

Design tokens (v6 — "modern dashboard")
----------------------------------------
A colorful, friendly SaaS-dashboard look (think Linear / Notion / Stripe
dashboard), built specifically for an inventory & analytics tool: one bold
indigo brand accent for actions/navigation, plus a small semantic palette
(green = healthy stock, amber = low stock, rose = out of stock / delete) so
the eye can scan status at a glance. Soft lavender-tinted background, white
rounded cards with gentle shadows, Poppins for display/headings and Inter
for body & data so numbers stay crisp and readable.

Product cards are text-only — product name, category, price and stock.
There are no thumbnails anywhere in the app, so the card leads with the
name at a larger size and carries a thin gradient strip on top to keep the
grid from reading as a plain wall of text.

Colors:
  --ink          #1F2333   near-black indigo-tinted — primary text
  --bg           #F5F6FC   soft lavender-white — page background
  --card         #FFFFFF   card surface
  --border       #E7E8F5   soft border/divider
  --primary      #6366F1   indigo — brand accent, buttons, active states, links
  --primary-dark #4F46E5   hover/pressed state of primary
  --primary-soft #EEF0FE   pale indigo tint — chips, hovers, soft backgrounds
  --muted        #6B7280   secondary text
  --success      #10B981   in-stock / positive
  --success-soft #DCFCE9   pale green tint
  --warning      #F59E0B   low stock
  --warning-soft #FEF3D6   pale amber tint
  --danger       #EF4444   out-of-stock / destructive
  --danger-soft  #FEE2E2   pale rose tint

Type:
  Display  — 'Poppins' (600/700) — headings, brand wordmark, big numbers
  Body     — 'Inter'   — all UI text, labels, table data

Shapes: 12–16px radius, soft colored shadows instead of hairlines, chip-style
badges with tinted backgrounds. Motion stays minimal — a gentle fade/slide
on load, hover lifts on cards and buttons — nothing looping or distracting.

v7 additions
------------
- `html { scroll-behavior: smooth; }` + a `.hero-cta-btn` style so the auth
  hero's "Create / Log in Account" button can link to `#auth-section` and
  glide the page down to the login/signup card instead of jumping instantly.
"""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --ink: #1F2333;
    --bg: #F5F6FC;
    --bg-alt: #ECEEFA;
    --card: #FFFFFF;
    --border: #E7E8F5;
    --primary: #6366F1;
    --primary-dark: #4F46E5;
    --primary-soft: #EEF0FE;
    --muted: #6B7280;
    --success: #10B981;
    --success-soft: #DCFCE9;
    --warning: #F59E0B;
    --warning-soft: #FEF3D6;
    --danger: #EF4444;
    --danger-soft: #FEE2E2;

    /* legacy aliases so any leftover references keep working */
    --forest: var(--ink);
    --forest-deep: var(--ink);
    --forest-mid: var(--muted);
    --lime: var(--bg-alt);
    --lime-soft: var(--primary-soft);
    --orange: var(--primary);
    --orange-soft: var(--primary-dark);
    --gold: var(--warning);
    --gold-bright: var(--warning);
    --cream: var(--bg);
    --cream-dim: var(--bg-alt);
    --paper: var(--bg);
    --paper-alt: var(--bg-alt);
    --paper-dim: var(--bg-alt);
    --ink-text: var(--ink);
    --ink-light: var(--muted);
    --ink-deep: var(--ink);
    --clay: var(--primary);
    --clay-soft: var(--primary-dark);
    --line: var(--border);
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation-duration: 0.001ms !important; transition-duration: 0.001ms !important; }
    html { scroll-behavior: auto !important; }
}

html { scroll-behavior: smooth; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--ink);
}
.stApp {
    background:
        radial-gradient(circle at 6% 10%, rgba(99,102,241,0.10) 0%, transparent 32%),
        radial-gradient(circle at 94% 16%, rgba(236,72,153,0.08) 0%, transparent 34%),
        radial-gradient(circle at 12% 88%, rgba(139,92,246,0.07) 0%, transparent 36%),
        radial-gradient(circle at 90% 85%, rgba(16,185,129,0.06) 0%, transparent 32%),
        var(--bg);
    background-attachment: fixed;
}

/* ---------- Top accent bar — static, colorful gradient ---------- */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, #6366F1 0%, #8B5CF6 45%, #EC4899 100%);
    z-index: 999999;
}

.block-container {
    padding-top: 2.6rem !important;
    padding-bottom: 4rem !important;
    max-width: 1180px;
}

h1, h2, h3 {
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important;
    color: var(--ink) !important;
    letter-spacing: -0.01em;
}

/* ---------- Divider accent ---------- */
@keyframes pageFade { from { opacity: 0; transform: translateY(6px);} to { opacity: 1; transform: translateY(0);} }
.squiggle {
    width: 40px; height: 4px; margin: 0 0 16px 0;
    background: linear-gradient(90deg, var(--primary), #EC4899);
    border: none; border-radius: 4px;
}
.squiggle-lime { background: var(--border); }

/* ---------- Hero call-to-action button (auth screen) ---------- */
.hero-cta-btn {
    display: inline-block;
    margin-top: 4px;
    padding: 14px 32px;
    border-radius: 12px;
    background: linear-gradient(135deg, #6366F1, #EC4899);
    color: #fff !important;
    font-family: 'Poppins', sans-serif;
    font-weight: 600;
    font-size: 0.98rem;
    text-decoration: none !important;
    box-shadow: 0 10px 24px rgba(99,102,241,0.32);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    cursor: pointer;
    border: none;
}
.hero-cta-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 30px rgba(99,102,241,0.4);
    color: #fff !important;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #4338CA 0%, #312E81 100%);
    border-right: none;
}
section[data-testid="stSidebar"] * { color: #EEF0FE !important; }
section[data-testid="stSidebar"] .stRadio label {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
}
.sidebar-brand { display: flex; align-items: center; gap: 12px; padding: 4px 0 26px 0; }
.sidebar-brand-mark {
    width: 38px; height: 38px; min-width: 38px;
    border-radius: 11px;
    background: linear-gradient(135deg, #818CF8, #EC4899);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.05rem;
    font-family: 'Poppins', sans-serif; font-weight: 700;
    color: #fff !important;
    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
}
.sidebar-brand-name {
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    font-size: 1.35rem;
    letter-spacing: -0.01em;
    color: #fff !important;
}
.sidebar-shop {
    font-family: 'Poppins', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    margin-top: 2px;
    color: #fff !important;
}
.sidebar-owner {
    font-family: 'Inter', sans-serif;
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #C7D2FE !important;
    margin-top: 4px;
    font-weight: 700;
}
.sidebar-divider {
    border-top: 1px solid rgba(255,255,255,0.14);
    margin: 22px 0 18px 0;
}
.sidebar-spacer { margin-top: 16px; }

section[data-testid="stSidebar"] .stRadio > div { gap: 4px; }
section[data-testid="stSidebar"] .stRadio label {
    padding: 11px 14px;
    border-radius: 10px;
    transition: background 0.15s ease, opacity 0.15s ease;
    margin-bottom: 0;
    opacity: 0.82;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    opacity: 1;
    background: rgba(255,255,255,0.08);
}
section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: rgba(255,255,255,0.16);
    opacity: 1;
    box-shadow: inset 3px 0 0 0 #F472B6;
}
section[data-testid="stSidebar"] .stRadio label:has(input:checked) p {
    color: #fff !important;
    font-weight: 700 !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.1) !important;
    border: 1.5px solid rgba(255,255,255,0.28) !important;
    border-radius: 10px !important;
    color: #fff !important;
    font-weight: 600;
    font-size: 0.86rem;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, #EC4899, #F472B6) !important;
    border-color: transparent !important;
    color: #fff !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(236,72,153,0.35);
}
section[data-testid="stSidebar"] .stButton > button p,
section[data-testid="stSidebar"] .stButton > button span,
section[data-testid="stSidebar"] .stButton > button div {
    color: #fff !important;
}
.sidebar-link {
    display: inline-flex; align-items: center; gap: 6px;
    color: #C7D2FE !important; font-size: 0.84rem; font-weight: 600; text-decoration: none;
}
.sidebar-link:hover { text-decoration: underline; }

/* ---------- Brand header ---------- */
.brand-header { padding: 4px 0 28px 0; margin-bottom: 8px; }
.brand-header .mark {
    display: block;
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    font-size: clamp(1.9rem, 4vw, 2.5rem);
    background: linear-gradient(90deg, #4F46E5, #EC4899);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
    line-height: 1;
}
.brand-header .tag {
    display: flex; align-items: center; gap: 10px;
    font-family: 'Inter', sans-serif;
    font-size: 0.74rem;
    font-weight: 700;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px solid var(--border);
}

/* ---------- KPI row ---------- */
div[class*="st-key-kpi_row"] > div { gap: 16px; background: transparent; }
div[class*="st-key-kpi_row"] { margin-bottom: 12px; border: none; }
.kpi-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 22px 22px 24px 22px;
    position: relative;
    height: 100%;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(99,102,241,0.06);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.kpi-card::before {
    content: "";
    position: absolute; top: 0; left: 0; right: 0; height: 4px;
    background: var(--kpi-accent, var(--primary));
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 10px 24px rgba(99,102,241,0.14); }
.kpi-icon {
    width: 38px; height: 38px; border-radius: 11px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.15rem; margin-bottom: 14px;
    background: var(--kpi-accent-soft, var(--primary-soft));
}
.kpi-card .kpi-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    display: flex;
    align-items: center;
    gap: 6px;
}
.kpi-card .kpi-value {
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    font-size: clamp(1.8rem, 3vw, 2.3rem);
    color: var(--ink);
    margin-top: 10px;
    letter-spacing: -0.01em;
}
.kpi-card .kpi-sub { font-size: 0.8rem; color: var(--muted); margin-top: 6px; font-weight: 500; }

/* ---------- Generic content panels ---------- */
div[class*="st-key-panel_"] {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 34px 36px;
    box-shadow: 0 2px 14px rgba(99,102,241,0.06);
    margin-bottom: 28px;
}
.panel-title {
    font-family: 'Poppins', sans-serif;
    font-weight: 600;
    font-size: 1.3rem;
    color: var(--ink);
    margin-bottom: 22px;
}

/* ---------- Empty states ---------- */
.empty-state {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    text-align: center; padding: 44px 10px 26px 10px; color: var(--muted);
}
.empty-icon { font-size: 1.8rem; margin-bottom: 10px; opacity: 0.6; }
.empty-text { font-size: 0.92rem; font-weight: 500; }

/* ---------- Sale total ---------- */
.sale-total {
    font-family: 'Poppins', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary-dark);
    margin: 14px 0 6px 0;
    padding-top: 16px;
    border-top: 1px dashed var(--border);
}

/* ---------- Badges — colorful chips ---------- */
.badge {
    display: inline-block;
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 4px 10px;
    letter-spacing: 0.01em;
    border: none;
    border-radius: 999px;
}
.badge-in { color: #067A55; background: var(--success-soft); }
.badge-low { color: #B45309; background: var(--warning-soft); }
.badge-out { color: #B91C1C; background: var(--danger-soft); }

/* ---------- Buttons — rounded, colorful ---------- */
.stButton > button {
    background: var(--card) !important;
    color: var(--ink) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.4rem;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    transition: all 0.15s ease;
}
.stButton > button:hover {
    background: var(--primary-soft) !important;
    color: var(--primary-dark) !important;
    border-color: var(--primary) !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 14px rgba(99,102,241,0.18);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
    color: #fff !important; border-color: transparent !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.35);
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #4F46E5, #7C3AED) !important;
    border-color: transparent !important; color: #fff !important;
    box-shadow: 0 8px 20px rgba(99,102,241,0.4);
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #6366F1, #8B5CF6) !important; color: #fff !important; border: none !important;
    border-radius: 12px !important; font-weight: 600; font-family: 'Inter', sans-serif;
    box-shadow: 0 4px 14px rgba(99,102,241,0.3);
}
.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #4F46E5, #7C3AED) !important;
    transform: translateY(-1px); box-shadow: 0 8px 20px rgba(99,102,241,0.4);
}
div[class*="st-key-link_"] .stButton > button {
    background: transparent !important; color: var(--muted) !important; border: none !important;
    font-weight: 600 !important; padding: 0 !important; text-decoration: underline; box-shadow: none !important;
}
div[class*="st-key-link_"] .stButton > button:hover { background: transparent !important; color: var(--primary) !important; transform: none; }

/* ---------- Inputs — rounded, soft focus glow ---------- */
.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
    border-radius: 10px !important; border: 1.5px solid var(--border) !important;
    background: var(--card) !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--primary) !important; box-shadow: 0 0 0 3px var(--primary-soft) !important;
}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif; font-weight: 600; color: var(--muted);
    border-radius: 10px 10px 0 0; padding: 10px 16px;
}
.stTabs [data-baseweb="tab"]:hover { background: var(--primary-soft); color: var(--primary-dark); }
.stTabs [aria-selected="true"] {
    color: var(--primary-dark) !important; background: var(--primary-soft);
    border-bottom: 3px solid var(--primary) !important;
}

/* ---------- Dataframes ---------- */
[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 14px; overflow: hidden; }

/* ---------- Auth screen — colorful full-bleed hero ---------- */
@keyframes authRise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes authFade { from { opacity: 0; } to { opacity: 1; } }

.auth-hero {
    background: radial-gradient(circle at 15% 20%, #E0E7FF 0%, transparent 45%),
                radial-gradient(circle at 85% 0%, #FCE7F3 0%, transparent 50%),
                var(--bg-alt);
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
    border-bottom: 1px solid var(--border);
}
@media (max-width: 1040px) {
    .auth-hero { padding-left: 40px; padding-right: 40px; }
}
.hero-orb, .hero-orb-1, .hero-orb-2 { display: none; }

.hero-top {
    display: flex; align-items: center; justify-content: space-between;
    position: relative; gap: 16px; max-width: 900px; margin: 0 auto 48px auto;
}
.hero-topline {
    display: flex; align-items: center; gap: 9px;
    font-family: 'Inter', sans-serif; font-size: 0.72rem; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase; color: var(--primary-dark); position: relative;
}
.hero-topline-dot { width: 6px; height: 6px; border-radius: 50%; background: linear-gradient(135deg,#6366F1,#EC4899); display: inline-block; }
.hero-mark {
    font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 1.3rem;
    background: linear-gradient(90deg, #4F46E5, #EC4899);
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
    position: relative;
}
.hero-mid {
    position: relative; max-width: 780px; margin: 0 auto; text-align: center;
}
.hero-script {
    font-family: 'Poppins', sans-serif; font-weight: 500;
    font-size: clamp(1.1rem, 2vw, 1.35rem); line-height: 1.3;
    color: var(--muted); margin-bottom: 10px; position: relative;
}
.hero-headline {
    font-family: 'Poppins', sans-serif; font-weight: 800; font-size: clamp(2.4rem, 5vw, 3.8rem);
    line-height: 1.08; margin-bottom: 26px; position: relative;
    letter-spacing: -0.02em;
    background: linear-gradient(90deg, #1F2333 15%, #4F46E5 55%, #8B5CF6 85%);
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-sub {
    color: var(--muted); font-size: 1.02rem; line-height: 1.65;
    max-width: 480px; margin: 0 auto 32px auto; position: relative; font-weight: 500;
}
.hero-cta-wrap {
    position: relative;
    margin: 0 auto 46px auto;
    text-align: center;
}
.hero-grid {
    display: flex; flex-wrap: wrap; justify-content: center; gap: 16px;
    position: relative; max-width: 900px; margin: 0 auto;
    border-top: none;
}
.hero-feature {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 16px;
    padding: 22px 22px 18px 22px; text-align: left;
    flex: 1 1 190px;
    box-shadow: 0 2px 10px rgba(99,102,241,0.06);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.hero-feature:hover { transform: translateY(-3px); box-shadow: 0 10px 22px rgba(99,102,241,0.14); }
.hero-feature-icon { display: block; font-size: 1.4rem; margin-bottom: 10px; }
.hero-feature-title { font-family: 'Poppins', sans-serif; font-weight: 600; font-size: 0.98rem; color: var(--ink); margin-bottom: 6px; }
.hero-feature-desc { font-size: 0.85rem; line-height: 1.5; color: var(--muted); font-weight: 500; }
.hero-bottom-bar { display: none; }

/* Login form: colorful rounded card with soft glow */
div[class*="st-key-auth_wrap"] {
    max-width: 400px; margin: 0 auto 40px auto;
    padding: 0;
    animation: authRise 0.5s ease-out;
    background: transparent;
    border: none;
    box-shadow: none;
    scroll-margin-top: 40px;
}
div[class*="st-key-auth_wrap"] h3 {
    margin-bottom: 8px; font-size: 1.7rem;
    font-family: 'Poppins', sans-serif !important;
    font-weight: 700 !important;
    text-align: center;
}
.auth-sub {
    color: var(--muted); font-size: 0.94rem; margin-bottom: 32px; text-align: center; font-weight: 500;
}
div[class*="st-key-auth_wrap"] div[data-testid="stForm"] {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 32px 30px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 12px 32px rgba(99,102,241,0.14);
}
div[class*="st-key-auth_wrap"] div[data-testid="stRadio"] {
    text-align: center; margin-bottom: 26px;
}
div[class*="st-key-auth_wrap"] div[data-testid="stRadio"] div[role="radiogroup"] {
    display: inline-flex;
}
div[class*="st-key-auth_wrap"] .stColumns { margin-top: 20px; }

/* ---------- Dashboard welcome hero — colorful gradient block ---------- */
.welcome-hero {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 55%, #EC4899 100%);
    border: none;
    border-radius: 22px;
    padding: 52px 52px;
    margin-bottom: 40px;
    position: relative;
    overflow: hidden;
    min-height: 190px;
    display: flex;
    align-items: center;
    box-shadow: 0 16px 40px rgba(99,102,241,0.28);
}
.welcome-hero::before {
    content: "";
    position: absolute; top: -60px; right: -60px;
    width: 220px; height: 220px; border-radius: 50%;
    background: rgba(255,255,255,0.12);
}
.welcome-hero::after {
    content: "";
    position: absolute; bottom: -80px; right: 120px;
    width: 160px; height: 160px; border-radius: 50%;
    background: rgba(255,255,255,0.08);
}
.welcome-hero-text { position: relative; max-width: 620px; z-index: 1; }
.welcome-script {
    font-family: 'Poppins', sans-serif; font-weight: 500;
    font-size: clamp(1.1rem, 2vw, 1.3rem); line-height: 1.2;
    color: #FDE68A; margin-bottom: 8px; position: relative;
}
.welcome-title {
    font-family: 'Poppins', sans-serif; font-weight: 700;
    font-size: clamp(1.9rem, 3.4vw, 2.5rem);
    color: #fff; letter-spacing: -0.01em; line-height: 1.15;
    position: relative;
}
.welcome-shop {
    font-family: 'Poppins', sans-serif; font-style: normal;
    font-weight: 500;
    color: #E0E7FF; font-size: 0.46em;
    display: block; margin-top: 10px;
}
.welcome-sub {
    color: #EEF0FE; opacity: 0.92; font-size: 1rem; font-weight: 500;
    margin-top: 18px; position: relative; max-width: 440px;
}

/* ---------- Product card grid — text only, no thumbnails ---------- */
.product-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 8px;
    position: relative;
    height: 100%;
    box-shadow: 0 2px 10px rgba(99,102,241,0.06);
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}
.product-card::before {
    content: "";
    position: absolute; top: 0; left: 0; right: 0; height: 4px;
    background: linear-gradient(90deg, #6366F1, #8B5CF6 60%, #EC4899);
}
.product-card:hover { transform: translateY(-3px); border-color: var(--primary); box-shadow: 0 12px 26px rgba(99,102,241,0.16); }
.product-body { padding: 22px 18px 20px 18px; }
.product-cat {
    font-family: 'Inter', sans-serif; font-size: 0.66rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.07em; color: var(--primary); margin-bottom: 8px;
}
.product-name {
    font-family: 'Poppins', sans-serif; font-weight: 600; font-size: 1.12rem;
    color: var(--ink); margin-bottom: 18px; min-height: 2.6em; line-height: 1.3;
}
.product-row {
    display: flex; align-items: center; justify-content: space-between; gap: 8px;
    flex-wrap: wrap;
    padding-top: 14px; border-top: 1px solid var(--border);
}
.product-price { font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 1.05rem; color: var(--primary-dark); }

/* ---------- Mini product card (Sales page) — text only ---------- */
.mini-card {
    display: flex; align-items: center; gap: 14px;
    background: var(--primary-soft); border: 1px solid var(--border);
    border-left: 4px solid var(--primary);
    border-radius: 14px; padding: 14px 16px; margin: 8px 0 20px 0;
}
.mini-cat {
    font-family: 'Inter', sans-serif; font-size: 0.62rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.06em; color: var(--primary-dark);
}
.mini-name { font-family: 'Poppins', sans-serif; font-weight: 600; font-size: 1.02rem; color: var(--ink); }

/* ---------- Profile page ---------- */
.profile-photo-wrap {
    display: flex; justify-content: center; margin-bottom: 20px;
}
.profile-photo-wrap img {
    border-radius: 50%;
    border: 4px solid var(--primary-soft);
    box-shadow: 0 6px 18px rgba(99,102,241,0.2);
    object-fit: cover;
}
.profile-username {
    text-align: center; color: var(--muted); font-size: 0.85rem;
    font-weight: 600; margin-bottom: 24px;
}

/* ---------- Language toggle ---------- */
div[data-testid="stRadio"] div[role="radiogroup"] {
    background: var(--primary-soft);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 3px;
    display: inline-flex;
    gap: 0;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] {
    background: rgba(255,255,255,0.1);
    border-color: rgba(255,255,255,0.2);
}

/* ---------- Misc ---------- */
hr { border-color: var(--border) !important; }
.small-muted { color: var(--muted); font-size: 0.82rem; }
footer, #MainMenu { visibility: hidden; }
button:focus-visible, input:focus-visible, [role="radio"]:focus-visible {
    outline: 2px solid var(--primary) !important; outline-offset: 2px;
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


_KPI_ACCENTS = {
    "primary": ("#6366F1", "#EEF0FE"),
    "violet": ("#8B5CF6", "#F1EBFE"),
    "success": ("#10B981", "#DCFCE9"),
    "warning": ("#F59E0B", "#FEF3D6"),
    "danger": ("#EF4444", "#FEE2E2"),
}


def kpi_card_html(label: str, value: str, sub: str = "", icon: str = "", accent: str = "primary") -> str:
    color, soft = _KPI_ACCENTS.get(accent, _KPI_ACCENTS["primary"])
    icon_html = f'<div class="kpi-icon">{icon}</div>' if icon else ""
    return f"""
    <div class="kpi-card" style="--kpi-accent:{color}; --kpi-accent-soft:{soft};">
        {icon_html}
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """


def product_card_html(name: str, category: str, price: float, stock_badge: str) -> str:
    """Text-only product card: category, name, price and stock status."""
    return f"""
    <div class="product-card">
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


def product_mini_card_html(name: str, category: str) -> str:
    """Compact text-only product summary used on the Sales page."""
    return f"""
    <div class="mini-card">
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

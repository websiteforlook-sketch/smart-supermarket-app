import streamlit as st


def load_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            --navy-900: #0a1a2f;
            --navy-800: #0f2540;
            --navy-700: #16324f;
            --navy-600: #1d4165;
            --amber-500: #f5a623;
            --amber-600: #e0921a;
            --amber-100: #fdf1dc;
            --gray-50: #f7f8fa;
            --gray-100: #eef1f5;
            --gray-200: #e2e6ec;
            --gray-400: #98a2b3;
            --gray-600: #475467;
            --gray-800: #1d2939;
            --green-600: #12b76a;
            --red-600: #f04438;
            --radius: 12px;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* App background */
        .stApp {
            background: var(--gray-50);
        }

        /* Hide default Streamlit chrome */
        #MainMenu, footer, header[data-testid="stHeader"] {
            visibility: hidden;
            height: 0;
        }

        /* Main content padding */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }

        /* ---------- Sidebar ---------- */
        section[data-testid="stSidebar"] {
            background: var(--navy-900);
            border-right: 1px solid var(--navy-700);
        }
        section[data-testid="stSidebar"] * {
            color: #e7ecf3 !important;
        }
        section[data-testid="stSidebar"] .stButton button {
            width: 100%;
            text-align: left;
            background: transparent;
            border: 1px solid transparent;
            border-radius: 8px;
            padding: 0.55rem 0.9rem;
            font-weight: 500;
            font-size: 0.92rem;
            transition: all 0.15s ease;
        }
        section[data-testid="stSidebar"] .stButton button:hover {
            background: var(--navy-700);
            border-color: var(--navy-600);
        }
        section[data-testid="stSidebar"] hr {
            border-color: var(--navy-700);
        }

        .sidebar-brand {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 0.4rem 0 1.2rem 0;
        }
        .sidebar-brand-mark {
            width: 34px;
            height: 34px;
            background: var(--amber-500);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            color: var(--navy-900);
            font-size: 1rem;
        }
        .sidebar-brand-name {
            font-weight: 700;
            font-size: 1.15rem;
            letter-spacing: -0.02em;
        }
        .sidebar-user {
            font-size: 0.8rem;
            color: #9fb0c7 !important;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--navy-700);
            margin-bottom: 1rem;
        }
        .sidebar-nav-label {
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            color: #6d84a3 !important;
            text-transform: uppercase;
            margin: 0.6rem 0 0.4rem 0.2rem;
        }
        .nav-active button {
            background: var(--navy-700) !important;
            border-color: var(--amber-500) !important;
            border-left: 3px solid var(--amber-500) !important;
            color: #ffffff !important;
        }

        /* ---------- Page header ---------- */
        .page-header {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            margin-bottom: 1.6rem;
        }
        .page-title {
            font-size: 1.65rem;
            font-weight: 800;
            color: var(--gray-800);
            letter-spacing: -0.02em;
            margin: 0;
        }
        .page-subtitle {
            color: var(--gray-600);
            font-size: 0.92rem;
            margin-top: 0.15rem;
        }

        /* ---------- Metric / stat cards ---------- */
        .stat-card {
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: var(--radius);
            padding: 1.1rem 1.3rem;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
            height: 100%;
        }
        .stat-label {
            font-size: 0.76rem;
            font-weight: 600;
            color: var(--gray-600);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 0.5rem;
        }
        .stat-value {
            font-size: 1.9rem;
            font-weight: 800;
            color: var(--navy-900);
            letter-spacing: -0.02em;
            line-height: 1.1;
        }
        .stat-foot {
            font-size: 0.78rem;
            color: var(--gray-400);
            margin-top: 0.35rem;
        }
        .stat-accent-amber { border-top: 3px solid var(--amber-500); }
        .stat-accent-navy { border-top: 3px solid var(--navy-800); }
        .stat-accent-green { border-top: 3px solid var(--green-600); }
        .stat-accent-red { border-top: 3px solid var(--red-600); }

        /* ---------- Generic content card ---------- */
        .content-card {
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: var(--radius);
            padding: 1.4rem 1.5rem;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        }
        .content-card-title {
            font-size: 1.02rem;
            font-weight: 700;
            color: var(--gray-800);
            margin-bottom: 0.9rem;
        }

        /* ---------- Product cards ---------- */
        .product-card {
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: var(--radius);
            overflow: hidden;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
            transition: box-shadow 0.15s ease, transform 0.15s ease;
            margin-bottom: 1rem;
        }
        .product-card:hover {
            box-shadow: 0 8px 20px rgba(16, 24, 40, 0.10);
            transform: translateY(-2px);
        }
        .product-img-wrap {
            width: 100%;
            height: 150px;
            background: var(--gray-100);
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        .product-img-wrap img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .product-img-placeholder {
            font-size: 2rem;
            color: var(--gray-400);
        }
        .product-body {
            padding: 0.9rem 1rem 1rem 1rem;
        }
        .product-category {
            font-size: 0.68rem;
            font-weight: 700;
            color: var(--amber-600);
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .product-name {
            font-size: 0.98rem;
            font-weight: 700;
            color: var(--gray-800);
            margin: 0.15rem 0 0.4rem 0;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .product-price {
            font-size: 1.15rem;
            font-weight: 800;
            color: var(--navy-900);
        }
        .product-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 0.5rem;
            font-size: 0.78rem;
            color: var(--gray-600);
        }
        .stock-badge {
            padding: 0.15rem 0.55rem;
            border-radius: 999px;
            font-weight: 600;
            font-size: 0.72rem;
        }
        .stock-ok { background: #e7f8f0; color: var(--green-600); }
        .stock-low { background: #fdf1dc; color: var(--amber-600); }
        .stock-out { background: #fdeceb; color: var(--red-600); }

        /* ---------- Buttons ---------- */
        .stButton button {
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.88rem;
        }
        div[data-testid="stForm"] .stButton button,
        .main .stButton button {
            background: var(--navy-900);
            color: white;
            border: none;
            padding: 0.5rem 1.1rem;
        }
        .main .stButton button:hover {
            background: var(--navy-700);
        }

        /* ---------- Inputs ---------- */
        .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            border-radius: 8px !important;
            border: 1px solid var(--gray-200) !important;
        }

        /* ---------- Tables ---------- */
        .stDataFrame {
            border: 1px solid var(--gray-200);
            border-radius: var(--radius);
            overflow: hidden;
        }

        /* ---------- Login page ---------- */
        .login-wrap {
            max-width: 380px;
            margin: 4rem auto 0 auto;
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 16px;
            padding: 2.4rem 2.2rem;
            box-shadow: 0 8px 24px rgba(16, 24, 40, 0.08);
        }
        .login-brand-mark {
            width: 46px;
            height: 46px;
            background: var(--navy-900);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--amber-500);
            font-weight: 800;
            font-size: 1.3rem;
            margin: 0 auto 1rem auto;
        }
        .login-title {
            text-align: center;
            font-size: 1.35rem;
            font-weight: 800;
            color: var(--gray-800);
            margin-bottom: 0.2rem;
        }
        .login-subtitle {
            text-align: center;
            color: var(--gray-600);
            font-size: 0.88rem;
            margin-bottom: 1.6rem;
        }

        .badge-pill {
            display: inline-block;
            background: var(--amber-100);
            color: var(--amber-600);
            font-weight: 700;
            font-size: 0.72rem;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            padding: 0.25rem 0.7rem;
            border-radius: 999px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def stat_card(label, value, foot="", icon="", accent="navy"):
    return f"""
    <div class="stat-card stat-accent-{accent}">
        <div class="stat-label">{icon} {label}</div>
        <div class="stat-value">{value}</div>
        <div class="stat-foot">{foot}</div>
    </div>
    """


def product_card_html(product):
    stock = product["stock"]
    if stock == 0:
        badge = '<span class="stock-badge stock-out">Out of stock</span>'
    elif stock <= 5:
        badge = f'<span class="stock-badge stock-low">{stock} left</span>'
    else:
        badge = f'<span class="stock-badge stock-ok">{stock} in stock</span>'

    if product.get("image_url"):
        img_html = f'<img src="{product["image_url"]}" onerror="this.parentElement.innerHTML=\'<div class=&quot;product-img-placeholder&quot;>📦</div>\'" />'
    else:
        img_html = '<div class="product-img-placeholder">📦</div>'

    category = product.get("category") or "General"

    return f"""
    <div class="product-card">
        <div class="product-img-wrap">{img_html}</div>
        <div class="product-body">
            <div class="product-category">{category}</div>
            <div class="product-name" title="{product['name']}">{product['name']}</div>
            <div class="product-price">₹{product['price']:,.2f}</div>
            <div class="product-meta">
                <span>{badge}</span>
                <span>#{product['id']}</span>
            </div>
        </div>
    </div>
    """


def page_header(title, subtitle=""):
    return f"""
    <div class="page-header">
        <div>
            <div class="page-title">{title}</div>
            <div class="page-subtitle">{subtitle}</div>
        </div>
    </div>
    """

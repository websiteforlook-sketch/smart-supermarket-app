"""
app.py
SmartMart — Smart Supermarket Inventory & Sales Analytics
Main Streamlit entry point: landing page, sign up, log in, and dashboard.
"""

import streamlit as st
from database import create_user, get_user_by_username
from auth_utils import (
    hash_password,
    verify_password,
    is_valid_email,
    is_valid_username,
    password_strength_ok,
)

st.set_page_config(
    page_title="SmartMart | Inventory & Sales Analytics",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Styling — Amazon-style: full-width dark navbar + centered content below
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header[data-testid="stHeader"] {display: none;}

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, 'Segoe UI', Arial, sans-serif;
        }

        .stApp {
            background-color: #eaeded;   /* Amazon's light grey page background */
        }

        /* Kill Streamlit's default top padding so the navbar sits flush at the top */
        .block-container {
            max-width: 480px;
            padding-top: 0rem;
            padding-bottom: 3rem;
        }

        /* ---- Full-width Amazon-style top navbar ---- */
        .smartmart-navbar {
            position: relative;
            left: 50%;
            right: 50%;
            margin-left: -50vw;
            margin-right: -50vw;
            width: 100vw;
            background-color: #131921;
            padding: 14px 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin-bottom: 2.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.15);
        }

        .smartmart-navbar .nav-logo {
            font-size: 1.9rem;
            line-height: 1;
        }

        .smartmart-navbar .nav-text {
            display: flex;
            flex-direction: column;
            line-height: 1.1;
        }

        .smartmart-navbar .nav-title {
            font-family: Georgia, 'Times New Roman', serif;
            font-weight: 700;
            font-size: 1.5rem;
            color: #ffffff;
        }

        .smartmart-navbar .nav-subtitle {
            font-size: 0.72rem;
            color: #d5d9d9;
            letter-spacing: 0.02em;
        }

        /* ---- Auth / content card, Amazon login-box style ---- */
        .auth-card {
            background: #ffffff;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 1.75rem 1.75rem 1.5rem 1.75rem;
            box-shadow: 0 2px 5px rgba(15,17,17,0.15);
        }

        .card-heading {
            font-size: 1.6rem;
            font-weight: 400;
            color: #0f1111;
            margin-bottom: 1.1rem;
        }

        .field-label {
            font-size: 0.85rem;
            font-weight: 700;
            color: #0f1111;
            margin-bottom: -0.6rem;
        }

        /* Primary buttons — Amazon yellow/orange gradient */
        div.stButton > button, div.stFormSubmitButton > button {
            width: 100%;
            background: linear-gradient(to bottom, #f7dfa5, #f0c14b);
            color: #0f1111;
            border: 1px solid #a88734;
            border-radius: 8px;
            padding: 0.55rem 0;
            font-weight: 500;
            font-size: 0.95rem;
            transition: filter 0.1s ease-in-out;
        }

        div.stButton > button:hover, div.stFormSubmitButton > button:hover {
            filter: brightness(0.96);
            border-color: #9c7e31;
            color: #0f1111;
        }

        div.stButton > button:focus {
            box-shadow: none !important;
        }

        .switch-text {
            text-align: center;
            margin-top: 1.4rem;
            color: #565959;
            font-size: 0.85rem;
        }

        hr.divider {
            border: none;
            border-top: 1px solid #e7e7e7;
            margin: 1.25rem 0;
        }

        .small-print {
            font-size: 0.75rem;
            color: #565959;
            text-align: center;
            margin-top: 1.5rem;
            line-height: 1.4;
        }

        .stTextInput>div>div>input {
            border-radius: 4px;
            border: 1px solid #a6a6a6;
        }

        .stTextInput>div>div>input:focus {
            border-color: #e77600;
            box-shadow: 0 0 0 3px rgba(228,121,17,0.5);
        }

        /* Dashboard "welcome" strip under the navbar */
        .dash-card {
            background: #ffffff;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 1.5rem 1.75rem;
            box-shadow: 0 2px 5px rgba(15,17,17,0.1);
            margin-bottom: 1.25rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None


def go_to(page_name: str):
    st.session_state.page = page_name


def navbar():
    st.markdown(
        """
        <div class="smartmart-navbar">
            <div class="nav-logo">🛒</div>
            <div class="nav-text">
                <div class="nav-title">SmartMart</div>
                <div class="nav-subtitle">SMART SUPERMARKET INVENTORY &amp; SALES ANALYTICS</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Landing page — choose Create Account or Log In
# ---------------------------------------------------------------------------
def render_landing():
    navbar()
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-heading">Welcome to SmartMart</div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#565959; font-size:0.9rem; margin-top:-0.8rem;">'
        'Sign in to manage your shop, or create a free account to get started.</p>',
        unsafe_allow_html=True,
    )

    if st.button("Log In", key="landing_login"):
        go_to("login")
        st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:0.85rem; color:#0f1111; margin-bottom:0.6rem;">New to SmartMart?</p>',
        unsafe_allow_html=True,
    )
    if st.button("Create Your SmartMart Account", key="landing_signup"):
        go_to("signup")
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="small-print">By continuing, you agree that your shop and account '
        'details are stored securely and used only to power your SmartMart dashboard.</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Sign Up page
# ---------------------------------------------------------------------------
def render_signup():
    navbar()
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-heading">Create account</div>', unsafe_allow_html=True)

    with st.form("signup_form", clear_on_submit=False):
        shop_name = st.text_input("Shop Name")
        owner_name = st.text_input("Owner Name")
        email = st.text_input("Email")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        submitted = st.form_submit_button("Create Account")

        if submitted:
            errors = []
            if not shop_name.strip():
                errors.append("Shop name is required.")
            if not owner_name.strip():
                errors.append("Owner name is required.")
            if not is_valid_email(email):
                errors.append("Please enter a valid email address.")
            if not is_valid_username(username):
                errors.append(
                    "Username must be 3-20 characters (letters, numbers, underscores only)."
                )
            if not password_strength_ok(password):
                errors.append(
                    "Password must be at least 8 characters and include a letter and a number."
                )
            if password != confirm_password:
                errors.append("Passwords do not match.")

            if errors:
                for err in errors:
                    st.error(err)
            else:
                pw_hash = hash_password(password)
                success, message = create_user(
                    shop_name.strip(), owner_name.strip(), email.strip().lower(),
                    username.strip(), pw_hash,
                )
                if success:
                    st.success(message + " You can now log in.")
                    go_to("login")
                    st.rerun()
                else:
                    st.error(message)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(
        '<div class="switch-text">Already have a SmartMart account?</div>',
        unsafe_allow_html=True,
    )
    if st.button("Log In Instead", key="signup_to_login"):
        go_to("login")
        st.rerun()


# ---------------------------------------------------------------------------
# Log In page
# ---------------------------------------------------------------------------
def render_login():
    navbar()
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-heading">Sign in</div>', unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In")

        if submitted:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                user = get_user_by_username(username.strip())
                if user and verify_password(password, user["password_hash"]):
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    go_to("dashboard")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown(
        '<div class="switch-text" style="margin-top:0;">New to SmartMart?</div>',
        unsafe_allow_html=True,
    )
    if st.button("Create Your SmartMart Account", key="login_to_signup"):
        go_to("signup")
        st.rerun()


# ---------------------------------------------------------------------------
# Dashboard (placeholder — build out inventory/analytics screens here)
# ---------------------------------------------------------------------------
def render_dashboard():
    user = st.session_state.user
    navbar()

    st.markdown('<div class="dash-card">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="card-heading" style="margin-bottom:0.25rem;">'
        f'Welcome back, {user["owner_name"]}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p style="color:#565959; font-size:0.9rem;">Managing <b>{user["shop_name"]}</b></p>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="dash-card">', unsafe_allow_html=True)
    st.markdown('<p style="font-weight:600; margin-bottom:0.75rem;">Account details</p>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <p style="font-size:0.9rem; color:#0f1111; line-height:1.9; margin:0;">
            <b>Shop Name:</b> {user['shop_name']}<br>
            <b>Owner Name:</b> {user['owner_name']}<br>
            <b>Email:</b> {user['email']}<br>
            <b>Username:</b> {user['username']}
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.info("Inventory and sales analytics will appear here next.")

    if st.button("Log Out"):
        st.session_state.authenticated = False
        st.session_state.user = None
        go_to("landing")
        st.rerun()


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
if st.session_state.authenticated:
    render_dashboard()
elif st.session_state.page == "signup":
    render_signup()
elif st.session_state.page == "login":
    render_login()
else:
    render_landing()

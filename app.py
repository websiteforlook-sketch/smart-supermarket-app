"""
app.py — Smart Supermarket Inventory & Sales Analytics System
Streamlit + TiDB Cloud (MySQL-compatible) + Pandas/Matplotlib + OpenPyXL

Note on product images
----------------------
Product images (drawn icons, auto-matched illustrations and real web photos)
were removed from this app entirely. Products are identified by name,
category, price and stock only. If the `products` table in an older
deployment still has an `image_url` column, it is simply ignored — nothing
reads or writes it.

Note on profile photos
-----------------------
Unlike product images, the shopkeeper's own profile photo IS supported
(uploaded on the new Profile page and stored as bytes in users.profile_photo).
This is unrelated to the old, removed product-photo feature. The photo is
also shown as a small round avatar in the sidebar, next to the SmartMart
wordmark.

Dashboard KPI updates
----------------------
- The "Profit today" KPI now relabels itself to "Loss today" (with the
  matching translated string) when today_profit is negative, instead of
  just tinting the same "Profit today" label red. The displayed number is
  the absolute value of the loss so it doesn't show a confusing double
  negative like "Loss today: -₹120".
- The "Low stock alerts" KPI card is now a clickable anchor link that
  smooth-scrolls the page down to the "Low stock — restock soon" panel
  (id="low-stock-section"), using the same `html { scroll-behavior: smooth; }`
  CSS already used for the auth-screen hero CTA.

Remove-product fix
-------------------
Removing a product used to crash with
StreamlitWidgetAlreadyInstantiatedError right after a successful delete,
because the old code reset st.session_state["remove_confirm"] (the
checkbox's own widget key) *after* that checkbox had already been
instantiated in the same run — Streamlit only allows setting a widget's
session_state value before that widget is created. The Remove tab now uses
a separate plain flag ("_reset_remove_confirm") that is applied before the
checkbox widget exists on the next run, so the checkbox correctly resets to
unchecked after a successful removal without crashing.

Cost price editing (Products → All products → Edit)
------------------------------------------------------
Previously there was no way to fix a product's cost_price after it was
created — the Edit expander only exposed Stock. This mattered a lot for
bulk-uploaded products: db.bulk_upsert_products() only recognizes a
cost_price column if the uploaded sheet has one named cost_price/cost/
purchase_price/cp (case-insensitive); anything else imports with
cost_price=0. With cost_price stuck at 0, profit always equals revenue
exactly (profit = total_price - 0), so "Profit today" never differs from
"Sales today" and a real loss day can never be detected. The Edit expander
now also has a Cost price input, wired to the existing (previously unused)
db.update_cost_price().
"""
import io
import base64
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows

import db
import styling
import i18n

# ---------------------------------------------------------------------------
# Page config + one-time setup
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="SmartMart — Inventory & Sales",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded",
)

styling.inject_css()
db.init_tables()

if "user" not in st.session_state:
    st.session_state.user = None
if "auth_view" not in st.session_state:
    st.session_state.auth_view = "login"  # "login" | "signup" | "forgot"
if "lang" not in st.session_state:
    st.session_state.lang = "en"  # "en" | "gu" — see i18n.py

PALETTE = {
    "ink": "#1F2333",
    "clay": "#6366F1",
    "muted": "#6B7280",
    "success": "#10B981",
    "danger": "#EF4444",
}

# The app is built for Indian kirana/grocery shops. "Today" and the morning/
# afternoon/evening greeting should reflect the shop's local time (IST),
# not whatever timezone the server happens to be running in — Streamlit
# Cloud runs its servers on UTC, so using datetime.now() unqualified showed
# "Good afternoon" well into the evening in India.
IST = ZoneInfo("Asia/Kolkata")


def panel(key: str):
    """
    A real, properly-nested styled card — replaces the old '<div class="panel">
    ... </div>' markdown pattern, which rendered content as *siblings* of the
    div rather than children, leaving empty ghost boxes on the page.

    st.container(key=...) gives Streamlit a genuine wrapping element we can
    target with CSS (see styling.py, selector on [class*="st-key-panel_"]).

    NOTE: the key is prefixed with "panel_" here so every call site
    (panel("dash_top_sellers"), panel("prod_manual"), etc.) actually lands on
    a Streamlit-generated class like `st-key-panel_dash_top_sellers`, which is
    what styling.py's CSS selector matches. Without this prefix the CSS never
    matched anything and every panel rendered completely unstyled.
    """
    return st.container(key=f"panel_{key}")


def chart_style(fig, ax):
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("#E7E8F5")
    ax.tick_params(colors=PALETTE["muted"], labelsize=9)
    ax.title.set_color(PALETTE["ink"])
    ax.xaxis.label.set_color(PALETTE["muted"])
    ax.yaxis.label.set_color(PALETTE["muted"])


def empty_state(icon: str, text: str):
    st.markdown(
        f'<div class="empty-state"><div class="empty-icon">{icon}</div>'
        f'<div class="empty-text">{text}</div></div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Auth screens
# ---------------------------------------------------------------------------
def _auth_hero():
    st.markdown(
        f"""
        <div class="auth-hero">
            <div class="hero-top">
                <div class="hero-mark">SmartMart</div>
                <div class="hero-topline">
                    <span class="hero-topline-dot"></span>
                    {i18n.t("hero_eyebrow")}
                </div>
            </div>
            <div class="hero-mid">
                <div class="hero-script">{i18n.t("hero_script")}</div>
                <div class="hero-headline">{i18n.t("hero_caps")}</div>
                <div class="hero-sub">
                    {i18n.t("hero_sub")}
                </div>
                <div style="margin-bottom:42px;">
                    <a href="#auth-section" class="hero-cta-btn">{i18n.t("hero_cta")}</a>
                </div>
                <div class="hero-grid">
                    <div class="hero-feature">
                        <div class="hero-feature-title">{i18n.t("feat_stock_title")}</div>
                        <div class="hero-feature-desc">{i18n.t("feat_stock_desc")}</div>
                    </div>
                    <div class="hero-feature">
                        <div class="hero-feature-title">{i18n.t("feat_barcode_title")}</div>
                        <div class="hero-feature-desc">{i18n.t("feat_barcode_desc")}</div>
                    </div>
                    <div class="hero-feature">
                        <div class="hero-feature-title">{i18n.t("feat_dash_title")}</div>
                        <div class="hero-feature-desc">{i18n.t("feat_dash_desc")}</div>
                    </div>
                    <div class="hero-feature">
                        <div class="hero-feature-title">{i18n.t("feat_export_title")}</div>
                        <div class="hero-feature-desc">{i18n.t("feat_export_desc")}</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def auth_screen():
    # Full-bleed hero band up top, spanning the whole page — not a boxed panel.
    _auth_hero()

    st.markdown(
        '<div style="text-align:center; margin-top:-24px;">'
        '<span class="squiggle" style="display:inline-block;"></span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Anchor target for the hero "Create / Log in Account" button — clicking
    # it smooth-scrolls straight down to the login/signup card below
    # (smooth-scroll behavior is enabled globally in styling.py).
    st.markdown('<div id="auth-section"></div>', unsafe_allow_html=True)

    # Login form sits centered directly on the page below it, no card border
    # around the whole thing — just the form itself gets a light lift.
    left, mid, right = st.columns([1, 1.15, 1])
    with mid:
        with st.container(key="auth_wrap"):
            i18n.render_lang_toggle(key_suffix="auth")
            view = st.session_state.auth_view

            if view == "login":
                st.markdown(f"### {i18n.t('welcome_back')}")
                st.markdown(f'<div class="auth-sub">{i18n.t("login_sub")}</div>',
                            unsafe_allow_html=True)
                with st.form("login_form"):
                    u = st.text_input(i18n.t("username"))
                    p = st.text_input(i18n.t("password"), type="password")
                    submitted = st.form_submit_button(i18n.t("log_in"), type="primary", use_container_width=True)

                if submitted:
                    if not u or not p:
                        st.warning(i18n.t("fill_both_fields"))
                    else:
                        user = db.verify_user(u.strip(), p)
                        if user:
                            st.session_state.user = {
                                "id": user["id"],
                                "username": user["username"],
                                "shop_name": user.get("shop_name") or "",
                                "owner_name": user.get("owner_name") or "",
                            }
                            st.rerun()
                        else:
                            st.error(i18n.t("wrong_login"))

                c1, c2 = st.columns(2)
                with c1:
                    with st.container(key="link_forgot"):
                        if st.button(i18n.t("forgot_password")):
                            st.session_state.auth_view = "forgot"
                            st.rerun()
                with c2:
                    with st.container(key="link_signup"):
                        if st.button(i18n.t("create_account_link")):
                            st.session_state.auth_view = "signup"
                            st.rerun()

            elif view == "signup":
                st.markdown(f"### {i18n.t('setup_shop')}")
                st.markdown(f'<div class="auth-sub">{i18n.t("setup_sub")}</div>',
                            unsafe_allow_html=True)
                with st.form("signup_form"):
                    shop_name = st.text_input(i18n.t("shop_name"))
                    owner_name = st.text_input(i18n.t("owner_name"))
                    nu = st.text_input(i18n.t("username"))
                    np1 = st.text_input(i18n.t("password"), type="password")
                    np2 = st.text_input(i18n.t("confirm_password"), type="password")
                    submitted2 = st.form_submit_button(i18n.t("create_account"), type="primary",
                                                        use_container_width=True)

                if submitted2:
                    if not all([shop_name.strip(), owner_name.strip(), nu.strip(), np1]):
                        st.warning(i18n.t("fill_all_fields"))
                    elif np1 != np2:
                        st.error(i18n.t("passwords_no_match"))
                    elif len(np1) < 4:
                        st.error(i18n.t("password_too_short"))
                    else:
                        ok, msg = db.create_user(nu.strip(), np1, shop_name, owner_name)
                        if ok:
                            user = db.verify_user(nu.strip(), np1)
                            st.session_state.user = {
                                "id": user["id"],
                                "username": user["username"],
                                "shop_name": user.get("shop_name") or "",
                                "owner_name": user.get("owner_name") or "",
                            }
                            st.toast(i18n.t("welcome_toast", shop=shop_name.strip()), icon="🎉")
                            st.rerun()
                        else:
                            st.error(msg)

                with st.container(key="link_back_login"):
                    if st.button(i18n.t("back_to_login")):
                        st.session_state.auth_view = "login"
                        st.rerun()

            elif view == "forgot":
                st.markdown(f"### {i18n.t('reset_password_title')}")
                st.markdown(
                    f'<div class="auth-sub">{i18n.t("reset_sub")}</div>',
                    unsafe_allow_html=True,
                )
                with st.form("forgot_form"):
                    fu = st.text_input(i18n.t("username"))
                    fp1 = st.text_input(i18n.t("new_password"), type="password")
                    fp2 = st.text_input(i18n.t("confirm_new_password"), type="password")
                    submitted3 = st.form_submit_button(i18n.t("update_password"), type="primary",
                                                         use_container_width=True)

                if submitted3:
                    if not fu.strip() or not fp1:
                        st.warning(i18n.t("fill_all_fields"))
                    elif fp1 != fp2:
                        st.error(i18n.t("passwords_no_match"))
                    elif len(fp1) < 4:
                        st.error(i18n.t("password_too_short"))
                    elif not db.user_exists(fu.strip()):
                        st.error(i18n.t("no_account_found"))
                    else:
                        ok, msg = db.reset_password(fu.strip(), fp1)
                        if ok:
                            st.success(msg)
                            st.session_state.auth_view = "login"
                        else:
                            st.error(msg)

                with st.container(key="link_back_login2"):
                    if st.button(i18n.t("back_to_login")):
                        st.session_state.auth_view = "login"
                        st.rerun()


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
def page_dashboard(user_id):
    styling.brand_header(i18n.t("page_dashboard"))

    products = db.get_products(user_id)
    sales = db.get_sales(user_id)

    shop = st.session_state.user.get("shop_name") or ""
    owner = st.session_state.user.get("owner_name") or st.session_state.user["username"]

    # Always compute "now" and "today" in the shop's local time (IST), not
    # the server's — see the IST constant defined near the top of this file.
    now_ist = datetime.now(IST)
    hour = now_ist.hour
    greeting = i18n.t("good_morning") if hour < 12 else (
        i18n.t("good_afternoon") if hour < 17 else i18n.t("good_evening"))

    st.markdown(
        f"""
        <div class="welcome-hero">
            <div class="welcome-hero-text">
                <div class="welcome-script">{greeting},</div>
                <div class="welcome-title">{owner.split()[0] if owner else 'there'} 👋
                    {f'<span class="welcome-shop">— {shop}</span>' if shop else ''}</div>
                <div class="welcome-sub">{i18n.t("welcome_sub")}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    total_products = len(products)
    stock_value = float((products["price"] * products["stock"]).sum()) if not products.empty else 0.0
    low_stock_count = int((products["stock"] <= 5).sum()) if not products.empty else 0

    today = now_ist.date()
    today_sales = 0.0
    today_profit = 0.0
    if not sales.empty:
        # sold_at is stored as a naive MySQL DATETIME written by
        # CURRENT_TIMESTAMP, which on TiDB Cloud is in UTC. Localize it to
        # UTC and convert to IST before comparing against "today" in IST —
        # otherwise sales made in the evening in India could be compared
        # against the wrong calendar day.
        sold_at_ist = pd.to_datetime(sales["sold_at"]).dt.tz_localize("UTC").dt.tz_convert(IST)
        today_mask = sold_at_ist.dt.date == today
        today_sales = float(sales.loc[today_mask, "total_price"].sum())

        # Profit = revenue - cost, using the cost price snapshotted on each
        # sale row at the time it was recorded (sales.cost_price), so later
        # edits to a product's cost don't rewrite historical profit.
        if "cost_price" in sales.columns:
            today_cost = float(
                (sales.loc[today_mask, "cost_price"] * sales.loc[today_mask, "quantity"]).sum()
            )
            today_profit = today_sales - today_cost

    # The 4th KPI card flips between "Profit today" and "Loss today" — not
    # just a red tint on the same "Profit today" label — whenever
    # today_profit goes negative. The displayed amount is abs(today_profit)
    # so a loss reads as "Loss today: ₹120", not "Profit today: -₹120".
    if today_profit >= 0:
        profit_label = i18n.t("kpi_profit_today")
        profit_value = f"₹{today_profit:,.0f}"
        profit_sub = i18n.t("kpi_profit_today_sub_pos")
        profit_icon = "📈"
        profit_accent = "success"
    else:
        profit_label = i18n.t("kpi_loss_today")
        profit_value = f"₹{abs(today_profit):,.0f}"
        profit_sub = i18n.t("kpi_profit_today_sub_neg")
        profit_icon = "📉"
        profit_accent = "danger"

    with st.container(key="kpi_row"):
        cols = st.columns(5)
        # Each tuple's last element is an optional anchor link the card
        # should scroll to when clicked (see styling.kpi_card_html). Only
        # the "Low stock alerts" card uses this, linking down to the
        # low-stock panel's id="low-stock-section" anchor below.
        kpis = [
            (i18n.t("kpi_products"), f"{total_products}", i18n.t("kpi_products_sub"), "📦", "primary", None),
            (i18n.t("kpi_stock_value"), f"₹{stock_value:,.0f}", i18n.t("kpi_stock_value_sub"), "💰", "violet", None),
            (i18n.t("kpi_sales_today"), f"₹{today_sales:,.0f}", today.strftime("%d %b %Y"), "🛒", "success", None),
            (profit_label, profit_value, profit_sub, profit_icon, profit_accent, None),
            (i18n.t("kpi_low_stock"), f"{low_stock_count}", i18n.t("kpi_low_stock_sub"), "⚠️", "warning",
             "#low-stock-section"),
        ]
        for c, (label, value, sub, icon, accent, link) in zip(cols, kpis):
            with c:
                st.markdown(
                    styling.kpi_card_html(label, value, sub, icon, accent, link=link),
                    unsafe_allow_html=True,
                )

    c1, c2 = st.columns(2)
    with c1:
        with panel("dash_top_sellers"):
            st.markdown(f'<div class="panel-title">🏆 {i18n.t("top_selling")}</div>', unsafe_allow_html=True)
            if sales.empty:
                empty_state("—", i18n.t("no_sales_yet"))
            else:
                top = sales.groupby("product_name")["quantity"].sum().sort_values(ascending=False).head(6)
                fig, ax = plt.subplots(figsize=(5, 3.2))
                ax.barh(top.index[::-1], top.values[::-1], color=PALETTE["clay"], height=0.55)
                ax.set_xlabel(i18n.t("units_sold"))
                chart_style(fig, ax)
                st.pyplot(fig, use_container_width=True)

    with c2:
        with panel("dash_stock_category"):
            st.markdown(f'<div class="panel-title">📊 {i18n.t("stock_by_category")}</div>', unsafe_allow_html=True)
            if products.empty:
                empty_state("—", i18n.t("no_products_yet"))
            else:
                by_cat = products.groupby("category")["stock"].sum()
                fig, ax = plt.subplots(figsize=(5, 3.2))
                colors = ["#6366F1", "#EC4899", "#F59E0B", "#10B981", "#8B5CF6", "#14B8A6"]
                ax.pie(
                    by_cat.values, labels=by_cat.index, autopct="%1.0f%%",
                    colors=colors[: len(by_cat)], textprops={"color": "#1F2333", "fontsize": 9},
                    wedgeprops={"edgecolor": "#FFFFFF", "linewidth": 2},
                )
                fig.patch.set_facecolor("#FFFFFF")
                st.pyplot(fig, use_container_width=True)

    # Anchor target for the "Low stock alerts" KPI card above. The
    # scroll-margin-top keeps the panel title from landing flush against
    # the browser's top edge after the smooth scroll (html { scroll-
    # behavior: smooth; } is set globally in styling.py).
    st.markdown(
        '<div id="low-stock-section" style="scroll-margin-top: 90px;"></div>',
        unsafe_allow_html=True,
    )
    with panel("dash_low_stock"):
        st.markdown(f'<div class="panel-title">⚠️ {i18n.t("low_stock_title")}</div>', unsafe_allow_html=True)
        if products.empty or low_stock_count == 0:
            empty_state("—", i18n.t("well_stocked"))
        else:
            low = products[products["stock"] <= 5][["name", "category", "stock", "barcode"]]
            low = low.rename(columns={
                "name": i18n.t("col_name"), "category": i18n.t("col_category"),
                "stock": i18n.t("col_stock"), "barcode": i18n.t("col_barcode"),
            })
            st.dataframe(low, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Products page (manual / bulk upload / remove / all products)
# ---------------------------------------------------------------------------
def page_products(user_id):
    styling.brand_header(i18n.t("page_products"))

    tab_manual, tab_bulk, tab_remove, tab_list = st.tabs(
        [i18n.t("tab_add_manually"), i18n.t("tab_bulk_upload"),
         i18n.t("tab_remove_product"), i18n.t("tab_all_products")]
    )

    with tab_manual:
        with panel("prod_manual"):
            with st.form("add_product_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    name = st.text_input(i18n.t("product_name"))
                    category = st.text_input(i18n.t("category"), value="General")
                with c2:
                    price = st.number_input(i18n.t("price_rs"), min_value=0.0, step=1.0, format="%.2f")
                    cost_price = st.number_input(
                        i18n.t("cost_price_rs"), min_value=0.0, step=1.0, format="%.2f"
                    )
                    stock = st.number_input(i18n.t("opening_stock"), min_value=0, step=1)
                barcode = st.text_input(i18n.t("barcode_optional"))
                submitted = st.form_submit_button(i18n.t("add_product"), type="primary")

            if submitted:
                if not name.strip():
                    st.warning(i18n.t("name_required"))
                else:
                    ok, msg = db.add_product(
                        user_id, name, category, price, stock, barcode or None, cost_price
                    )
                    st.success(msg) if ok else st.error(msg)

    with tab_bulk:
        with panel("prod_bulk"):
            st.write(i18n.t("bulk_instructions"))
            file = st.file_uploader(i18n.t("choose_file"), type=["csv", "xlsx", "xls"])
            if file is not None:
                try:
                    df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
                    st.dataframe(df.head(10), use_container_width=True, hide_index=True)
                    if st.button(i18n.t("import_products"), type="primary"):
                        success, skipped, errors = db.bulk_upsert_products(user_id, df)
                        st.success(i18n.t("imported_summary", success=success, skipped=skipped))
                        if errors:
                            with st.expander(i18n.t("see_skipped")):
                                for e in errors:
                                    st.write("• " + e)
                except Exception as e:
                    st.error(i18n.t("file_read_error", error=e))

    with tab_remove:
        with panel("prod_remove"):
            # Apply any pending reset of the confirm checkbox BEFORE that
            # checkbox widget is instantiated below. Streamlit raises
            # StreamlitWidgetAlreadyInstantiatedError if you assign to
            # st.session_state[<a widget's own key>] *after* that widget has
            # already been created in the current script run — which is
            # exactly what the old code did right after st.rerun(). Using a
            # separate plain flag here, applied before the checkbox exists,
            # avoids that entirely.
            if st.session_state.pop("_reset_remove_confirm", False):
                st.session_state["remove_confirm"] = False

            products_all = db.get_products(user_id)
            if products_all.empty:
                empty_state("—", i18n.t("no_products_add_one"))
            else:
                st.markdown(f'<div class="panel-title">{i18n.t("remove_product_title")}</div>',
                            unsafe_allow_html=True)
                options = {
                    f"{row['name']} — {row['category']} ({int(row['stock'])} in stock)": row["id"]
                    for _, row in products_all.iterrows()
                }
                choice = st.selectbox(
                    i18n.t("remove_select_product"), list(options.keys()), key="remove_select"
                )
                product_id_to_remove = options[choice]
                confirm = st.checkbox(i18n.t("remove_confirm_checkbox"), key="remove_confirm")
                if st.button(i18n.t("remove_button"), type="primary", disabled=not confirm):
                    ok, msg = db.delete_product(product_id_to_remove)
                    if ok:
                        st.success(msg)
                        st.session_state["_reset_remove_confirm"] = True
                        st.rerun()
                    else:
                        st.error(msg)

    with tab_list:
        with panel("prod_list"):
            products = db.get_products(user_id)
            if products.empty:
                empty_state("—", i18n.t("no_products_add_one"))
            else:
                st.markdown(f'<div class="panel-title">{i18n.t("all_products_title")}</div>',
                            unsafe_allow_html=True)

                all_cats_label = i18n.t("all_categories")
                fc1, fc2 = st.columns([2, 1])
                with fc1:
                    search = st.text_input(
                        i18n.t("search_products"), placeholder=i18n.t("search_placeholder"),
                        label_visibility="collapsed", key="prod_search",
                    )
                with fc2:
                    categories = [all_cats_label] + sorted(products["category"].dropna().unique().tolist())
                    cat_filter = st.selectbox(
                        i18n.t("category"), categories, label_visibility="collapsed", key="prod_cat_filter"
                    )

                filtered = products.copy()
                if search.strip():
                    filtered = filtered[filtered["name"].str.contains(search.strip(), case=False, na=False)]
                if cat_filter != all_cats_label:
                    filtered = filtered[filtered["category"] == cat_filter]

                if filtered.empty:
                    empty_state("—", i18n.t("no_search_match"))
                else:
                    st.markdown(
                        f'<div class="small-muted" style="margin:12px 0 4px 0;">'
                        f'{i18n.t("product_count", n=len(filtered))}</div>',
                        unsafe_allow_html=True,
                    )
                    # Text-only cards are much shorter than the old image
                    # tiles, so a wider grid keeps the page from looking
                    # sparse and stretched.
                    cols_per_row = 4
                    rows = [filtered.iloc[i:i + cols_per_row] for i in range(0, len(filtered), cols_per_row)]
                    for row_df in rows:
                        cols = st.columns(cols_per_row)
                        for col, (_, prod) in zip(cols, row_df.iterrows()):
                            with col:
                                st.markdown(
                                    styling.product_card_html(
                                        name=prod["name"],
                                        category=prod["category"],
                                        price=float(prod["price"]),
                                        stock_badge=styling.stock_badge(int(prod["stock"])),
                                    ),
                                    unsafe_allow_html=True,
                                )
                                with st.expander(i18n.t("edit")):
                                    new_stock = st.number_input(
                                        i18n.t("stock"), min_value=0, step=1,
                                        value=int(prod["stock"]), key=f"stock_{prod['id']}",
                                    )
                                    # Cost price editing — previously there was no way to
                                    # correct a product's cost_price after creation (e.g.
                                    # bulk-uploaded products whose sheet had no cost_price
                                    # column, which import as cost_price=0). db.py already
                                    # had update_cost_price(); it just wasn't wired into any
                                    # UI. Without a real cost price, profit always equals
                                    # sales exactly (profit = total_price - 0), so this field
                                    # is what actually lets profit/loss reporting mean anything.
                                    new_cost_price = st.number_input(
                                        i18n.t("cost_price_rs"), min_value=0.0, step=1.0, format="%.2f",
                                        value=float(prod["cost_price"]), key=f"cost_{prod['id']}",
                                    )
                                    if st.button(i18n.t("save"), key=f"save_{prod['id']}", type="primary",
                                                 use_container_width=True):
                                        if new_stock != int(prod["stock"]):
                                            db.update_stock(prod["id"], new_stock)
                                        if new_cost_price != float(prod["cost_price"]):
                                            db.update_cost_price(prod["id"], new_cost_price)
                                        st.success(i18n.t("product_updated", name=prod['name']))
                                        st.rerun()


# ---------------------------------------------------------------------------
# Sales page
# ---------------------------------------------------------------------------
def page_sales(user_id):
    styling.brand_header(i18n.t("page_sales"))

    products = db.get_products(user_id)

    c1, c2 = st.columns([1.1, 1])
    with c1:
        with panel("sales_record"):
            st.markdown(f'<div class="panel-title">🛒 {i18n.t("record_a_sale")}</div>', unsafe_allow_html=True)
            if products.empty:
                empty_state("—", i18n.t("add_products_first"))
            else:
                in_stock = products[products["stock"] > 0]
                if in_stock.empty:
                    st.warning(i18n.t("all_out_of_stock"))
                else:
                    options = {
                        f"{row['name']} — ₹{float(row['price']):.2f} ({row['stock']} left)": row["id"]
                        for _, row in in_stock.iterrows()
                    }
                    choice = st.selectbox(i18n.t("product"), list(options.keys()))
                    product_id = options[choice]
                    product_row = products[products["id"] == product_id].iloc[0]

                    st.markdown(
                        styling.product_mini_card_html(
                            name=product_row["name"],
                            category=product_row["category"],
                        ),
                        unsafe_allow_html=True,
                    )

                    max_qty = int(product_row["stock"])
                    qty = st.number_input(i18n.t("quantity"), min_value=1, max_value=max_qty, step=1)
                    total = float(product_row["price"]) * qty
                    st.markdown(
                        f'<div class="sale-total">₹{total:,.2f}</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button(i18n.t("record_sale"), type="primary"):
                        ok, msg = db.record_sale(user_id, product_id, qty, float(product_row["price"]))
                        st.success(msg) if ok else st.error(msg)
                        if ok:
                            st.rerun()

    with c2:
        with panel("sales_recent"):
            st.markdown(f'<div class="panel-title">🧾 {i18n.t("recent_sales")}</div>', unsafe_allow_html=True)
            sales = db.get_sales(user_id)
            if sales.empty:
                empty_state("—", i18n.t("no_sales_recorded"))
            else:
                display = sales[["product_name", "quantity", "total_price", "sold_at"]].head(15).rename(
                    columns={"product_name": i18n.t("col_product"), "quantity": i18n.t("col_qty"),
                              "total_price": i18n.t("col_total"), "sold_at": i18n.t("col_date")}
                )
                st.dataframe(display, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Reports page
# ---------------------------------------------------------------------------
def build_excel_report(products: pd.DataFrame, sales: pd.DataFrame) -> bytes:
    wb = Workbook()
    header_fill = PatternFill(start_color="6366F1", end_color="6366F1", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)

    def write_sheet(ws, df, title):
        ws.title = title
        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")
        for col in ws.columns:
            width = max(12, min(30, max(len(str(c.value)) for c in col) + 2))
            ws.column_dimensions[col[0].column_letter].width = width

    ws1 = wb.active
    # image_url is dropped too, in case an older deployment's table still
    # carries the column — the report should only show real product data.
    write_sheet(ws1, products.drop(columns=["user_id", "image_url"], errors="ignore"), "Products")
    ws2 = wb.create_sheet()
    write_sheet(ws2, sales.drop(columns=["id"], errors="ignore"), "Sales")

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def page_reports(user_id):
    styling.brand_header(i18n.t("page_reports"))

    products = db.get_products(user_id)
    sales = db.get_sales(user_id)

    with panel("reports_export"):
        st.write(i18n.t("reports_intro"))
        if products.empty and sales.empty:
            empty_state("—", i18n.t("nothing_to_export"))
        else:
            data = build_excel_report(products, sales)
            st.download_button(
                i18n.t("download_excel"),
                data=data,
                file_name=f"smartmart_report_{datetime.now(IST).strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
            )


# ---------------------------------------------------------------------------
# Profile page
# ---------------------------------------------------------------------------
def page_profile(user_id):
    styling.brand_header(i18n.t("page_profile"))

    profile = db.get_profile(user_id)

    with panel("profile_panel"):
        st.markdown(f'<div class="panel-title">👤 {i18n.t("my_profile")}</div>', unsafe_allow_html=True)

        pc1, pc2 = st.columns([1, 2.2])
        with pc1:
            if profile and profile.get("profile_photo"):
                st.image(profile["profile_photo"], width=160)
            else:
                st.markdown(
                    '<div class="empty-state" style="padding:20px 6px;">'
                    '<div class="empty-icon">🏪</div>'
                    '<div class="empty-text">No photo yet</div></div>',
                    unsafe_allow_html=True,
                )
            photo = st.file_uploader(
                i18n.t("upload_profile_photo"), type=["png", "jpg", "jpeg"], key="profile_photo_uploader"
            )

        with pc2:
            st.markdown(f'<div class="panel-title" style="font-size:1.05rem; margin-bottom:14px;">'
                        f'{i18n.t("edit_profile_details")}</div>', unsafe_allow_html=True)
            with st.form("profile_form"):
                shop_name = st.text_input(i18n.t("shop_name"), value=(profile.get("shop_name") if profile else "") or "")
                owner_name = st.text_input(i18n.t("owner_name"), value=(profile.get("owner_name") if profile else "") or "")
                mobile_number = st.text_input(
                    i18n.t("mobile_number"), value=(profile.get("mobile_number") if profile else "") or ""
                )
                email = st.text_input(i18n.t("email"), value=(profile.get("email") if profile else "") or "")
                submitted = st.form_submit_button(i18n.t("save_changes"), type="primary", use_container_width=True)

            if submitted:
                photo_bytes = photo.read() if photo is not None else None
                ok, msg = db.update_profile(
                    user_id, shop_name, owner_name, mobile_number, email, photo_bytes
                )
                if ok:
                    st.session_state.user["shop_name"] = shop_name.strip()
                    st.session_state.user["owner_name"] = owner_name.strip()
                    st.success(i18n.t("profile_updated"))
                    st.rerun()
                else:
                    st.error(msg)


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
def main():
    if not st.session_state.user:
        auth_screen()
        return

    with st.sidebar:
        # Fetch the shopkeeper's profile so we can show their photo (if any)
        # as a larger round avatar next to the shop name / owner name. This
        # is the same profile_photo bytes set on the Profile page.
        profile = db.get_profile(st.session_state.user["id"])
        avatar_html = ""
        if profile and profile.get("profile_photo"):
            photo_b64 = base64.b64encode(profile["profile_photo"]).decode()
            avatar_html = f'<img class="sidebar-avatar-lg" src="data:image/png;base64,{photo_b64}" />'
        else:
            avatar_html = '<div class="sidebar-avatar-lg sidebar-avatar-placeholder">🏪</div>'

        st.markdown(
            '<div class="sidebar-brand">'
            '<div class="sidebar-brand-mark">S</div>'
            '<div class="sidebar-brand-name">SmartMart</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        shop = st.session_state.user.get("shop_name") or ""
        owner = st.session_state.user.get("owner_name") or st.session_state.user["username"]
        if shop:
            st.markdown(
                '<div class="sidebar-profile-row">'
                f'{avatar_html}'
                '<div>'
                f'<div class="sidebar-shop">{shop}</div>'
                f'<div class="sidebar-owner">{owner}</div>'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="sidebar-profile-row">'
                f'{avatar_html}'
                '<div>'
                f'<div class="sidebar-owner">'
                f'{i18n.t("signed_in_as", name=st.session_state.user["username"])}</div>'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
        i18n.render_lang_toggle(key_suffix="sidebar")
        st.markdown('<div class="sidebar-spacer" style="margin-top:6px;"></div>', unsafe_allow_html=True)

        nav_map = {
            i18n.t('nav_dashboard'): "Dashboard",
            i18n.t('nav_products'): "Products",
            i18n.t('nav_sales'): "Sales",
            i18n.t('nav_reports'): "Reports",
            i18n.t('nav_profile'): "Profile",
        }
        nav_choice = st.radio(
            "Navigate",
            list(nav_map.keys()),
            label_visibility="collapsed",
        )
        page = nav_map[nav_choice]

        st.markdown('<div class="sidebar-spacer"></div>', unsafe_allow_html=True)
        if st.button(i18n.t("log_out"), use_container_width=True):
            st.session_state.user = None
            st.session_state.auth_view = "login"
            st.rerun()

    user_id = st.session_state.user["id"]
    if page == "Dashboard":
        page_dashboard(user_id)
    elif page == "Products":
        page_products(user_id)
    elif page == "Sales":
        page_sales(user_id)
    elif page == "Reports":
        page_reports(user_id)
    elif page == "Profile":
        page_profile(user_id)


if __name__ == "__main__":
    main()

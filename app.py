"""
app.py — Smart Supermarket Inventory & Sales Analytics System
Streamlit + TiDB Cloud (MySQL-compatible) + Pandas/Matplotlib + OpenPyXL
"""

import io
from datetime import datetime

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows

import db
import styling

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
if "barcode_lookup" not in st.session_state:
    st.session_state.barcode_lookup = None
if "auth_view" not in st.session_state:
    st.session_state.auth_view = "login"  # "login" | "signup" | "forgot"

PALETTE = {
    "ink": "#0B3B2E",
    "gold": "#C9973E",
    "muted": "#6B7368",
    "success": "#2E7D4F",
    "danger": "#B3432B",
}


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
        ax.spines[spine].set_color("#E7E1D3")
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
        """
        <div class="auth-hero">
            <div class="hero-orb hero-orb-1"></div>
            <div class="hero-orb hero-orb-2"></div>
            <div class="hero-topline">
                <span class="hero-topline-dot"></span>
                BUILT FOR SHOPS THAT MOVE FAST
            </div>
            <div class="hero-mark">🧾 SmartMart</div>
            <div class="hero-headline">Run your shop<br/>like clockwork.</div>
            <div class="hero-sub">
                One dashboard for stock, sales, and barcodes —
                built to feel as simple as writing it in a ledger.
            </div>
            <div class="hero-grid">
                <div class="hero-feature">
                    <div class="hero-feature-icon">📦</div>
                    <div class="hero-feature-title">Live stock</div>
                    <div class="hero-feature-desc">Know what's in and out, down to the unit.</div>
                </div>
                <div class="hero-feature">
                    <div class="hero-feature-icon">🔍</div>
                    <div class="hero-feature-title">Barcode ready</div>
                    <div class="hero-feature-desc">Scan to restock or add new items in seconds.</div>
                </div>
                <div class="hero-feature">
                    <div class="hero-feature-icon">📊</div>
                    <div class="hero-feature-title">Clear dashboards</div>
                    <div class="hero-feature-desc">See what's selling without digging for it.</div>
                </div>
                <div class="hero-feature">
                    <div class="hero-feature-icon">⬇</div>
                    <div class="hero-feature-title">Export anytime</div>
                    <div class="hero-feature-desc">A clean Excel report, whenever you need one.</div>
                </div>
            </div>
            <div class="hero-receipt">
                GROUP 47 · R.C. TECHNICAL INSTITUTE, AHMEDABAD
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def auth_screen():
    left, mid, right = st.columns([1, 0.08, 1])

    with left:
        st.write("")
        st.write("")
        _auth_hero()

    with right:
        with st.container(key="auth_wrap"):
            view = st.session_state.auth_view

            if view == "login":
                st.markdown("### Welcome back")
                st.markdown('<div class="auth-sub">Log in to your shop dashboard.</div>',
                            unsafe_allow_html=True)
                with st.form("login_form"):
                    u = st.text_input("Username")
                    p = st.text_input("Password", type="password")
                    submitted = st.form_submit_button("Log in", type="primary", use_container_width=True)
                if submitted:
                    if not u or not p:
                        st.warning("Enter both a username and password.")
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
                            st.error("Incorrect username or password.")

                c1, c2 = st.columns(2)
                with c1:
                    with st.container(key="link_forgot"):
                        if st.button("Forgot password?"):
                            st.session_state.auth_view = "forgot"
                            st.rerun()
                with c2:
                    with st.container(key="link_signup"):
                        if st.button("Create an account →"):
                            st.session_state.auth_view = "signup"
                            st.rerun()

            elif view == "signup":
                st.markdown("### Set up your shop")
                st.markdown('<div class="auth-sub">Takes less than a minute.</div>',
                            unsafe_allow_html=True)
                with st.form("signup_form"):
                    shop_name = st.text_input("Shop name")
                    owner_name = st.text_input("Shop owner name")
                    nu = st.text_input("Username")
                    np1 = st.text_input("Password", type="password")
                    np2 = st.text_input("Confirm password", type="password")
                    submitted2 = st.form_submit_button("Create account", type="primary", use_container_width=True)
                if submitted2:
                    if not all([shop_name.strip(), owner_name.strip(), nu.strip(), np1]):
                        st.warning("Fill in all fields.")
                    elif np1 != np2:
                        st.error("Passwords don't match.")
                    elif len(np1) < 4:
                        st.error("Password should be at least 4 characters.")
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
                            st.toast(f"Welcome, {shop_name.strip()}! Your shop is set up.", icon="🎉")
                            st.rerun()
                        else:
                            st.error(msg)

                with st.container(key="link_back_login"):
                    if st.button("← Back to log in"):
                        st.session_state.auth_view = "login"
                        st.rerun()

            elif view == "forgot":
                st.markdown("### Reset your password")
                st.markdown(
                    '<div class="auth-sub">Enter your username and choose a new password.</div>',
                    unsafe_allow_html=True,
                )
                with st.form("forgot_form"):
                    fu = st.text_input("Username")
                    fp1 = st.text_input("New password", type="password")
                    fp2 = st.text_input("Confirm new password", type="password")
                    submitted3 = st.form_submit_button("Update password", type="primary", use_container_width=True)
                if submitted3:
                    if not fu.strip() or not fp1:
                        st.warning("Fill in all fields.")
                    elif fp1 != fp2:
                        st.error("Passwords don't match.")
                    elif len(fp1) < 4:
                        st.error("Password should be at least 4 characters.")
                    elif not db.user_exists(fu.strip()):
                        st.error("No account found with that username.")
                    else:
                        ok, msg = db.reset_password(fu.strip(), fp1)
                        if ok:
                            st.success(msg)
                            st.session_state.auth_view = "login"
                        else:
                            st.error(msg)

                with st.container(key="link_back_login2"):
                    if st.button("← Back to log in"):
                        st.session_state.auth_view = "login"
                        st.rerun()


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

def page_dashboard(user_id):
    styling.brand_header("Dashboard")

    products = db.get_products(user_id)
    sales = db.get_sales(user_id)

    total_products = len(products)
    stock_value = float((products["price"] * products["stock"]).sum()) if not products.empty else 0.0
    low_stock_count = int((products["stock"] <= 5).sum()) if not products.empty else 0
    today = datetime.now().date()
    today_sales = 0.0
    if not sales.empty:
        sales["sold_at"] = pd.to_datetime(sales["sold_at"])
        today_sales = float(sales.loc[sales["sold_at"].dt.date == today, "total_price"].sum())

    with st.container(key="kpi_row"):
        cols = st.columns(4)
        kpis = [
            ("Products tracked", f"{total_products}", "across all categories", "📦"),
            ("Stock value", f"₹{stock_value:,.0f}", "at current price × qty", "💰"),
            ("Sales today", f"₹{today_sales:,.0f}", today.strftime("%d %b %Y"), "🧾"),
            ("Low stock alerts", f"{low_stock_count}", "5 units or fewer", "⚠️"),
        ]
        for c, (label, value, sub, icon) in zip(cols, kpis):
            with c:
                st.markdown(styling.kpi_card_html(label, value, sub, icon), unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        with panel("dash_top_sellers"):
            st.markdown('<div class="panel-title">Top-selling products</div>', unsafe_allow_html=True)
            if sales.empty:
                empty_state("📉", "No sales recorded yet.")
            else:
                top = sales.groupby("product_name")["quantity"].sum().sort_values(ascending=False).head(6)
                fig, ax = plt.subplots(figsize=(5, 3.2))
                ax.barh(top.index[::-1], top.values[::-1], color=PALETTE["ink"], height=0.55)
                ax.set_xlabel("Units sold")
                chart_style(fig, ax)
                st.pyplot(fig, use_container_width=True)

    with c2:
        with panel("dash_stock_category"):
            st.markdown('<div class="panel-title">Stock by category</div>', unsafe_allow_html=True)
            if products.empty:
                empty_state("📦", "No products yet.")
            else:
                by_cat = products.groupby("category")["stock"].sum()
                fig, ax = plt.subplots(figsize=(5, 3.2))
                colors = ["#0B3B2E", "#C9973E", "#6B7368", "#2E7D4F", "#B3432B", "#14543F"]
                ax.pie(
                    by_cat.values, labels=by_cat.index, autopct="%1.0f%%",
                    colors=colors[: len(by_cat)], textprops={"color": "#1F2A24", "fontsize": 9},
                    wedgeprops={"edgecolor": "#FFFFFF", "linewidth": 2},
                )
                fig.patch.set_facecolor("#FFFFFF")
                st.pyplot(fig, use_container_width=True)

    with panel("dash_low_stock"):
        st.markdown('<div class="panel-title">Low stock — restock soon</div>', unsafe_allow_html=True)
        if products.empty or low_stock_count == 0:
            empty_state("✅", "Everything is well stocked.")
        else:
            low = products[products["stock"] <= 5][["name", "category", "stock", "barcode"]]
            st.dataframe(low, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Products page (manual / bulk upload / barcode)
# ---------------------------------------------------------------------------

def page_products(user_id):
    styling.brand_header("Products")

    tab_manual, tab_bulk, tab_barcode, tab_list = st.tabs(
        ["➕ Add manually", "📄 Bulk upload", "🔍 Scan barcode", "📋 All products"]
    )

    with tab_manual:
        with panel("prod_manual"):
            with st.form("add_product_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    name = st.text_input("Product name")
                    category = st.text_input("Category", value="General")
                with c2:
                    price = st.number_input("Price (₹)", min_value=0.0, step=1.0, format="%.2f")
                    stock = st.number_input("Opening stock", min_value=0, step=1)
                barcode = st.text_input("Barcode (optional)")
                submitted = st.form_submit_button("Add product", type="primary")
            if submitted:
                if not name.strip():
                    st.warning("Product name is required.")
                else:
                    ok, msg = db.add_product(user_id, name, category, price, stock, barcode or None)
                    st.success(msg) if ok else st.error(msg)

    with tab_bulk:
        with panel("prod_bulk"):
            st.write("Upload a CSV or Excel file with columns: **name, category, price, stock, barcode** "
                      "(barcode is optional; column names are matched case-insensitively).")
            file = st.file_uploader("Choose file", type=["csv", "xlsx", "xls"])
            if file is not None:
                try:
                    df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
                    st.dataframe(df.head(10), use_container_width=True, hide_index=True)
                    if st.button("Import these products", type="primary"):
                        success, skipped, errors = db.bulk_upsert_products(user_id, df)
                        st.success(f"Imported {success} product(s). Skipped {skipped}.")
                        if errors:
                            with st.expander("See skipped rows"):
                                for e in errors:
                                    st.write("• " + e)
                except Exception as e:
                    st.error(f"Couldn't read that file: {e}")

    with tab_barcode:
        with panel("prod_barcode"):
            st.write(
                "Plug in a USB barcode scanner — it types the code and presses Enter automatically. "
                "Click into the box below and scan an item."
            )
            st.markdown('<div class="barcode-scan-box"></div>', unsafe_allow_html=True)

            with st.form("barcode_form", clear_on_submit=True):
                scanned = st.text_input("Scan or type barcode", placeholder="e.g. 8901030826829")
                look_up = st.form_submit_button("Look up", type="primary")

            if look_up and scanned.strip():
                existing = db.get_product_by_barcode(user_id, scanned.strip())
                st.session_state.barcode_lookup = {"code": scanned.strip(), "product": existing}

            lookup = st.session_state.barcode_lookup
            if lookup:
                code = lookup["code"]
                product = lookup["product"]
                if product:
                    st.info(f"Match found: **{product['name']}** ({product['category']}) — "
                            f"current stock {product['stock']}, ₹{float(product['price']):.2f}")
                    with st.form("restock_form"):
                        add_qty = st.number_input("Add to stock", min_value=1, step=1, value=10)
                        do_restock = st.form_submit_button("Restock", type="primary")
                    if do_restock:
                        db.restock_product(product["id"], add_qty)
                        st.success(f"Stock updated — {product['name']} now has "
                                   f"{product['stock'] + add_qty} units.")
                        st.session_state.barcode_lookup = None
                        st.rerun()
                else:
                    st.warning(f"No product found for barcode **{code}**. Add it as a new product:")
                    with st.form("new_from_barcode_form", clear_on_submit=True):
                        c1, c2 = st.columns(2)
                        with c1:
                            n_name = st.text_input("Product name")
                            n_category = st.text_input("Category", value="General")
                        with c2:
                            n_price = st.number_input("Price (₹)", min_value=0.0, step=1.0, format="%.2f")
                            n_stock = st.number_input("Opening stock", min_value=0, step=1, value=10)
                        create = st.form_submit_button("Create product", type="primary")
                    if create:
                        if not n_name.strip():
                            st.warning("Product name is required.")
                        else:
                            ok, msg = db.add_product(user_id, n_name, n_category, n_price, n_stock, code)
                            if ok:
                                st.success(msg)
                                st.session_state.barcode_lookup = None
                                st.rerun()
                            else:
                                st.error(msg)

    with tab_list:
        with panel("prod_list"):
            products = db.get_products(user_id)
            if products.empty:
                empty_state("📋", "No products yet — add one from the tabs above.")
            else:
                show = products.copy()
                show["status"] = show["stock"].apply(
                    lambda s: "Out of stock" if s <= 0 else ("Low" if s <= 5 else "In stock")
                )
                st.dataframe(
                    show[["name", "category", "price", "stock", "status", "barcode"]],
                    use_container_width=True, hide_index=True,
                )


# ---------------------------------------------------------------------------
# Sales page
# ---------------------------------------------------------------------------

def page_sales(user_id):
    styling.brand_header("Sales")

    products = db.get_products(user_id)
    c1, c2 = st.columns([1.1, 1])

    with c1:
        with panel("sales_record"):
            st.markdown('<div class="panel-title">Record a sale</div>', unsafe_allow_html=True)
            if products.empty:
                empty_state("📦", "Add products first.")
            else:
                in_stock = products[products["stock"] > 0]
                if in_stock.empty:
                    st.warning("Every product is out of stock — restock before recording sales.")
                else:
                    options = {
                        f"{row['name']} — ₹{float(row['price']):.2f} ({row['stock']} left)": row["id"]
                        for _, row in in_stock.iterrows()
                    }
                    choice = st.selectbox("Product", list(options.keys()))
                    product_id = options[choice]
                    product_row = products[products["id"] == product_id].iloc[0]
                    max_qty = int(product_row["stock"])
                    qty = st.number_input("Quantity", min_value=1, max_value=max_qty, step=1)
                    total = float(product_row["price"]) * qty
                    st.markdown(
                        f'<div class="sale-total">₹{total:,.2f}</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button("Record sale", type="primary"):
                        ok, msg = db.record_sale(user_id, product_id, qty, float(product_row["price"]))
                        st.success(msg) if ok else st.error(msg)
                        if ok:
                            st.rerun()

    with c2:
        with panel("sales_recent"):
            st.markdown('<div class="panel-title">Recent sales</div>', unsafe_allow_html=True)
            sales = db.get_sales(user_id)
            if sales.empty:
                empty_state("🧾", "No sales recorded yet.")
            else:
                st.dataframe(
                    sales[["product_name", "quantity", "total_price", "sold_at"]].head(15),
                    use_container_width=True, hide_index=True,
                )


# ---------------------------------------------------------------------------
# Reports page
# ---------------------------------------------------------------------------

def build_excel_report(products: pd.DataFrame, sales: pd.DataFrame) -> bytes:
    wb = Workbook()
    header_fill = PatternFill(start_color="0B3B2E", end_color="0B3B2E", fill_type="solid")
    header_font = Font(color="FAF7F0", bold=True)

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
    write_sheet(ws1, products.drop(columns=["user_id"], errors="ignore"), "Products")
    ws2 = wb.create_sheet()
    write_sheet(ws2, sales.drop(columns=["id"], errors="ignore"), "Sales")

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def page_reports(user_id):
    styling.brand_header("Reports")
    products = db.get_products(user_id)
    sales = db.get_sales(user_id)

    with panel("reports_export"):
        st.write("Download a full Excel workbook with your current product catalogue and sales history "
                  "— one sheet each, styled and ready to share.")
        if products.empty and sales.empty:
            empty_state("📊", "Nothing to export yet.")
        else:
            data = build_excel_report(products, sales)
            st.download_button(
                "⬇ Download Excel report",
                data=data,
                file_name=f"smartmart_report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
            )


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

def main():
    if not st.session_state.user:
        auth_screen()
        return

    with st.sidebar:
        st.markdown(
            '<div class="sidebar-brand">'
            '<div class="sidebar-brand-mark">🧾</div>'
            '<div class="sidebar-brand-name">SmartMart</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        shop = st.session_state.user.get("shop_name") or ""
        owner = st.session_state.user.get("owner_name") or st.session_state.user["username"]
        if shop:
            st.markdown(f'<div class="sidebar-shop">{shop}</div>'
                        f'<div class="sidebar-owner">{owner}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="sidebar-owner">Signed in as '
                        f'{st.session_state.user["username"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
        st.markdown('<a href="https://websiteforlook-sketch.github.io/-smartmart-landing/"target="_blank" style="color:#E7C077;font-size:0.85rem;text-decoration:none;">🌐 View landing page</a>', unsafe_allow_html=True) )

        nav_map = {
            "🧭  Dashboard": "Dashboard",
            "📦  Products": "Products",
            "🧾  Sales": "Sales",
            "📊  Reports": "Reports",
        }
        nav_choice = st.radio(
            "Navigate",
            list(nav_map.keys()),
            label_visibility="collapsed",
        )
        page = nav_map[nav_choice]

        st.markdown('<div class="sidebar-spacer"></div>', unsafe_allow_html=True)
        if st.button("↩ Log out", use_container_width=True):
            st.session_state.user = None
            st.session_state.barcode_lookup = None
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


if __name__ == "__main__":
    main()

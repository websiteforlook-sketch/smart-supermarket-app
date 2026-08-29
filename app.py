import streamlit as st
import pandas as pd
from datetime import datetime

import db
from styling import load_css, stat_card, product_card_html, page_header

st.set_page_config(
    page_title="ShopAdmin",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.init_db()
load_css()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "editing_product_id" not in st.session_state:
    st.session_state.editing_product_id = None


# ==================================================
# LOGIN PAGE
# ==================================================
def render_login():
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="login-brand-mark">S</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-title">ShopAdmin</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Sign in to manage your store</div>', unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username", placeholder="admin")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Sign in", use_container_width=True)

        if submitted:
            if db.verify_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password.")

    st.caption("Default login — username: `admin` · password: `admin123`")
    st.markdown('</div>', unsafe_allow_html=True)


# ==================================================
# SIDEBAR
# ==================================================
def render_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand-mark">S</div>
                <div class="sidebar-brand-name">ShopAdmin</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="sidebar-user">Signed in as <b>{st.session_state.username}</b></div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-nav-label">Menu</div>', unsafe_allow_html=True)

        nav_items = [
            ("Dashboard", "📊"),
            ("Products", "🏷️"),
            ("Sales", "🧾"),
            ("Reports", "📈"),
        ]
        for label, icon in nav_items:
            active = st.session_state.page == label
            wrapper_class = "nav-active" if active else ""
            st.markdown(f'<div class="{wrapper_class}">', unsafe_allow_html=True)
            if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
                st.session_state.page = label
                st.session_state.editing_product_id = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("↩ Log out", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()


# ==================================================
# DASHBOARD PAGE
# ==================================================
def render_dashboard():
    st.markdown(page_header("Dashboard", "Overview of your store performance"), unsafe_allow_html=True)

    stats = db.get_dashboard_stats()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(stat_card("Products", stats["total_products"], "items tracked", "📦", "navy"), unsafe_allow_html=True)
    with c2:
        st.markdown(stat_card("Units in stock", stats["total_stock"], "across all products", "🧮", "amber"), unsafe_allow_html=True)
    with c3:
        st.markdown(stat_card("Revenue", f"₹{stats['total_revenue']:,.0f}", f"{stats['total_sales']} orders total", "💰", "green"), unsafe_allow_html=True)
    with c4:
        low_count = len(stats["low_stock"])
        st.markdown(stat_card("Low stock alerts", low_count, "5 units or fewer", "⚠️", "red" if low_count else "navy"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="content-card-title">Revenue — last 14 days</div>', unsafe_allow_html=True)
        daily = db.get_sales_by_day(14)
        if daily:
            df = pd.DataFrame(daily)
            df["day"] = pd.to_datetime(df["day"])
            st.bar_chart(df.set_index("day")["revenue"], color="#f5a623", height=280)
        else:
            st.caption("No sales recorded yet. Once you make sales, revenue trends will appear here.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="content-card-title">Top products</div>', unsafe_allow_html=True)
        top = db.get_top_products(5)
        if top:
            df = pd.DataFrame(top).set_index("product_name")
            st.bar_chart(df["units_sold"], color="#0a1a2f", height=280)
        else:
            st.caption("No sales yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    if stats["low_stock"]:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="content-card-title">⚠️ Low stock — needs restocking</div>', unsafe_allow_html=True)
        df = pd.DataFrame(stats["low_stock"])[["name", "category", "stock", "price"]]
        df.columns = ["Product", "Category", "Stock left", "Price (₹)"]
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ==================================================
# PRODUCTS PAGE
# ==================================================
def render_products():
    st.markdown(page_header("Products", "Manage your product catalog"), unsafe_allow_html=True)

    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        search = st.text_input("Search products", placeholder="Search by name or category…", label_visibility="collapsed")
    with top_col2:
        add_clicked = st.button("＋ Add product", use_container_width=True)

    if add_clicked:
        st.session_state.editing_product_id = "new"

    if st.session_state.editing_product_id is not None:
        render_product_form()
        st.markdown("---")

    products = db.get_products(search)

    if not products:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.caption("No products yet. Click **＋ Add product** to create your first one.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    cols_per_row = 4
    for i in range(0, len(products), cols_per_row):
        row_products = products[i:i + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, product in zip(cols, row_products):
            with col:
                st.markdown(product_card_html(product), unsafe_allow_html=True)
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("Edit", key=f"edit_{product['id']}", use_container_width=True):
                        st.session_state.editing_product_id = product["id"]
                        st.rerun()
                with b2:
                    if st.button("Delete", key=f"delete_{product['id']}", use_container_width=True):
                        db.delete_product(product["id"])
                        st.rerun()


def render_product_form():
    editing_id = st.session_state.editing_product_id
    is_new = editing_id == "new"
    existing = None if is_new else db.get_product(editing_id)

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="content-card-title">{"Add new product" if is_new else "Edit product"}</div>',
        unsafe_allow_html=True,
    )

    with st.form("product_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Product name", value=existing["name"] if existing else "")
            category = st.text_input("Category", value=existing["category"] if existing else "")
            barcode = st.text_input("Barcode (optional)", value=existing["barcode"] if existing and existing["barcode"] else "")
        with c2:
            price = st.number_input("Price (₹)", min_value=0.0, step=1.0, value=float(existing["price"]) if existing else 0.0)
            stock = st.number_input("Stock quantity", min_value=0, step=1, value=int(existing["stock"]) if existing else 0)
            image_url = st.text_input("Image URL (optional)", value=existing["image_url"] if existing and existing["image_url"] else "",
                                       placeholder="https://example.com/product.jpg")

        fc1, fc2 = st.columns(2)
        with fc1:
            save = st.form_submit_button("Save product", use_container_width=True)
        with fc2:
            cancel = st.form_submit_button("Cancel", use_container_width=True)

        if save:
            if not name.strip():
                st.error("Product name is required.")
            else:
                if is_new:
                    db.add_product(name, category, price, stock, barcode, image_url)
                else:
                    db.update_product(editing_id, name, category, price, stock, barcode, image_url)
                st.session_state.editing_product_id = None
                st.rerun()

        if cancel:
            st.session_state.editing_product_id = None
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ==================================================
# SALES PAGE
# ==================================================
def render_sales():
    st.markdown(page_header("Sales", "Record new sales and view sales history"), unsafe_allow_html=True)

    products = db.get_products()

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<div class="content-card-title">Record a sale</div>', unsafe_allow_html=True)

    if not products:
        st.caption("Add a product first before recording sales.")
    else:
        with st.form("sale_form"):
            options = {f"{p['name']} — ₹{p['price']:,.2f} ({p['stock']} in stock)": p["id"] for p in products}
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                choice = st.selectbox("Product", list(options.keys()))
            with c2:
                qty = st.number_input("Quantity", min_value=1, step=1, value=1)
            with c3:
                st.write("")
                st.write("")
                submit = st.form_submit_button("Record sale", use_container_width=True)

            if submit:
                product_id = options[choice]
                success, message = db.record_sale(product_id, qty)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<div class="content-card-title">Recent sales</div>', unsafe_allow_html=True)

    sales = db.get_sales(limit=100)
    if sales:
        df = pd.DataFrame(sales)
        df["sold_at"] = pd.to_datetime(df["sold_at"]).dt.strftime("%d %b %Y, %I:%M %p")
        df = df[["sold_at", "product_name", "quantity", "unit_price", "total"]]
        df.columns = ["Date", "Product", "Qty", "Unit price (₹)", "Total (₹)"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.caption("No sales recorded yet.")
    st.markdown('</div>', unsafe_allow_html=True)


# ==================================================
# REPORTS PAGE
# ==================================================
def render_reports():
    st.markdown(page_header("Reports", "Deeper insights into your store performance"), unsafe_allow_html=True)

    stats = db.get_dashboard_stats()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(stat_card("Total revenue", f"₹{stats['total_revenue']:,.0f}", "all-time", "💰", "green"), unsafe_allow_html=True)
    with c2:
        st.markdown(stat_card("Total orders", stats["total_sales"], "all-time", "🧾", "navy"), unsafe_allow_html=True)
    with c3:
        avg = stats["total_revenue"] / stats["total_sales"] if stats["total_sales"] else 0
        st.markdown(stat_card("Avg. order value", f"₹{avg:,.0f}", "per transaction", "📐", "amber"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="content-card-title">Revenue trend (30 days)</div>', unsafe_allow_html=True)
        daily = db.get_sales_by_day(30)
        if daily:
            df = pd.DataFrame(daily)
            df["day"] = pd.to_datetime(df["day"])
            st.line_chart(df.set_index("day")["revenue"], color="#f5a623", height=300)
        else:
            st.caption("No sales data yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="content-card-title">Top products by revenue</div>', unsafe_allow_html=True)
        top = db.get_top_products(8)
        if top:
            df = pd.DataFrame(top).set_index("product_name")
            st.bar_chart(df["revenue"], color="#0a1a2f", height=300)
        else:
            st.caption("No sales data yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<div class="content-card-title">All-time product performance</div>', unsafe_allow_html=True)
    top_all = db.get_top_products(50)
    if top_all:
        df = pd.DataFrame(top_all)
        df.columns = ["Product", "Units sold", "Revenue (₹)"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.caption("No sales data yet.")
    st.markdown('</div>', unsafe_allow_html=True)


# ==================================================
# ROUTER
# ==================================================
if not st.session_state.logged_in:
    render_login()
else:
    render_sidebar()
    page = st.session_state.page
    if page == "Dashboard":
        render_dashboard()
    elif page == "Products":
        render_products()
    elif page == "Sales":
        render_sales()
    elif page == "Reports":
        render_reports()

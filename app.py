"""
app.py — Smart Supermarket Inventory & Sales Analytics System
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO

import db
from styling import inject_custom_css, kpi_card

st.set_page_config(page_title="SmartMart", page_icon="🛒", layout="wide")
inject_custom_css()

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.shop_name = None


# =====================================================================
# LOGIN / SIGNUP (shown when not logged in)
# =====================================================================
def show_auth():
    col_l, col_c, col_r = st.columns([1, 1.3, 1])
    with col_c:
        st.markdown("<div style='text-align:center; font-size:44px; margin-top:40px;'>🛒</div>", unsafe_allow_html=True)
        st.markdown("<div class='auth-title'>SmartMart</div>", unsafe_allow_html=True)
        st.markdown("<div class='auth-sub'>Smart Supermarket Inventory & Sales Analytics</div>", unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Log In", use_container_width=True)

                if submitted:
                    user = db.get_user_by_email(email)
                    if user and check_password_hash(user["password_hash"], password):
                        st.session_state.logged_in = True
                        st.session_state.user_id = user["user_id"]
                        st.session_state.shop_name = user["shop_name"]
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")

        with tab_signup:
            with st.form("signup_form"):
                shop_name = st.text_input("Shop Name")
                email = st.text_input("Email", key="signup_email")
                password = st.text_input("Password", type="password", key="signup_password")
                submitted = st.form_submit_button("Create Account", use_container_width=True)

                if submitted:
                    if not shop_name or not email or not password:
                        st.error("Please fill in all fields.")
                    else:
                        password_hash = generate_password_hash(password)
                        success, message = db.create_user(shop_name, email, password_hash)
                        if success:
                            st.success(message + " Please log in from the 'Log In' tab.")
                        else:
                            st.error(message)


# =====================================================================
# DASHBOARD
# =====================================================================
def show_dashboard():
    st.header("📊 Dashboard")
    total_revenue, total_sales, sales_df = db.get_sales_summary(st.session_state.user_id)
    products_df = db.get_products(st.session_state.user_id)
    low_stock_df = db.get_low_stock_products(st.session_state.user_id)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card("Total Revenue", f"₹{total_revenue:,.2f}", accent="#2F6B4F")
    with col2:
        kpi_card("Total Units Sold", int(total_sales), accent="#C08829")
    with col3:
        kpi_card("Products in Stock", len(products_df), accent="#14322A")
    with col4:
        alert_color = "#A8452B" if len(low_stock_df) > 0 else "#2F6B4F"
        kpi_card("Low Stock Alerts", len(low_stock_df), accent=alert_color)

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Top Selling Products")
        if not sales_df.empty:
            top_products = sales_df.groupby("product_name")["quantity_sold"].sum().sort_values(ascending=False).head(8)
            fig, ax = plt.subplots(facecolor="none")
            ax.set_facecolor("none")
            ax.bar(top_products.index, top_products.values, color="#2F6B4F", edgecolor="none")
            ax.set_ylabel("Units Sold", fontsize=10, color="#20251F")
            ax.spines[["top", "right"]].set_visible(False)
            ax.tick_params(colors="#20251F")
            plt.xticks(rotation=40, ha="right", fontsize=9)
            st.pyplot(fig, transparent=True)
        else:
            st.info("No sales recorded yet.")

    with c2:
        st.subheader("Sales by Category")
        if not sales_df.empty:
            cat_sales = sales_df.groupby("category")["total_amount"].sum()
            fig2, ax2 = plt.subplots(facecolor="none")
            ax2.pie(cat_sales.values, labels=cat_sales.index, autopct="%1.1f%%",
                    colors=["#14322A", "#2F6B4F", "#C08829", "#7FA08D", "#DCC48A"],
                    textprops={"fontsize": 9, "color": "#20251F"},
                    wedgeprops={"edgecolor": "white", "linewidth": 1.5})
            st.pyplot(fig2, transparent=True)
        else:
            st.info("No sales recorded yet.")

    if not low_stock_df.empty:
        st.divider()
        st.subheader("⚠️ Low Stock Alerts")
        st.dataframe(low_stock_df[["name", "category", "stock_quantity", "reorder_level"]], use_container_width=True)


# =====================================================================
# PRODUCT MANAGEMENT
# =====================================================================
def show_products():
    st.header("📦 Product Management")

    tab_add, tab_upload, tab_view = st.tabs(["Add Product", "Bulk Upload (CSV/Excel)", "View Inventory"])

    with tab_add:
        with st.form("add_product_form"):
            name = st.text_input("Product Name")
            category = st.text_input("Category")
            price = st.number_input("Price (₹)", min_value=0.0, step=1.0)
            stock = st.number_input("Stock Quantity", min_value=0, step=1)
            reorder = st.number_input("Reorder Level", min_value=0, step=1, value=10)
            supplier = st.text_input("Supplier")
            submitted = st.form_submit_button("Add Product")

            if submitted:
                if not name:
                    st.error("Product name is required.")
                else:
                    db.add_product(st.session_state.user_id, name, category, price, stock, reorder, supplier)
                    st.success(f"'{name}' added to inventory!")
                    st.rerun()

    with tab_upload:
        st.write("Upload a CSV or Excel file with columns: **name, category, price, stock_quantity, reorder_level, supplier**")
        uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

        if uploaded_file is not None:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.write("Preview:")
            st.dataframe(df.head(), use_container_width=True)

            if st.button("Import These Products"):
                db.bulk_add_products(st.session_state.user_id, df)
                st.success(f"Imported {len(df)} products successfully!")
                st.rerun()

    with tab_view:
        products_df = db.get_products(st.session_state.user_id)
        if products_df.empty:
            st.info("No products added yet.")
        else:
            st.dataframe(products_df, use_container_width=True)


# =====================================================================
# SALES MANAGEMENT
# =====================================================================
def show_sales():
    st.header("💳 Sales Management")

    products_df = db.get_products(st.session_state.user_id)

    if products_df.empty:
        st.warning("Add some products first before recording a sale.")
        return

    with st.form("add_sale_form"):
        product_name = st.selectbox("Product", products_df["name"])
        product_row = products_df[products_df["name"] == product_name].iloc[0]
        st.write(f"Available Stock: **{product_row['stock_quantity']}** | Price: **₹{product_row['price']}**")

        qty = st.number_input("Quantity Sold", min_value=1, step=1, max_value=int(product_row["stock_quantity"]) if product_row["stock_quantity"] > 0 else 1)
        submitted = st.form_submit_button("Record Sale")

        if submitted:
            total_amount = float(product_row["price"]) * qty
            db.add_sale(st.session_state.user_id, int(product_row["product_id"]), qty, total_amount)
            st.success(f"Sale recorded: {qty} × {product_name} = ₹{total_amount:.2f}")
            st.rerun()

    st.divider()
    st.subheader("Sales History")
    sales_df = db.get_sales(st.session_state.user_id)
    if sales_df.empty:
        st.info("No sales recorded yet.")
    else:
        st.dataframe(sales_df, use_container_width=True)


# =====================================================================
# REPORTS
# =====================================================================
def show_reports():
    st.header("📁 Reports")

    products_df = db.get_products(st.session_state.user_id)
    sales_df = db.get_sales(st.session_state.user_id)

    st.write("Download your current inventory and sales data as an Excel report.")

    if st.button("Generate Excel Report"):
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            products_df.to_excel(writer, sheet_name="Products", index=False)
            sales_df.to_excel(writer, sheet_name="Sales", index=False)
        buffer.seek(0)

        st.download_button(
            label="⬇️ Download Report (Excel)",
            data=buffer,
            file_name=f"{st.session_state.shop_name}_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# =====================================================================
# MAIN APP LAYOUT
# =====================================================================
def main_app():
    with st.sidebar:
        st.markdown(f"### 🛒 SmartMart")
        st.caption(f"**{st.session_state.shop_name}**")
        st.divider()
        page = st.radio("Navigate", ["Dashboard", "Products", "Sales", "Reports"], label_visibility="collapsed")
        st.divider()
        if st.button("Log Out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.shop_name = None
            st.rerun()

    if page == "Dashboard":
        show_dashboard()
    elif page == "Products":
        show_products()
    elif page == "Sales":
        show_sales()
    elif page == "Reports":
        show_reports()


# =====================================================================
# ENTRY POINT
# =====================================================================
if st.session_state.logged_in:
    main_app()
else:
    show_auth()

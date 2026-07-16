"""
Smart Supermarket Inventory & Sales Analytics System
-----------------------------------------------------
Run with:  streamlit run app.py
"""

import os
import hashlib
from datetime import date

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# --------------------------------------------------------------------------
# CONFIG & DATA FILES
# --------------------------------------------------------------------------
st.set_page_config(page_title="Smart Supermarket System", page_icon="🛒", layout="wide")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = os.path.join(DATA_DIR, "users.csv")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.csv")
SALES_FILE = os.path.join(DATA_DIR, "sales.csv")

USERS_COLS = ["shop_name", "owner_name", "email", "phone", "username", "password"]
PRODUCTS_COLS = ["username", "product_name", "category", "quantity",
                  "buying_price", "selling_price", "supplier", "date"]
SALES_COLS = ["username", "product_name", "quantity_sold", "total_amount", "profit", "date"]


def _ensure_csv(path, cols):
    if not os.path.exists(path):
        pd.DataFrame(columns=cols).to_csv(path, index=False)


_ensure_csv(USERS_FILE, USERS_COLS)
_ensure_csv(PRODUCTS_FILE, PRODUCTS_COLS)
_ensure_csv(SALES_FILE, SALES_COLS)


def load_csv(path, cols):
    df = pd.read_csv(path)
    for c in cols:
        if c not in df.columns:
            df[c] = None
    return df[cols]


def save_csv(df, path):
    df.to_csv(path, index=False)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# --------------------------------------------------------------------------
# SESSION STATE
# --------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "page" not in st.session_state:
    st.session_state.page = "home"


def go_to(page):
    st.session_state.page = page


def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.page = "home"


# --------------------------------------------------------------------------
# HOME / REGISTER / LOGIN
# --------------------------------------------------------------------------
def home_page():
    st.title("🛒 Smart Supermarket Inventory & Sales Analytics System")
    st.write("Manage your supermarket's inventory, sales, and business analytics — all in one place.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Create Account", use_container_width=True):
            go_to("register")
    with col2:
        if st.button("Login", use_container_width=True):
            go_to("login")


def register_page():
    st.title("Create Account")
    with st.form("register_form"):
        shop_name = st.text_input("Shop Name")
        owner_name = st.text_input("Owner Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Register")

    if submitted:
        if not all([shop_name, owner_name, email, phone, username, password]):
            st.error("Please fill in all fields.")
            return

        users = load_csv(USERS_FILE, USERS_COLS)
        if username in users["username"].values:
            st.error("Username already exists. Please choose another.")
            return

        new_user = pd.DataFrame([{
            "shop_name": shop_name, "owner_name": owner_name, "email": email,
            "phone": phone, "username": username, "password": hash_password(password),
        }])
        users = pd.concat([users, new_user], ignore_index=True)
        save_csv(users, USERS_FILE)

        st.success("Account created successfully! Taking you to your dashboard...")
        st.session_state.logged_in = True
        st.session_state.username = username
        go_to("dashboard")
        st.rerun()

    if st.button("⬅ Back to Home"):
        go_to("home")


def login_page():
    st.title("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        users = load_csv(USERS_FILE, USERS_COLS)
        match = users[(users["username"] == username) &
                      (users["password"] == hash_password(password))]
        if not match.empty:
            st.session_state.logged_in = True
            st.session_state.username = username
            go_to("dashboard")
            st.rerun()
        else:
            st.error("Invalid username or password.")

    if st.button("⬅ Back to Home"):
        go_to("home")


# --------------------------------------------------------------------------
# DASHBOARD
# --------------------------------------------------------------------------
def dashboard_page():
    username = st.session_state.username
    st.title(f"📊 Dashboard — {username}")

    products = load_csv(PRODUCTS_FILE, PRODUCTS_COLS)
    sales = load_csv(SALES_FILE, SALES_COLS)
    my_products = products[products["username"] == username]
    my_sales = sales[sales["username"] == username]

    total_products = len(my_products)
    total_sales = pd.to_numeric(my_sales["total_amount"], errors="coerce").sum()
    total_profit = pd.to_numeric(my_sales["profit"], errors="coerce").sum()
    low_stock = my_products[pd.to_numeric(my_products["quantity"], errors="coerce") < 10]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Products", total_products)
    col2.metric("Total Sales (₹)", f"{total_sales:,.2f}")
    col3.metric("Total Profit (₹)", f"{total_profit:,.2f}")
    col4.metric("Low Stock Items", len(low_stock))

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Recent Products")
        st.dataframe(my_products.tail(5), use_container_width=True)
    with c2:
        st.subheader("Recent Sales")
        st.dataframe(my_sales.tail(5), use_container_width=True)

    if not low_stock.empty:
        st.warning("⚠️ Low Stock Alert: " + ", ".join(low_stock["product_name"].astype(str)))


# --------------------------------------------------------------------------
# PRODUCT MANAGEMENT
# --------------------------------------------------------------------------
def products_page():
    username = st.session_state.username
    st.title("📦 Product Management")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Add Product", "View / Search Products", "Delete Product", "Upload from File"]
    )

    with tab1:
        with st.form("add_product_form"):
            product_name = st.text_input("Product Name")
            category = st.text_input("Category")
            quantity = st.number_input("Quantity", min_value=0, step=1)
            buying_price = st.number_input("Buying Price", min_value=0.0, step=0.5)
            selling_price = st.number_input("Selling Price", min_value=0.0, step=0.5)
            supplier = st.text_input("Supplier")
            submitted = st.form_submit_button("Add Product")

        if submitted:
            if not product_name:
                st.error("Product name is required.")
            else:
                products = load_csv(PRODUCTS_FILE, PRODUCTS_COLS)
                new_row = pd.DataFrame([{
                    "username": username, "product_name": product_name, "category": category,
                    "quantity": quantity, "buying_price": buying_price,
                    "selling_price": selling_price, "supplier": supplier,
                    "date": str(date.today()),
                }])
                products = pd.concat([products, new_row], ignore_index=True)
                save_csv(products, PRODUCTS_FILE)
                st.success(f"Product '{product_name}' added successfully.")

    with tab2:
        products = load_csv(PRODUCTS_FILE, PRODUCTS_COLS)
        my_products = products[products["username"] == username]

        search = st.text_input("Search by product name or category")
        if search:
            mask = (my_products["product_name"].str.contains(search, case=False, na=False) |
                    my_products["category"].str.contains(search, case=False, na=False))
            my_products = my_products[mask]

        st.dataframe(my_products, use_container_width=True)
        st.download_button(
            "⬇ Download Product Report (CSV)",
            my_products.to_csv(index=False),
            file_name="product_report.csv",
            mime="text/csv",
        )

    with tab3:
        products = load_csv(PRODUCTS_FILE, PRODUCTS_COLS)
        my_products = products[products["username"] == username]
        if my_products.empty:
            st.info("No products to delete.")
        else:
            to_delete = st.selectbox("Select product to delete", my_products["product_name"].tolist())
            if st.button("Delete Product", type="primary"):
                products = products[~((products["username"] == username) &
                                       (products["product_name"] == to_delete))]
                save_csv(products, PRODUCTS_FILE)
                st.success(f"Product '{to_delete}' deleted.")
                st.rerun()

    with tab4:
        st.write(
            "Upload a **CSV or Excel** file to add many products at once instead of "
            "typing them one by one."
        )
        st.caption(
            "Required columns: **product_name, category, quantity, buying_price, "
            "selling_price, supplier** (column names must match exactly, any order)."
        )

        template_df = pd.DataFrame(columns=[
            "product_name", "category", "quantity", "buying_price", "selling_price", "supplier"
        ])
        st.download_button(
            "⬇ Download Template File",
            template_df.to_csv(index=False),
            file_name="product_upload_template.csv",
            mime="text/csv",
        )

        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file", type=["csv", "xlsx", "xls"]
        )

        if uploaded_file is not None:
            try:
                if uploaded_file.name.lower().endswith(".csv"):
                    upload_df = pd.read_csv(uploaded_file)
                else:
                    upload_df = pd.read_excel(uploaded_file)
            except Exception as e:
                st.error(f"Could not read the file: {e}")
                upload_df = None

            if upload_df is not None:
                required_cols = ["product_name", "category", "quantity",
                                  "buying_price", "selling_price", "supplier"]
                # normalize column names: strip spaces, lowercase, replace spaces with underscore
                upload_df.columns = [
                    str(c).strip().lower().replace(" ", "_") for c in upload_df.columns
                ]
                missing = [c for c in required_cols if c not in upload_df.columns]

                if missing:
                    st.error(f"Missing required column(s): {', '.join(missing)}")
                else:
                    upload_df = upload_df[required_cols].copy()
                    upload_df["quantity"] = pd.to_numeric(upload_df["quantity"], errors="coerce").fillna(0)
                    upload_df["buying_price"] = pd.to_numeric(upload_df["buying_price"], errors="coerce").fillna(0)
                    upload_df["selling_price"] = pd.to_numeric(upload_df["selling_price"], errors="coerce").fillna(0)
                    upload_df = upload_df.dropna(subset=["product_name"])

                    st.write(f"Preview — {len(upload_df)} product(s) found:")
                    st.dataframe(upload_df, use_container_width=True)

                    if st.button("Confirm & Add These Products", type="primary"):
                        upload_df["username"] = username
                        upload_df["date"] = str(date.today())
                        upload_df = upload_df[PRODUCTS_COLS]

                        products = load_csv(PRODUCTS_FILE, PRODUCTS_COLS)
                        products = pd.concat([products, upload_df], ignore_index=True)
                        save_csv(products, PRODUCTS_FILE)
                        st.success(f"{len(upload_df)} product(s) added successfully.")
                        st.rerun()


# --------------------------------------------------------------------------
# SALES MANAGEMENT
# --------------------------------------------------------------------------
def sales_page():
    username = st.session_state.username
    st.title("💰 Sales Management")

    products = load_csv(PRODUCTS_FILE, PRODUCTS_COLS)
    my_products = products[products["username"] == username]

    tab1, tab2 = st.tabs(["Record Sale", "Sales History"])

    with tab1:
        if my_products.empty:
            st.info("Add products first before recording a sale.")
        else:
            with st.form("record_sale_form"):
                product_name = st.selectbox("Select Product", my_products["product_name"].tolist())
                quantity_sold = st.number_input("Quantity Sold", min_value=1, step=1)
                submitted = st.form_submit_button("Record Sale")

            if submitted:
                idx = my_products[my_products["product_name"] == product_name].index[0]
                available_qty = int(products.loc[idx, "quantity"])
                buying_price = float(products.loc[idx, "buying_price"])
                selling_price = float(products.loc[idx, "selling_price"])

                if quantity_sold > available_qty:
                    st.error(f"Only {available_qty} units available in stock.")
                else:
                    total_amount = quantity_sold * selling_price
                    profit = quantity_sold * (selling_price - buying_price)

                    # update stock
                    products.loc[idx, "quantity"] = available_qty - quantity_sold
                    save_csv(products, PRODUCTS_FILE)

                    # record sale
                    sales = load_csv(SALES_FILE, SALES_COLS)
                    new_sale = pd.DataFrame([{
                        "username": username, "product_name": product_name,
                        "quantity_sold": quantity_sold, "total_amount": total_amount,
                        "profit": profit, "date": str(date.today()),
                    }])
                    sales = pd.concat([sales, new_sale], ignore_index=True)
                    save_csv(sales, SALES_FILE)

                    st.success(f"Sale recorded: {quantity_sold} x {product_name} — "
                               f"₹{total_amount:,.2f} (Profit: ₹{profit:,.2f})")

    with tab2:
        sales = load_csv(SALES_FILE, SALES_COLS)
        my_sales = sales[sales["username"] == username]
        st.dataframe(my_sales, use_container_width=True)
        st.download_button(
            "⬇ Download Sales Report (CSV)",
            my_sales.to_csv(index=False),
            file_name="sales_report.csv",
            mime="text/csv",
        )


# --------------------------------------------------------------------------
# ANALYTICS
# --------------------------------------------------------------------------
def analytics_page():
    username = st.session_state.username
    st.title("📈 Analytics")

    products = load_csv(PRODUCTS_FILE, PRODUCTS_COLS)
    sales = load_csv(SALES_FILE, SALES_COLS)
    my_products = products[products["username"] == username].copy()
    my_sales = sales[sales["username"] == username].copy()

    if my_products.empty and my_sales.empty:
        st.info("No data yet. Add products and record sales to see analytics.")
        return

    my_products["quantity"] = pd.to_numeric(my_products["quantity"], errors="coerce")
    my_sales["quantity_sold"] = pd.to_numeric(my_sales["quantity_sold"], errors="coerce")
    my_sales["total_amount"] = pd.to_numeric(my_sales["total_amount"], errors="coerce")
    my_sales["profit"] = pd.to_numeric(my_sales["profit"], errors="coerce")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Products", len(my_products))
    col2.metric("Total Sales (₹)", f"{my_sales['total_amount'].sum():,.2f}")
    col3.metric("Total Profit (₹)", f"{my_sales['profit'].sum():,.2f}")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Product Category Distribution")
        if not my_products.empty:
            cat_counts = my_products["category"].value_counts()
            fig, ax = plt.subplots()
            ax.pie(cat_counts.values, labels=cat_counts.index, autopct="%1.1f%%")
            st.pyplot(fig)

    with c2:
        st.subheader("Stock Quantity by Product")
        if not my_products.empty:
            fig, ax = plt.subplots()
            ax.bar(my_products["product_name"], my_products["quantity"])
            ax.set_ylabel("Quantity")
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig)

    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Sales Over Time")
        if not my_sales.empty:
            daily_sales = my_sales.groupby("date")["total_amount"].sum()
            fig, ax = plt.subplots()
            ax.plot(daily_sales.index, daily_sales.values, marker="o")
            ax.set_ylabel("Sales (₹)")
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig)

    with c4:
        st.subheader("Profit Over Time")
        if not my_sales.empty:
            daily_profit = my_sales.groupby("date")["profit"].sum()
            fig, ax = plt.subplots()
            ax.plot(daily_profit.index, daily_profit.values, marker="o", color="green")
            ax.set_ylabel("Profit (₹)")
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig)

    st.divider()
    b1, b2 = st.columns(2)
    with b1:
        st.subheader("🏆 Best Selling Product")
        if not my_sales.empty:
            best = my_sales.groupby("product_name")["quantity_sold"].sum().idxmax()
            st.success(best)
    with b2:
        st.subheader("⚠️ Low Stock Products")
        low_stock = my_products[my_products["quantity"] < 10]
        if not low_stock.empty:
            st.dataframe(low_stock[["product_name", "quantity"]], use_container_width=True)
        else:
            st.info("No low stock products.")


# --------------------------------------------------------------------------
# REPORTS
# --------------------------------------------------------------------------
def reports_page():
    username = st.session_state.username
    st.title("📄 Reports")

    products = load_csv(PRODUCTS_FILE, PRODUCTS_COLS)
    sales = load_csv(SALES_FILE, SALES_COLS)
    my_products = products[products["username"] == username]
    my_sales = sales[sales["username"] == username]

    st.subheader("Product Report")
    st.dataframe(my_products, use_container_width=True)
    st.download_button("⬇ Download Product Report", my_products.to_csv(index=False),
                        file_name="product_report.csv", mime="text/csv")

    st.subheader("Sales Report")
    st.dataframe(my_sales, use_container_width=True)
    st.download_button("⬇ Download Sales Report", my_sales.to_csv(index=False),
                        file_name="sales_report.csv", mime="text/csv")

    st.subheader("Profit Summary")
    total_profit = pd.to_numeric(my_sales["profit"], errors="coerce").sum()
    st.metric("Total Profit (₹)", f"{total_profit:,.2f}")


# --------------------------------------------------------------------------
# MAIN ROUTER
# --------------------------------------------------------------------------
def main():
    if st.session_state.logged_in:
        st.sidebar.title(f"👤 {st.session_state.username}")
        choice = st.sidebar.radio(
            "Menu",
            ["Dashboard", "Products", "Sales", "Analytics", "Reports"],
        )
        st.sidebar.divider()
        if st.sidebar.button("Logout"):
            logout()
            st.rerun()

        if choice == "Dashboard":
            dashboard_page()
        elif choice == "Products":
            products_page()
        elif choice == "Sales":
            sales_page()
        elif choice == "Analytics":
            analytics_page()
        elif choice == "Reports":
            reports_page()
    else:
        if st.session_state.page == "home":
            home_page()
        elif st.session_state.page == "register":
            register_page()
        elif st.session_state.page == "login":
            login_page()


if __name__ == "__main__":
    main()
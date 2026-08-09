"""
db.py — Data access layer for Smart Supermarket Inventory & Sales Analytics System.
Connects to Aiven MySQL (cloud) using credentials stored in st.secrets.
All read queries are cached with st.cache_data; writes clear the relevant cache.
"""

import streamlit as st
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import certifi
from datetime import datetime


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

@st.cache_resource
def get_connection():
    """
    Create (and cache) a single MySQL connection for the session.

    Works with both Aiven MySQL and TiDB Cloud Serverless — both require TLS.
    TiDB additionally requires certificate verification, so we always point
    at a trusted CA bundle via certifi (works the same on Streamlit Cloud's
    Linux runtime as it does locally).
    """
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=st.secrets["mysql"].get("port", 4000),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            ssl_ca=certifi.where(),
            ssl_verify_identity=True,
            autocommit=True,
        )
        return conn
    except Error as e:
        st.error(f"Database connection failed: {e}")
        st.stop()


def _cursor(dictionary=True):
    conn = get_connection()
    try:
        conn.ping(reconnect=True, attempts=3, delay=1)
    except Error:
        get_connection.clear()
        conn = get_connection()
    return conn, conn.cursor(dictionary=dictionary)


def init_tables():
    """Create tables if they don't already exist (safe to call every run)."""
    conn, cur = _cursor(dictionary=False)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            name VARCHAR(150) NOT NULL,
            category VARCHAR(80) DEFAULT 'General',
            price DECIMAL(10,2) NOT NULL DEFAULT 0,
            stock INT NOT NULL DEFAULT 0,
            barcode VARCHAR(64) DEFAULT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE KEY uniq_user_barcode (user_id, barcode)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            product_id INT NOT NULL,
            quantity INT NOT NULL,
            total_price DECIMAL(10,2) NOT NULL,
            sold_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
    """)
    cur.close()


# ---------------------------------------------------------------------------
# Users / Auth
# ---------------------------------------------------------------------------

def create_user(username: str, password: str) -> tuple[bool, str]:
    conn, cur = _cursor()
    try:
        cur.execute("SELECT id FROM users WHERE username=%s", (username,))
        if cur.fetchone():
            return False, "That username is already taken."
        pw_hash = generate_password_hash(password)
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, pw_hash),
        )
        return True, "Account created successfully."
    except Error as e:
        return False, f"Signup failed: {e}"
    finally:
        cur.close()


def verify_user(username: str, password: str):
    conn, cur = _cursor()
    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    row = cur.fetchone()
    cur.close()
    if row and check_password_hash(row["password_hash"], password):
        return row
    return None


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

@st.cache_data(ttl=20)
def get_products(user_id: int) -> pd.DataFrame:
    conn, cur = _cursor()
    cur.execute(
        "SELECT * FROM products WHERE user_id=%s ORDER BY name ASC", (user_id,)
    )
    rows = cur.fetchall()
    cur.close()
    return pd.DataFrame(rows)


def get_product_by_barcode(user_id: int, barcode: str):
    """Look up a single product by barcode for this user. Returns dict or None."""
    conn, cur = _cursor()
    cur.execute(
        "SELECT * FROM products WHERE user_id=%s AND barcode=%s",
        (user_id, barcode),
    )
    row = cur.fetchone()
    cur.close()
    return row


def add_product(user_id, name, category, price, stock, barcode=None):
    conn, cur = _cursor()
    try:
        barcode = barcode.strip() if barcode else None
        cur.execute(
            """INSERT INTO products (user_id, name, category, price, stock, barcode)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            (user_id, name.strip(), category.strip() or "General", price, stock, barcode),
        )
        get_products.clear()
        return True, "Product added."
    except mysql.connector.errors.IntegrityError:
        return False, "A product with this barcode already exists."
    except Error as e:
        return False, f"Could not add product: {e}"
    finally:
        cur.close()


def restock_product(product_id: int, add_qty: int):
    """Increase stock on an existing product (used by barcode re-scan)."""
    conn, cur = _cursor()
    cur.execute(
        "UPDATE products SET stock = stock + %s WHERE id=%s", (add_qty, product_id)
    )
    cur.close()
    get_products.clear()


def update_stock(product_id: int, new_stock: int):
    conn, cur = _cursor()
    cur.execute("UPDATE products SET stock=%s WHERE id=%s", (new_stock, product_id))
    cur.close()
    get_products.clear()


def bulk_upsert_products(user_id: int, df: pd.DataFrame) -> tuple[int, int, list]:
    """
    Insert products from an uploaded CSV/Excel dataframe.
    Column names are normalized (case-insensitive) to: name, category, price, stock, barcode.
    Returns (success_count, skipped_count, error_messages).
    """
    col_map = {}
    for col in df.columns:
        key = col.strip().lower().replace(" ", "")
        if key in ("name", "productname", "itemname"):
            col_map[col] = "name"
        elif key in ("category", "cat"):
            col_map[col] = "category"
        elif key in ("price", "unitprice", "mrp"):
            col_map[col] = "price"
        elif key in ("stock", "quantity", "qty"):
            col_map[col] = "stock"
        elif key in ("barcode", "sku", "code"):
            col_map[col] = "barcode"
    df = df.rename(columns=col_map)

    success, skipped, errors = 0, 0, []
    conn, cur = _cursor()
    for i, row in df.iterrows():
        name = str(row.get("name", "")).strip()
        if not name or name.lower() == "nan":
            skipped += 1
            errors.append(f"Row {i+2}: missing product name — skipped.")
            continue
        try:
            price = float(row.get("price", 0) or 0)
        except (ValueError, TypeError):
            price = 0.0
        try:
            stock = int(float(row.get("stock", 0) or 0))
        except (ValueError, TypeError):
            stock = 0
        category = str(row.get("category", "General") or "General").strip()
        barcode = row.get("barcode")
        barcode = str(barcode).strip() if barcode and str(barcode).lower() != "nan" else None

        try:
            cur.execute(
                """INSERT INTO products (user_id, name, category, price, stock, barcode)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (user_id, name, category, price, stock, barcode),
            )
            success += 1
        except mysql.connector.errors.IntegrityError:
            skipped += 1
            errors.append(f"Row {i+2}: duplicate barcode for '{name}' — skipped.")
        except Error as e:
            skipped += 1
            errors.append(f"Row {i+2}: {e}")
    cur.close()
    get_products.clear()
    return success, skipped, errors


# ---------------------------------------------------------------------------
# Sales
# ---------------------------------------------------------------------------

@st.cache_data(ttl=20)
def get_sales(user_id: int) -> pd.DataFrame:
    conn, cur = _cursor()
    cur.execute(
        """SELECT s.id, p.name AS product_name, p.category, s.quantity,
                  s.total_price, s.sold_at
           FROM sales s JOIN products p ON s.product_id = p.id
           WHERE s.user_id=%s ORDER BY s.sold_at DESC""",
        (user_id,),
    )
    rows = cur.fetchall()
    cur.close()
    return pd.DataFrame(rows)


def record_sale(user_id: int, product_id: int, quantity: int, unit_price: float):
    conn, cur = _cursor()
    try:
        cur.execute("SELECT stock FROM products WHERE id=%s", (product_id,))
        row = cur.fetchone()
        if not row or row["stock"] < quantity:
            return False, "Not enough stock to complete this sale."
        total = round(float(unit_price) * quantity, 2)
        cur.execute(
            "INSERT INTO sales (user_id, product_id, quantity, total_price) VALUES (%s,%s,%s,%s)",
            (user_id, product_id, quantity, total),
        )
        cur.execute(
            "UPDATE products SET stock = stock - %s WHERE id=%s", (quantity, product_id)
        )
        get_products.clear()
        get_sales.clear()
        return True, f"Sale recorded — ₹{total:.2f}"
    except Error as e:
        return False, f"Could not record sale: {e}"
    finally:
        cur.close()

"""
db.py — Data access layer for Smart Supermarket Inventory & Sales Analytics System.
Connects to TiDB Cloud Serverless (MySQL-compatible) using credentials in st.secrets.
All read queries are cached with st.cache_data; writes clear the relevant cache.
"""

import time
from functools import wraps

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
    at a trusted CA bundle via certifi.

    use_pure=True forces the pure-Python MySQL driver instead of the compiled
    C extension. The C extension has crashed with low-level memory-corruption
    errors on some Streamlit Cloud runtimes running very new Python versions
    it wasn't built against — the pure-Python path avoids that entirely.
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
            use_pure=True,
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


def _with_retry(fn):
    """
    Retry a DB-facing function on transient connection errors.

    TiDB Cloud Serverless scales to zero when idle and wakes up on the next
    query — during that wake-up window the very first query can fail with a
    dropped/broken TLS session ("Lost connection", "RECORD_LAYER_FAILURE").
    That's recoverable: clear the cached connection and try again, giving
    the cluster a moment to finish waking up.

    Only applied to read-only or naturally idempotent functions (see call
    sites below) — never to functions with side effects that shouldn't run
    twice, like record_sale or add_product; those already handle their own
    errors and return a friendly message instead of retrying blindly.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        last_err = None
        for attempt in range(3):
            try:
                return fn(*args, **kwargs)
            except Error as e:
                last_err = e
                get_connection.clear()
                time.sleep(1.2 * (attempt + 1))
        raise last_err
    return wrapper


@_with_retry
def init_tables():
    """Create tables if they don't already exist (safe to call every run)."""
    conn, cur = _cursor(dictionary=False)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            shop_name VARCHAR(150) NOT NULL DEFAULT '',
            owner_name VARCHAR(150) NOT NULL DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Safe, idempotent migration for anyone who created the users table
    # before shop_name/owner_name existed (older deployments of this app).
    for col_def in ["shop_name VARCHAR(150) NOT NULL DEFAULT ''",
                     "owner_name VARCHAR(150) NOT NULL DEFAULT ''"]:
        try:
            cur.execute(f"ALTER TABLE users ADD COLUMN {col_def}")
        except Error:
            pass  # column already exists
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

def create_user(username: str, password: str, shop_name: str, owner_name: str) -> tuple[bool, str]:
    conn, cur = _cursor()
    try:
        cur.execute("SELECT id FROM users WHERE username=%s", (username,))
        if cur.fetchone():
            return False, "That username is already taken."
        pw_hash = generate_password_hash(password)
        cur.execute(
            """INSERT INTO users (username, password_hash, shop_name, owner_name)
               VALUES (%s, %s, %s, %s)""",
            (username, pw_hash, shop_name.strip(), owner_name.strip()),
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
verify_user = _with_retry(verify_user)


def user_exists(username: str) -> bool:
    conn, cur = _cursor()
    cur.execute("SELECT id FROM users WHERE username=%s", (username,))
    row = cur.fetchone()
    cur.close()
    return row is not None
user_exists = _with_retry(user_exists)


def get_user_by_username(username: str):
    conn, cur = _cursor()
    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    row = cur.fetchone()
    cur.close()
    return row
get_user_by_username = _with_retry(get_user_by_username)


def reset_password(username: str, new_password: str) -> tuple[bool, str]:
    """
    Reset a user's password by username.
    Note: this project has no email/SMS delivery set up, so this performs a
    direct reset once the username is confirmed to exist — there's no separate
    identity-verification step (like an emailed code). That's an acceptable
    trade-off for a student project, but worth mentioning if this ever handles
    real customer data.
    """
    conn, cur = _cursor()
    try:
        cur.execute("SELECT id FROM users WHERE username=%s", (username,))
        if not cur.fetchone():
            return False, "No account found with that username."
        pw_hash = generate_password_hash(new_password)
        cur.execute(
            "UPDATE users SET password_hash=%s WHERE username=%s",
            (pw_hash, username),
        )
        return True, "Password updated — you can log in now."
    except Error as e:
        return False, f"Could not reset password: {e}"
    finally:
        cur.close()


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

@st.cache_data(ttl=20)
@_with_retry
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
get_product_by_barcode = _with_retry(get_product_by_barcode)


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
restock_product = _with_retry(restock_product)


def update_stock(product_id: int, new_stock: int):
    conn, cur = _cursor()
    cur.execute("UPDATE products SET stock=%s WHERE id=%s", (new_stock, product_id))
    cur.close()
    get_products.clear()
update_stock = _with_retry(update_stock)


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
@_with_retry
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

"""
db.py — Data access layer for Smart Supermarket Inventory & Sales Analytics System.
Connects to TiDB Cloud Serverless (MySQL-compatible) using credentials in st.secrets.
All read queries are cached with st.cache_data; writes clear the relevant cache.

Driver note
-----------
This uses PyMySQL, a 100% pure-Python MySQL client — deliberately NOT
mysql-connector-python. mysql-connector-python ships an optional compiled C
extension, and even when a connection is opened with use_pure=True, the
package's import/feature-detection path can still touch that extension on
some hosts. On Streamlit Community Cloud's container image that showed up
as a hard crash at startup ("double free or corruption (!prev)" / process
aborted) the moment db.init_tables() opened its first connection — a
memory-corruption bug in the C extension itself, not fixable from our
Python code, and not something a try/except can catch (a corrupted-heap
abort takes the whole process down). PyMySQL has no C extension at all, so
that entire failure class is structurally impossible here.

Product images
--------------
Product images were removed from the app. Nothing here reads or writes an
image column any more. Older deployments whose `products` table already has
an `image_url` column don't need a migration — the column is nullable, every
INSERT below simply omits it, and it's dropped from the Excel report. If you
want it gone from the schema for good, run this once by hand:

    ALTER TABLE products DROP COLUMN image_url;
"""

import time
from functools import wraps

import streamlit as st
import pymysql
import pymysql.cursors
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
    """
    try:
        conn = pymysql.connect(
            host=st.secrets["mysql"]["host"],
            port=st.secrets["mysql"].get("port", 4000),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            ssl={"ca": certifi.where()},
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor,
        )
        return conn
    except pymysql.err.Error as e:
        st.error(f"Database connection failed: {e}")
        st.stop()


def _cursor(dictionary=True):
    conn = get_connection()
    try:
        conn.ping(reconnect=True)
    except pymysql.err.Error:
        get_connection.clear()
        conn = get_connection()
    cursor_cls = pymysql.cursors.DictCursor if dictionary else pymysql.cursors.Cursor
    return conn, conn.cursor(cursor_cls)


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
            except pymysql.err.Error as e:
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
            mobile VARCHAR(30) DEFAULT NULL,
            email VARCHAR(190) DEFAULT NULL,
            profile_photo MEDIUMBLOB NULL,
            profile_photo_mime VARCHAR(100) DEFAULT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Safe, idempotent migration for anyone who created the users table
    # before shop_name/owner_name existed (older deployments of this app).
    for col_def in [
        "shop_name VARCHAR(150) NOT NULL DEFAULT ''",
        "owner_name VARCHAR(150) NOT NULL DEFAULT ''",
        "mobile VARCHAR(30) DEFAULT NULL",
        "email VARCHAR(190) DEFAULT NULL",
        "profile_photo MEDIUMBLOB NULL",
        "profile_photo_mime VARCHAR(100) DEFAULT NULL",
    ]:
        try:
            cur.execute(f"ALTER TABLE users ADD COLUMN {col_def}")
        except pymysql.err.Error:
            pass  # column already exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            name VARCHAR(150) NOT NULL,
            category VARCHAR(80) DEFAULT 'General',
            cost_price DECIMAL(10,2) NOT NULL DEFAULT 0,
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
            cost_price DECIMAL(10,2) NOT NULL DEFAULT 0,
            sold_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
    """)
    # Idempotent migrations for databases created by the previous version.
    for table, col_def in [
        ("products", "cost_price DECIMAL(10,2) NOT NULL DEFAULT 0"),
        ("sales", "cost_price DECIMAL(10,2) NOT NULL DEFAULT 0"),
    ]:
        try:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {col_def}")
        except pymysql.err.Error:
            pass
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
    except pymysql.err.Error as e:
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


def get_user_by_id(user_id: int):
    conn, cur = _cursor()
    cur.execute("SELECT id, username, shop_name, owner_name, mobile, email, profile_photo, profile_photo_mime FROM users WHERE id=%s", (user_id,))
    row = cur.fetchone()
    cur.close()
    return row
get_user_by_id = _with_retry(get_user_by_id)


def update_profile(user_id: int, shop_name: str, owner_name: str, mobile: str, email: str, photo_bytes=None, photo_mime=None):
    conn, cur = _cursor()
    try:
        if photo_bytes is None:
            cur.execute(
                "UPDATE users SET shop_name=%s, owner_name=%s, mobile=%s, email=%s WHERE id=%s",
                (shop_name.strip(), owner_name.strip(), mobile.strip() or None, email.strip() or None, user_id),
            )
        else:
            cur.execute(
                "UPDATE users SET shop_name=%s, owner_name=%s, mobile=%s, email=%s, profile_photo=%s, profile_photo_mime=%s WHERE id=%s",
                (shop_name.strip(), owner_name.strip(), mobile.strip() or None, email.strip() or None, photo_bytes, photo_mime, user_id),
            )
        return True, "Profile updated successfully."
    except pymysql.err.Error as e:
        return False, f"Could not update profile: {e}"
    finally:
        cur.close()


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
    except pymysql.err.Error as e:
        return False, f"Could not reset password: {e}"
    finally:
        cur.close()


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

@st.cache_data(ttl=20)
@_with_retry
def get_products(user_id: int) -> pd.DataFrame:
    """
    Fetch this shop's products. Columns are named explicitly rather than
    SELECT * so that a leftover image_url column in an older deployment's
    table never reaches the UI or the Excel report.
    """
    conn, cur = _cursor()
    cur.execute(
        """SELECT id, user_id, name, category, cost_price, price, stock, barcode, created_at
           FROM products WHERE user_id=%s ORDER BY name ASC""",
        (user_id,),
    )
    rows = cur.fetchall()
    cur.close()
    return pd.DataFrame(rows)


def get_product_by_barcode(user_id: int, barcode: str):
    """Look up a single product by barcode for this user. Returns dict or None."""
    conn, cur = _cursor()
    cur.execute(
        """SELECT id, user_id, name, category, cost_price, price, stock, barcode, created_at
           FROM products WHERE user_id=%s AND barcode=%s""",
        (user_id, barcode),
    )
    row = cur.fetchone()
    cur.close()
    return row
get_product_by_barcode = _with_retry(get_product_by_barcode)


def add_product(user_id, name, category, price, stock, barcode=None, cost_price=0.0):
    """Add a single product (used by the manual "Add product" form)."""
    conn, cur = _cursor()
    try:
        barcode = barcode.strip() if barcode else None
        cur.execute(
            """INSERT INTO products (user_id, name, category, cost_price, price, stock, barcode)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (user_id, name.strip(), category.strip() or "General", cost_price, price, stock, barcode),
        )
        get_products.clear()
        return True, "Product added."
    except pymysql.err.IntegrityError:
        return False, "A product with this barcode already exists."
    except pymysql.err.Error as e:
        return False, f"Could not add product: {e}"
    finally:
        cur.close()


def delete_product(product_id: int):
    """
    Permanently remove a product. Because products.id is referenced by
    sales.product_id with ON DELETE CASCADE, this also removes that
    product's sales history — the "Remove product" tab in the UI warns
    about this and requires the shopkeeper to confirm before calling this.
    """
    conn, cur = _cursor()
    try:
        cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
        get_products.clear()
        get_sales.clear()
        return True, "Product removed."
    except pymysql.err.Error as e:
        return False, f"Could not remove product: {e}"
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
    Column names are normalized (case-insensitive) to:
    name, category, price, stock, barcode.

    Any image/photo column in the uploaded sheet is ignored — the app
    doesn't show product pictures.

    Returns (success_count, skipped_count, error_messages).
    """
    col_map = {}
    for col in df.columns:
        key = col.strip().lower().replace(" ", "")
        if key in ("name", "productname", "itemname"):
            col_map[col] = "name"
        elif key in ("category", "cat"):
            col_map[col] = "category"
        elif key in ("costprice", "cost", "purchaseprice", "buyprice"):
            col_map[col] = "cost_price"
        elif key in ("price", "unitprice", "mrp", "sellingprice"):
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
            cost_price = float(row.get("cost_price", 0) or 0)
        except (ValueError, TypeError):
            cost_price = 0.0
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
                """INSERT INTO products (user_id, name, category, cost_price, price, stock, barcode)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (user_id, name, category, cost_price, price, stock, barcode),
            )
            success += 1
        except pymysql.err.IntegrityError:
            skipped += 1
            errors.append(f"Row {i+2}: duplicate barcode for '{name}' — skipped.")
        except pymysql.err.Error as e:
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
                  s.total_price, s.cost_price, s.sold_at
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
        cur.execute("SELECT stock, cost_price FROM products WHERE id=%s", (product_id,))
        row = cur.fetchone()
        if not row or row["stock"] < quantity:
            return False, "Not enough stock to complete this sale."
        total = round(float(unit_price) * quantity, 2)
        cost_price = float(row.get("cost_price") or 0)
        cur.execute(
            "INSERT INTO sales (user_id, product_id, quantity, total_price, cost_price) VALUES (%s,%s,%s,%s,%s)",
            (user_id, product_id, quantity, total, cost_price),
        )
        cur.execute(
            "UPDATE products SET stock = stock - %s WHERE id=%s", (quantity, product_id)
        )
        get_products.clear()
        get_sales.clear()
        return True, f"Sale recorded — ₹{total:.2f}"
    except pymysql.err.Error as e:
        return False, f"Could not record sale: {e}"
    finally:
        cur.close()



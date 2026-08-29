import sqlite3
import hashlib
from datetime import datetime

DB_PATH = "shop.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            barcode TEXT,
            image_url TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total REAL NOT NULL,
            sold_at TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    """)

    # Seed a default admin user if none exists
    cur.execute("SELECT COUNT(*) as c FROM users")
    if cur.fetchone()["c"] == 0:
        cur.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            ("admin", hash_password("admin123"), datetime.now().isoformat()),
        )

    conn.commit()
    conn.close()


# ---------- Auth ----------

def verify_user(username: str, password: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        return False
    return row["password_hash"] == hash_password(password)


def create_user(username: str, password: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, hash_password(password), datetime.now().isoformat()),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


# ---------- Products ----------

def add_product(name, category, price, stock, barcode, image_url):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO products (name, category, price, stock, barcode, image_url, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (name, category, price, stock, barcode, image_url, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_products(search: str = ""):
    conn = get_connection()
    cur = conn.cursor()
    if search:
        cur.execute(
            "SELECT * FROM products WHERE name LIKE ? OR category LIKE ? ORDER BY created_at DESC",
            (f"%{search}%", f"%{search}%"),
        )
    else:
        cur.execute("SELECT * FROM products ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_product(product_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_product(product_id, name, category, price, stock, barcode, image_url):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """UPDATE products SET name=?, category=?, price=?, stock=?, barcode=?, image_url=?
           WHERE id=?""",
        (name, category, price, stock, barcode, image_url, product_id),
    )
    conn.commit()
    conn.close()


def delete_product(product_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()


def adjust_stock(product_id: int, delta: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (delta, product_id))
    conn.commit()
    conn.close()


# ---------- Sales ----------

def record_sale(product_id: int, quantity: int):
    product = get_product(product_id)
    if not product or product["stock"] < quantity:
        return False, "Not enough stock available."

    total = product["price"] * quantity
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO sales (product_id, product_name, quantity, unit_price, total, sold_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (product_id, product["name"], quantity, product["price"], total, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()
    adjust_stock(product_id, -quantity)
    return True, "Sale recorded."


def get_sales(limit: int = None):
    conn = get_connection()
    cur = conn.cursor()
    if limit:
        cur.execute("SELECT * FROM sales ORDER BY sold_at DESC LIMIT ?", (limit,))
    else:
        cur.execute("SELECT * FROM sales ORDER BY sold_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------- Dashboard / Reports ----------

def get_dashboard_stats():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) as c FROM products")
    total_products = cur.fetchone()["c"]

    cur.execute("SELECT COALESCE(SUM(stock), 0) as s FROM products")
    total_stock = cur.fetchone()["s"]

    cur.execute("SELECT COALESCE(SUM(total), 0) as s FROM sales")
    total_revenue = cur.fetchone()["s"]

    cur.execute("SELECT COUNT(*) as c FROM sales")
    total_sales = cur.fetchone()["c"]

    cur.execute("SELECT * FROM products WHERE stock <= 5 ORDER BY stock ASC")
    low_stock = [dict(r) for r in cur.fetchall()]

    conn.close()
    return {
        "total_products": total_products,
        "total_stock": total_stock,
        "total_revenue": total_revenue,
        "total_sales": total_sales,
        "low_stock": low_stock,
    }


def get_sales_by_day(days: int = 14):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT date(sold_at) as day, SUM(total) as revenue, SUM(quantity) as units
           FROM sales GROUP BY day ORDER BY day DESC LIMIT ?""",
        (days,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return list(reversed(rows))


def get_top_products(limit: int = 5):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT product_name, SUM(quantity) as units_sold, SUM(total) as revenue
           FROM sales GROUP BY product_name ORDER BY revenue DESC LIMIT ?""",
        (limit,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

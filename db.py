"""
db.py — MySQL connection and all database helper functions.
Uses the existing supermarket_db database (users, products, sales tables).
"""

import mysql.connector
import pandas as pd


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="supermarket_user",
        password="@Krisha/!2007",   # replace with your real password
        database="supermarket_db"
    )


# ---------------- USERS ----------------

def create_user(shop_name, email, password_hash):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (shop_name, email, password_hash) VALUES (%s, %s, %s)",
            (shop_name, email, password_hash)
        )
        conn.commit()
        return True, "Account created successfully."
    except mysql.connector.IntegrityError:
        return False, "An account with this email already exists."
    finally:
        cursor.close()
        conn.close()


def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


# ---------------- PRODUCTS ----------------

def add_product(user_id, name, category, price, stock_quantity, reorder_level, supplier):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO products (user_id, name, category, price, stock_quantity, reorder_level, supplier)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (user_id, name, category, price, stock_quantity, reorder_level, supplier)
    )
    conn.commit()
    cursor.close()
    conn.close()


def bulk_add_products(user_id, dataframe):
    """
    Expects a DataFrame with columns:
    name, category, price, stock_quantity, reorder_level, supplier
    (from an uploaded CSV/Excel file)
    """
    conn = get_connection()
    cursor = conn.cursor()
    for _, row in dataframe.iterrows():
        cursor.execute(
            """INSERT INTO products (user_id, name, category, price, stock_quantity, reorder_level, supplier)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                user_id,
                row.get("name", ""),
                row.get("category", ""),
                float(row.get("price", 0) or 0),
                int(row.get("stock_quantity", 0) or 0),
                int(row.get("reorder_level", 10) or 10),
                row.get("supplier", ""),
            )
        )
    conn.commit()
    cursor.close()
    conn.close()


def get_products(user_id):
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM products WHERE user_id = %s", conn, params=(user_id,))
    conn.close()
    return df


def get_low_stock_products(user_id):
    conn = get_connection()
    df = pd.read_sql(
        "SELECT * FROM products WHERE user_id = %s AND stock_quantity <= reorder_level",
        conn, params=(user_id,)
    )
    conn.close()
    return df


def update_stock_after_sale(product_id, quantity_sold):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s",
        (quantity_sold, product_id)
    )
    conn.commit()
    cursor.close()
    conn.close()


# ---------------- SALES ----------------

def add_sale(user_id, product_id, quantity_sold, total_amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO sales (user_id, product_id, quantity_sold, total_amount)
           VALUES (%s, %s, %s, %s)""",
        (user_id, product_id, quantity_sold, total_amount)
    )
    conn.commit()
    cursor.close()
    conn.close()
    update_stock_after_sale(product_id, quantity_sold)


def get_sales(user_id):
    conn = get_connection()
    query = """
        SELECT s.sale_id, p.name AS product_name, p.category, s.quantity_sold,
               s.total_amount, s.sale_date
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        WHERE s.user_id = %s
        ORDER BY s.sale_date DESC
    """
    df = pd.read_sql(query, conn, params=(user_id,))
    conn.close()
    return df


def get_sales_summary(user_id):
    df = get_sales(user_id)
    total_revenue = df["total_amount"].sum() if not df.empty else 0
    total_sales = df["quantity_sold"].sum() if not df.empty else 0
    return total_revenue, total_sales, df

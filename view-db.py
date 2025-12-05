import sqlite3

def view_customers(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers;")
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    print(f"\nContents of table: customers")
    print(f"{' | '.join(column_names)}")
    print("-" * (len(' | '.join(column_names)) + 10))
    for row in rows:
        print(f"{' | '.join(map(str, row))}")
    conn.close()

def view_complaints(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints;")
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    print(f"\nContents of table: complaints")
    print(f"{' | '.join(column_names)}")
    print("-" * (len(' | '.join(column_names)) + 10))
    for row in rows:
        print(f"{' | '.join(map(str, row))}")
    conn.close()

def view_orders(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders;")
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    print(f"\nContents of table: orders")
    print(f"{' | '.join(column_names)}")
    print("-" * (len(' | '.join(column_names)) + 10))
    for row in rows:
        print(f"{' | '.join(map(str, row))}")
    conn.close()

def view_products(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products;")
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    print(f"\nContents of table: products")
    print(f"{' | '.join(column_names)}")
    print("-" * (len(' | '.join(column_names)) + 10))
    for row in rows:
        print(f"{' | '.join(map(str, row))}")
    conn.close()

def view_order_details(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orderDetails;")
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    print(f"\nContents of table: orderDetails")
    print(f"{' | '.join(column_names)}")
    print("-" * (len(' | '.join(column_names)) + 10))
    for row in rows:
        print(f"{' | '.join(map(str, row))}")
    conn.close()

# Path to your SQLite database file
db_file = 'walmart.db'

# View contents of each table
view_customers(db_file)
view_complaints(db_file)
view_orders(db_file)
# view_products(db_file)
# view_order_details(db_file)

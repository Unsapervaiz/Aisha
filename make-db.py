import sqlite3
import random
import string

# Function to generate patterned IDs
def generate_order_id():
    number_part = random.randint(10000, 99999)
    letters_part = ''.join(random.choices(string.ascii_uppercase, k=3))
    return f"{number_part}{letters_part}"

def generate_product_id():
    number_part = random.randint(1000, 9999)
    letters_part = ''.join(random.choices(string.ascii_uppercase, k=5))
    return f"{number_part}{letters_part}"

def generate_user_id():
    return f"U{random.randint(1000, 9999)}"

def generate_ticket_no():
    return f"{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}{random.randint(1000, 9999)}"

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('walmart.db')
cursor = conn.cursor()

# Create tables

# Customers table
cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    userId TEXT PRIMARY KEY,
    firstName TEXT NOT NULL,
    lastName TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    address TEXT,
    registrationDate DATE DEFAULT (datetime('now'))
)
''')

# Complaints table with phone number instead of userId
cursor.execute('''
CREATE TABLE IF NOT EXISTS complaints (
    ticketNo TEXT PRIMARY KEY,
    phone TEXT,
    issue TEXT NOT NULL,
    complaintDate DATE DEFAULT (datetime('now')),
    status TEXT DEFAULT 'Open',
    FOREIGN KEY (phone) REFERENCES customers (phone)
)
''')

# Orders table
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    orderId TEXT PRIMARY KEY,
    userId TEXT,
    orderDate DATE DEFAULT (datetime('now')),
    totalAmount REAL NOT NULL,
    status TEXT DEFAULT 'Pending',
    shippingAddress TEXT,
    FOREIGN KEY (userId) REFERENCES customers (userId)
)
''')

# Products table
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    productId TEXT PRIMARY KEY,
    productName TEXT NOT NULL,
    price REAL NOT NULL,
    stockQuantity INTEGER NOT NULL
)
''')

# OrderDetails table to track which products are in which orders
cursor.execute('''
CREATE TABLE IF NOT EXISTS orderDetails (
    orderDetailId INTEGER PRIMARY KEY AUTOINCREMENT,
    orderId TEXT,
    productId TEXT,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (orderId) REFERENCES orders (orderId),
    FOREIGN KEY (productId) REFERENCES products (productId)
)
''')

# Insert sample records into customers table
customers = [
    (generate_user_id(), 'Dhairya', 'Arora', 'dhairya2arora@gmail.com', '9811264318', '357, Hakikat Nagar, Delhi-110009'),
    (generate_user_id(), 'Yash', 'Khattar', 'yashkhattar73@gmail.com', '8448721780', 'Gurugram, Haryana'),
    (generate_user_id(), 'Yash', 'Khattar', 'yashkhattar83@gmail.com', '8448721745', 'Gurugram, Haryana'),
    (generate_user_id(), 'Ravi', 'Sharma', 'ravi.sharma@example.com', '9876543210', 'Noida, Uttar Pradesh'),
    (generate_user_id(), 'Sneha', 'Patel', 'sneha.patel@example.com', '9988776655', 'Mumbai, Maharashtra')
]
cursor.executemany('''
INSERT INTO customers (userId, firstName, lastName, email, phone, address)
VALUES (?, ?, ?, ?, ?, ?)
''', customers)

# Insert sample records into complaints table
complaints = [
    (generate_ticket_no(), customers[0][4], 'Incorrect item received'),
    (generate_ticket_no(), customers[1][4], 'Late delivery'),
    (generate_ticket_no(), customers[2][4], 'Product arrived damaged'),
    (generate_ticket_no(), customers[3][4], 'Received wrong size'),
    (generate_ticket_no(), customers[4][4], 'Product not as described')
]
cursor.executemany('''
INSERT INTO complaints (ticketNo, phone, issue)
VALUES (?, ?, ?)
''', complaints)

# Insert sample records into orders table
orders = [
    (generate_order_id(), customers[0][0], '2024-08-01', 1000, 'Shipped', '357, Hakikat Nagar, Delhi-110009'),
    (generate_order_id(), customers[1][0], '2024-08-02', 1200, 'Pending', 'Gurugram, Haryana'),
    (generate_order_id(), customers[2][0], '2024-08-03', 1500, 'Delivered', '357, Hakikat Nagar, Delhi-110009'),
    (generate_order_id(), customers[3][0], '2024-08-04', 2000, 'Shipped', 'Noida, Uttar Pradesh'),
    (generate_order_id(), customers[4][0], '2024-08-05', 2500, 'Pending', 'Mumbai, Maharashtra')
]
cursor.executemany('''
INSERT INTO orders (orderId, userId, orderDate, totalAmount, status, shippingAddress)
VALUES (?, ?, ?, ?, ?, ?)
''', orders)

# Insert sample records into products table
products = [
    (generate_product_id(), 'Laptop', 70000, 10),
    (generate_product_id(), 'Smartphone', 30000, 20),
    (generate_product_id(), 'Headphones', 4000, 50),
    (generate_product_id(), 'Smartwatch', 10000, 15),
    (generate_product_id(), 'Keyboard', 1500, 25)
]
cursor.executemany('''
INSERT INTO products (productId, productName, price, stockQuantity)
VALUES (?, ?, ?, ?)
''', products)

# Insert sample records into orderDetails table
order_details = [
    (orders[0][0], products[0][0], 1, 70000),
    (orders[0][0], products[2][0], 2, 4000),
    (orders[1][0], products[1][0], 1, 30000),
    (orders[2][0], products[0][0], 1, 70000),
    (orders[2][0], products[1][0], 1, 30000),
    (orders[3][0], products[3][0], 1, 10000),
    (orders[4][0], products[4][0], 1, 1500)
]
cursor.executemany('''
INSERT INTO orderDetails (orderId, productId, quantity, price)
VALUES (?, ?, ?, ?)
''', order_details)

# Commit and close the connection
conn.commit()
conn.close()

print("Tables created and sample records inserted successfully.")

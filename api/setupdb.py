import os
import mysql.connector

# Configuration via environment variables with sensible defaults
DB_NAME = os.environ.get("MYSQL_DATABASE", "mijn_database")
DB_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")  # force TCP
DB_PORT = int(os.environ.get("MYSQL_PORT", 3306))
DB_USER = os.environ.get("MYSQL_USER", "root")
DB_PASSWORD = os.environ.get("MYSQL_PASSWORD", "pass")

# 1. Connect without specifying a database (so we can create it)
conn = mysql.connector.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
)
cursor = conn.cursor()

# 2. Create the database if it doesn't exist
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
print(f"Database '{DB_NAME}' ready.")

# 3. Reuse the connection to set the database
conn.database = DB_NAME

# 4. Create tables
# 4. Create tables (in dependency order)
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(150),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(30),
    role VARCHAR(50) DEFAULT 'USER',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    birth_year INT,
    active TINYINT(1) DEFAULT 1
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS parking_lots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    address VARCHAR(255),
    capacity INT NOT NULL DEFAULT 0,
    reserved INT NOT NULL DEFAULT 0,
    tariff DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    daytariff DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    lat DECIMAL(9,6),
    lng DECIMAL(9,6)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    license_plate VARCHAR(20) NOT NULL UNIQUE,
    make VARCHAR(100),
    model VARCHAR(100),
    color VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    parking_lot_id INT,
    vehicle_id INT,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    cost DECIMAL(10, 2),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    FOREIGN KEY (parking_lot_id) REFERENCES parking_lots(id) ON DELETE CASCADE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    payment_id VARCHAR(255) NOT NULL UNIQUE,
    amount DECIMAL(12,2) DEFAULT 0,
    initiator VARCHAR(255),
    processed_by VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed DATETIME,
    coupled_to VARCHAR(255),
    hash VARCHAR(255)
)
""")

def seed_db(cursor):
    pl = {
        "name": "Natuur Enschede Parking",
        "location": "Beach/Recreation",
        "capacity": 388,
        "hourly_rate": 3.0,
        "created_at": "2018-02-15"
    }

    cursor.execute("SELECT id FROM parking_lots WHERE name = %s", (pl["name"],))
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO parking_lots (name, location, capacity, hourly_rate, created_at) VALUES (%s, %s, %s, %s, %s)",
            (pl["name"], pl["location"], pl["capacity"], pl["hourly_rate"], pl["created_at"])
        )
        print("Seeded parking_lots:", pl["name"])
    else:
        print("Parking lot already present:", pl["name"])

    tx = {
        "payment_id": "tx_0001",
        "amount": 0.00,
        "initiator": "system",
        "processed_by": "system",
        "created_at": "2025-01-01 00:00:00",
        "completed": None,
        "coupled_to": "none",
        "hash": "abc123"
    }

    cursor.execute("SELECT id FROM payments WHERE payment_id = %s", (tx["payment_id"],))
    if cursor.fetchone() is None:
        cursor.execute(
            """
            INSERT INTO payments
            (payment_id, amount, initiator, processed_by, created_at, completed, coupled_to, hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (tx["payment_id"], tx["amount"], tx["initiator"], tx["processed_by"], tx["created_at"], tx["completed"], tx["coupled_to"], tx["hash"])
        )
        print("Seeded payments:", tx["payment_id"])
    else:
        print("Payment already present:", tx["payment_id"])
seed_db(cursor)



conn.commit()
cursor.close()
conn.close()

import os

from loaddb import load_data
import mysql.connector


# Configuration via environment variables with sensible defaults

DB_NAME = os.environ.get("MYSQL_DATABASE", "mobypark")
DB_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")  # force TCP
DB_PORT = int(os.environ.get("MYSQL_PORT", 3307))
DB_USER = os.environ.get("MYSQL_USER", "stilstaan")
DB_PASSWORD = os.environ.get("MYSQL_PASSWORD", "stil")

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
    hash VARCHAR(255),
    session_id INT,
    parking_lot_id INT
)
""")

def seed_db(cursor):
    # pl_data = load_data.load_parkinglots()
    # rs_data = load_data.load_reservations()
    # vs_data = load_data.load_vehicles()
    # us_data = load_data.load_users()
    lp = load_data.load_payments()
  # Seed users
    # for us in us_data:
    #     cursor.execute(
    #         """
    #         INSERT IGNORE INTO users
    #         (username, password, name, email, phone, role, created_at, birth_year, active)
    #         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    #         """,
    #         (us["username"], us["password"], us["name"], us["email"], us["phone"], us["role"],
    #         us["created_at"], us["birth_year"], us["active"])
    #     )
    # print("Seeded users (duplicates ignored)")

    
    # Seed parkinglots
    # for pl in pl_data:
    #     cursor.execute(
    #             "INSERT IGNORE INTO parking_lots (name, location, address, capacity, reserved, tariff, daytariff, created_at, lat, lng) VALUES (%s, %s, %s, %s, %s,%s, %s,%s, %s,%s)",
    #             (pl["name"], pl["location"], pl["address"], pl["capacity"], pl["reserved"], pl["tariff"],pl["daytariff"],pl["created_at"],pl["lat"],pl["lng"])
    #         )
    # print("Seeded parking_lots:", pl["name"])

    # # Seed reservations
    # for rs in rs_data:
    #     cursor.execute(
    #             "INSERT IGNORE INTO reservations (user_id, parking_lot_id, vehicle_id, start_time, end_time, status, created_at, cost) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
    #             (rs["user_id"], rs["parking_lot_id"], rs["vehicle_id"], rs["start_time"], rs["end_time"], rs['status'], rs["created_at"], rs["cost"])
    #         )
    # print("Seeded reservations")

    # Seed vehicles
    # for vs in vs_data:
    #     cursor.execute(
    #             "INSERT IGNORE INTO vehicles (user_id, license_plate, make, model, color, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
    #             (vs["user_id"], vs["license_plate"], vs["make"], vs["model"], vs["color"], vs["created_at"])
    #         )
    # print("Seeded vehicles")


     # Seed Payments
    for pay in lp:
        cursor.execute(
                """
                    INSERT IGNORE INTO payments (transaction_id, amount, initiator, processed_by, created_at, completed, date, method, issuer, bank, hash, session_id, parking_lot_id) 
                    VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s)
                """,
                    (pay["transaction_id"],
                    pay["amount"],
                    pay["initiator"],
                    pay["processed_by"],
                    pay["created_at"],
                    pay["completed"],
                    pay["method"],
                    pay["issuer"],
                    pay["bank"],
                    pay["hash"],
                    pay["session_id"],
                    pay["parking_lot_id"])
              
            )
    print("Seeded payments")
seed_db(cursor)



conn.commit()
cursor.close()
conn.close()

import os

from loaddb import load_data
import mysql.connector
from mysql.connector import IntegrityError

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
    username  VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(150),
    email VARCHAR(255) ,
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
    license_plate VARCHAR(20) NOT NULL ,
    make VARCHAR(100),
    model VARCHAR(100),
    color VARCHAR(50),
    year VARCHAR(50),
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
    status VARCHAR(50),
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    cost DECIMAL(10, 2),
               
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parking_lot_id) REFERENCES parking_lots(id) ON DELETE CASCADE
)
""")
#[{"id":"1","user_id":"281","parking_lot_id":"217","vehicle_id":"471","start_time":"2025-12-03T11:00:00Z","end_time":"2025-12-03T14:00:00Z","status":"confirmed","created_at":"2025-12-01T11:00:00Z","cost":7.5}



cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction VARCHAR(255) NOT NULL UNIQUE,
    amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    initiator VARCHAR(255) NOT NULL,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ,
    completed DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    method VARCHAR(255),
    issuer VARCHAR(255),
    bank VARCHAR(255),
    hash VARCHAR(255) NOT NULL ,
    session_id INT NOT NULL,
    parking_lot_id INT NOT NULL,
               

    FOREIGN KEY (parking_lot_id) REFERENCES parking_lots(id) ON DELETE CASCADE
)
""")
cursor.execute("""
                CREATE TABLE IF NOT EXISTS parking_sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    parking_lot_id INT NOT NULL,
                    licenseplate VARCHAR(255) NOT NULL,
                    started DATETIME DEFAULT CURRENT_TIMESTAMP,
                    stopped DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user VARCHAR(30),
                    duration_minutes INT,
                    cost DECIMAL(12,2),
                    payment_status VARCHAR(50),
                            
                    
                    FOREIGN KEY (parking_lot_id) REFERENCES parking_lots(id) ON DELETE CASCADE
                )
                """)

conn.commit()

def seed_db(cursor):
    # pl_data = load_data.load_parkinglots()
    # rs_data = load_data.load_reservations()
    # vs_data = load_data.load_vehicles()
    # us_data = load_data.load_users()

  # Seed users
    # for us in us_data:
    #     cursor.execute(
    #         """
    #         INSERT INTO users
    #         (username, password, name, email, phone, role, created_at, birth_year, active)
    #         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    #         """,
    #         (us["username"], us["password"], us["name"], us["email"], us["phone"], us["role"],
    #         us["created_at"], us["birth_year"], us["active"])
    #     )
    # print("Seeded users (duplicates ignored)")
    # conn.commit() 
    
    # Seed parkinglots
    # for pl in pl_data:
    #     cursor.execute(
    #             "INSERT INTO parking_lots (name, location, address, capacity, reserved, tariff, daytariff, created_at, lat, lng) VALUES (%s, %s, %s, %s, %s,%s, %s,%s, %s,%s)",
    #             (pl["name"], pl["location"], pl["address"], pl["capacity"], pl["reserved"], pl["tariff"],pl["daytariff"],pl["created_at"],pl["lat"],pl["lng"])
    #         )
    # print("Seeded parking_lots:", pl["name"])
    # conn.commit() 
    
    # # Seed reservations
    # for rs in rs_data:
    #     cursor.execute(
    #             "INSERT INTO reservations (user_id, parking_lot_id, vehicle_id, start_time, end_time, status, created_at, cost) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
    #             (rs["user_id"], rs["parking_lot_id"], rs["vehicle_id"], rs["start_time"], rs["end_time"], rs['status'], rs["created_at"], rs["cost"])
    #         )
    # print("Seeded reservations")
    # conn.commit() 
    
    # Seed vehicles
    # for vs in vs_data:
    #     cursor.execute(
    #             "INSERT INTO vehicles (user_id, license_plate, make, model, color, year, created_at) VALUES (%s, %s, %s, %s, %s, %s,  %s)",
    #             (vs["user_id"], vs["license_plate"], vs["make"], vs["model"], vs["color"], vs["year"], vs["created_at"]) 
    #         )
    # print("Seeded vehicles")
    # conn.commit() 

    # Seed parking sessions
    # seed_parking_sessions_batch
    # print("Seeded parking sessions")

     # Seed Payments
    seed_payments_batch()
    print("Seeded payments")
    
# seed_db(cursor)


def seed_parking_sessions_batch():
    sesh = load_data.load_parking_sessions()  # 6M rows
  
    BATCH_SIZE = 5000  # smaller chunks to avoid max_allowed_packet
    c = 0
    sql = """
    INSERT INTO parking_sessions
    (parking_lot_id, licenseplate, started, stopped, user, duration_minutes, cost, payment_status)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    for i in range(0, len(sesh), BATCH_SIZE):
        batch = sesh[i:i + BATCH_SIZE]
        values = [
            (
                row["parking_lot_id"],
                row["licenseplate"],
                row["started"],
                row["stopped"],
                row["user"],
                row["duration_minutes"],
                row["cost"],
                row["payment_status"]
            )
            for row in batch
        ]
        placeholders = ",".join(["(%s, %s, %s, %s, %s, %s, %s, %s)"] * len(values))

        sql = f"""
        INSERT INTO parking_sessions
        (parking_lot_id, licenseplate, started, stopped, user, duration_minutes, cost, payment_status)
        VALUES {placeholders}
        """

        flat_values = [item for row in values for item in row]
        c+=1
        cursor.execute(sql, flat_values)

        print(f"Inserted {c} batch of {len(values)} rows")
        
        conn.commit()  # commit per batch
    cursor.close()
    conn.close()

def seed_payments_batch():
    conn.autocommit = False
    c = 350
    sesh = load_data.load_payments()
    BATCH_SIZE = 5000

 

    print("SQL insert started")

    cursor = conn.cursor()   

    start_index = 350 * 5000
    BLOCK_TRANSACTION = "1535349fea5cca288b217d491838f836AA"
    for i in range(start_index, len(sesh), BATCH_SIZE):
        batch = sesh[i:i + BATCH_SIZE]
        batch = [
        row for row in batch
        if row["transaction"] != BLOCK_TRANSACTION
        ] 
        values = [
            (
                row["transaction"],
                row["amount"],
                row["initiator"],
                row["created_at"],
                row["completed"],
                row["hash"],
                row["date"],
                row["method"],
                row["issuer"],
                row["bank"],
                row["session_id"],
                row["parking_lot_id"]
            )
            for row in batch
        ]

        placeholders = ",".join(["(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"] * len(values))

        sql = f"""
        INSERT IGNORE INTO payments
        (transaction, amount, initiator, created_at, completed, hash, date, method, issuer, bank, session_id, parking_lot_id)
        VALUES {placeholders}
        """
        print(f"Inserted {c}")
        c+=len(values)
        flat_values = [item for row in values for item in row]

        try:
            cursor.execute(sql, flat_values)
        except IntegrityError as e:
            print("IntegrityError caught!")
            print("Batch that caused the error:")
            for row in batch:
                print("Initiator:", row["initiator"])
            raise e  # Re-raise to stop execution if you want
        conn.commit()

    # Commit once at the end (MUCH FASTER)
    conn.commit()

    cursor.close()

    conn.close()

seed_db(cursor)


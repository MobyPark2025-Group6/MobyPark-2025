import os
import mysql.connector
from argon2 import PasswordHasher

ph = PasswordHasher()


def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
        port=int(os.environ.get("MYSQL_PORT", 3307)),
        user=os.environ.get("MYSQL_USER", "stilstaan"),
        password=os.environ.get("MYSQL_PASSWORD", "stil"),
        database=os.environ.get("MYSQL_DATABASE", "mobypark"),
    )


def needs_hash(value: str) -> bool:
    return not (isinstance(value, str) and value.startswith("$argon2"))


def fetch_users(conn):
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT id, password FROM users")
        return cursor.fetchall()


def update_passwords(conn, updates):
    with conn.cursor() as cursor:
        cursor.executemany(
            "UPDATE users SET password = %s WHERE id = %s",
            updates,
        )


def rehash_all_passwords():
    count = 0
    conn = get_db_connection()
    try:
        users = fetch_users(conn)
        updates = []
        for user in users:
            current = user.get("password")
            if current is None:
                continue
            if needs_hash(current):
                count+=1
                updates.append((ph.hash(current), user["id"]))
                print(count)
        if updates:
            update_passwords(conn, updates)
            conn.commit()
            print(f"Updated {len(updates)} passwords")
        else:
            print("No passwords needed rehashing")
    finally:
        conn.close()


if __name__ == "__main__":
    rehash_all_passwords()

import os
import mysql.connector
from argon2 import PasswordHasher

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
        port=int(os.environ.get("MYSQL_PORT", 3307)),
        user=os.environ.get("MYSQL_USER", "stilstaan"),
        password=os.environ.get("MYSQL_PASSWORD", "stil"),
        database=os.environ.get("MYSQL_DATABASE", "mobypark"),
    )
conn = get_db_connection()
cursor = conn.cursor(dictionary=True) 

users = cursor.execute("SELECT * FROM users")
us = cursor.fetchall()
conn.commit() 
cursor.close()
conn.close()
ph = PasswordHasher()

for i in range(0,len(us)):
    print(i)
    us[i]["password"] = ph.hash(us[i]["password"]) 
for i in range(0,10):
    print(us[i])

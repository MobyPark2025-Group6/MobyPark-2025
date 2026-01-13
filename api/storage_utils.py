import json
import csv
import os
from datetime import datetime, timedelta
from loaddb import load_data
import mysql.connector
import math

import datetime 
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


def normalize_row(row):
    for key, value in row.items():
        if isinstance(value, datetime.datetime):
            row[key] = value.strftime("%Y-%m-%d %H:%M:%S")
        else:
            row[key] = str(value)
    return row

def save_record(table: str, data: dict, update_on_duplicate: bool = False) -> int:
    """Insert a row into MySQL and optionally update on duplicate key."""
    if not data:
        raise ValueError("No data provided to save")

    columns = ", ".join(data.keys())
    placeholders = ", ".join(["%s"] * len(data))
    values = tuple(data.values())

    sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    if update_on_duplicate:
        updates = ", ".join([f"{col}=VALUES({col})" for col in data.keys()])
        sql += f" ON DUPLICATE KEY UPDATE {updates}"

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, values)
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()
    
#Grabs the data from table for a given name
def load_data_db_table(tablename):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) 
    
    cursor.execute(f"SELECT * FROM {tablename}")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    content = [normalize_row(row) for row in rows]
    return content

def get_item_db(Row, Item, TableName):

    conn = get_db_connection()

    cursor = conn.cursor(dictionary=True) 
   
    cursor.execute(f"""
                   SELECT * FROM {TableName}
                   WHERE {Row} = '{Item}'
                   """)
    
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    content = [normalize_row(row) for row in rows]
    return content

def change_data(table,values,condition):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) 
    columns = list(values.keys())
  
    # value used in WHERE clause
    cond_val = values[condition]

    # keys except the condition key
    update_keys = [k for k in values.keys() if k != condition]

    # corresponding values (in same order)
    update_values = [values[k] for k in update_keys]

    set_sql = f"""UPDATE {table}\n SET """
    count = 0

    for c in columns:
        if not c == condition:
            if count + 1 != len(columns) - 1:
                set_string = f"{c} = %s, \n "
                set_sql += set_string
                count+=1 
            else:
                set_string = f"{c} = %s \n "
                set_sql += set_string
                count+=1 
    set_sql+=f"\n WHERE {condition} = {cond_val}"

    cursor.execute(set_sql, update_values)
    conn.commit()
    cursor.close()
    conn.close()
    
def create_data(table, values):
    return save_record(table, values)

def delete_data(item, Row, table):
        sql =   f"""
                DELETE FROM {table} 
                WHERE {Row} = {item};
                """
        

        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()

class save_vehicle:

    def create_vehicle(vehicle_data):
        create_data("Vehicles", vehicle_data)
  
    def change_vehicle(vehicle_data):
        change_data("vehicles", vehicle_data, "id")
        
    def delete_vehicle(id):
        delete_data("vehicles",id)
        

class save_payment:
    def create_payment(payment_data):
        create_data("payments",payment_data)

    def change_payment(payment_data):
        change_data("payments", payment_data, "id")

    def delete_payment(id):
        delete_data("payments",id)

class save_user:
    def create_user(user_data):
        create_data('users',user_data)

    def change_user(user_data):
        change_data("users", user_data, "id")

    def delete_user(id):
        delete_data("users",id)

class save_parking_lot:
    def create_plt(plt_data):
        create_data("parking_lots",plt_data)

    def change_plt(plt_data):
        change_data("parking_lots", plt_data, "id")

    def delete_plt(id):
        delete_data("parking_lots",id)

class save_discount:
    def create_discount(discount_data):
        create_data("discounts",discount_data)
   
    def change_discount(change_discount):
        change_data("discounts", change_discount, "id")

    def delete_discount(id):
        delete_data("discounts",id)

class save_reservation:
    def create_reservation(rsv_data):
        create_data("reservations",rsv_data)

    def change_reservation(rsv_data):
        change_data("reservations", rsv_data, "id")

    def delete_reservation(id):
        delete_data("reservations",id)

class save_parking_sessions:

    def create_parking_sessions(parking_session_data):
        create_data("parking_sessions", parking_session_data)
  
    def change_parking_sessions(parking_session_data):
        change_data("parking_sessions", parking_session_data, "id")
        
    def delete_parking_sessions(id):
        delete_data("parking_sessions",id)
        
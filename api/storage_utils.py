import json
import csv
import os

from loaddb import load_data
import mysql.connector

import datetime 
def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
        port=int(os.environ.get("MYSQL_PORT", 3307)),
        user=os.environ.get("MYSQL_USER", "stilstaan"),
        password=os.environ.get("MYSQL_PASSWORD", "stil"),
        database=os.environ.get("MYSQL_DATABASE", "mobypark"),
    )
def normalize_row(row):
    for key, value in row.items():
        if isinstance(value, datetime.datetime):
            row[key] = value.strftime("%Y-%m-%d %H:%M:%S")
        else:
            row[key] = str(value)
    return row

def load_json(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            if isinstance(data, list):
                return {str(i+1): v for i, v in enumerate(data)}
            return data
    except FileNotFoundError:
        return {}

def write_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, default=str)

def load_csv(filename):
    try:
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            return [row for row in reader]
    except FileNotFoundError:
        return []

def write_csv(filename, data):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        for row in data:
            writer.writerow(row)

def load_text(filename):
    try:
        with open(filename, 'r') as file:
            return file.readlines()
    except FileNotFoundError:
        return []

def write_text(filename, data):
    with open(filename, 'w') as file:
        for line in data:
            file.write(line + '\n')

def save_data(filename, data):
    if filename.endswith('.json'):
        write_json(filename, data)
    elif filename.endswith('.csv'):
        write_csv(filename, data)
    elif filename.endswith('.txt'):
        write_text(filename, data)
    else:
        raise ValueError("Unsupported file format") 

def load_data(filename):
    if filename.endswith('.json'):
        return load_json(filename)
    elif filename.endswith('.csv'):
        return load_csv(filename)
    elif filename.endswith('.txt'):
        return load_text(filename)
    else:
        return None
    
#Grabs the data from table for a given name
#Handles the following : 
#   vehicles, users, parking_lots, payments (TODO), reservations, sessions (TODO), 
def load_data_db_table(tablename):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) 
    
    cursor.execute(f"SELECT * FROM {tablename}")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    content = [normalize_row(row) for row in rows]
    return content


def save_user_data(data):
    save_data('data/users.json', data)

def load_parking_lot_data():
    return load_data('data/parking-lots.json')

def save_parking_lot_data(data):
    save_data('data/parking-lots.json', data)

def save_reservation_data(data):
    save_data('data/reservations.json', data)

def load_payment_data():
    # conn = get_db_connection()
    # cursor = conn.cursor(dictionary=True) 
    # cursor.execute("SELECT * FROM payments")
    # rows = cursor.fetchall()
    # cursor.close()
    # conn.close()
    # pys = [normalize_row(row) for row in rows]
    # return pys
    return load_json("data/payments")

def save_payment_data(data):
    save_data('data/payments.json', data)

def load_discounts_data():
    return load_data('data/discounts.csv')

def save_discounts_data(data):
    save_data('data/discounts.csv', data)

def save_vehicle_data(data):
    save_data('data/vehicles.json', data)


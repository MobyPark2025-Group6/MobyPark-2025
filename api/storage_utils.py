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
conn = get_db_connection()
cursor = conn.cursor(dictionary=True) 


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

def get_item_db(Row, Item, TableName):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) 
   
    cursor.execute(f"""
                   SELECT * FROM {TableName}
                   WHERE {Row} = %s
                   """,(Item,))
    
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

def delete_data(item, Row, table):
        sql =   f"""
                DELETE FROM {table} 
                WHERE {Row} = %s;
                """
        cursor.execute(sql,(item,))

class save_vehicle:

    def create_vehicle(vehicle_data):
        u_id,lp,make,model,color,year,c, = vehicle_data
        sql = """
                    INSERT INTO
                    (user_id, license_plate, make, model, color, year, year)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
              """
        values = (
            u_id,    # parking_lot_id
            lp,      # licenseplate
            make,    # started
            model,   # stopped
            color,   # user
            year,    # duration_minutes
            c,       # cost
       
        )
        cursor.execute(sql, values)

  
    def change_vehicle(vehicle_data):
        u_id,lp,make,model,color,year,c,id = vehicle_data
        sql = """
                UPDATE vehicles
                SET user_id = '%s', 
                license_plate = '%s', 
                make = '%s',
                model ='%s',
                color='%s',
                year='%s',
                year='%s',

                WHERE id = '%s'

            """
        values = (
            u_id,    # parking_lot_id
            lp,      # licenseplate
            make,    # started
            model,   # stopped
            color,   # user
            year,    # duration_minutes
            c,       # cost
            id
        )
        cursor.execute(sql, values)
        
    def delete_vehicle(id):
        delete_data("vehicles",id)
        

class save_payment:
    def create_payment(payment_data):
        pass
    def change_payment(payment_data):
        pass

    def delete_payment(id):
        delete_data("payments",id)

class save_user:
    def create_user(user_data):
        pass
    def change_user(user_data):
        pass

    def delete_user(id):
        delete_data("users",id)

class save_parking_lot:
    def create_plt(plt_data):
        pass
    def change_plt(plt_data):
        pass

    def delete_plt(id):
        delete_data("parking_lots",id)

class save_discount:
    def create_discount(discount_data):
        pass
    def change_plt(change_discount):
        pass

    def delete_discount(id):
        delete_data("discounts",id)

class save_reservation:
    def create_reservation(rsv_data):
        pass
    def change_reservation(rsv_data):
        pass

    def delete_reservation(rsv_data):
        delete_data("reservations",id)
import json 
import pathlib
import os 
import csv
from datetime import datetime

class load_data :

    def time_convert(time : str):
        if not time:
            return None 
        return datetime.fromisoformat(time.replace("Z", "+00:00"))
    
    def payment_time_convert(time : str):
        if not time:
            return None 
        return datetime.strptime(time[:19], '%d-%m-%Y %H:%M:%S')
    
    def parking_sesh_time_convert(time : str):
        if not time:
            return None 
        return datetime.strptime(
        time.replace("T", " "), 
        "%Y-%m-%d %H:%M:%S%z"
    )
    

    def load_users():
        with open('../data/users.json', 'r') as file:
            data = json.load(file)
            rows = []
            for u in data:
                    if u.get('username') == 'testuser':
                        print("Test user removed")
                        continue
                    rows.append({
                            'username':u.get('username'),
                            'password':u.get('password'),
                            'name':u.get('name'),
                            'email':u.get('email'),
                            'phone':u.get('phone'),
                            'role':u.get('role'),
                            'created_at': load_data.time_convert(u.get('created_at')),
                            'birth_year':u.get('birth_year'),
                            'active':1 if u.get('active', True) else 0,
                        })
            return rows

    def load_vehicles():
        with open('../data/vehicles.json', 'r') as file:
            data = json.load(file)
            rows = []
            for u in data:
                rows.append({
                    'user_id':u.get('user_id'),
                    'license_plate':u.get('license_plate'),
                    'make':u.get('make'),
                    'model':u.get('model'),
                    'color':u.get('color'),
                    'year':u.get('year'),
                    'created_at':load_data.time_convert(u.get('created_at')),
                })
            return rows

    def load_reservations():
        with open('../data/reservations.json', 'r') as file:
            data = json.load(file)
            rows = []
            for u in data:
                rows.append({
                   'user_id': u.get('user_id'),
                   'parking_lot_id':u.get('parking_lot_id'),
                   'vehicle_id': u.get('vehicle_id'),
                   'start_time':load_data.time_convert(u.get('start_time')),
                   'end_time': load_data.time_convert(u.get('end_time')),
                   'status':u.get('status'),
                   'created_at':load_data.time_convert(u.get('created_at')),
                   'cost':u.get('cost')
                })
            return rows
        
    def load_parkinglots():
        with open('../data/parking-lots.json', 'r') as file:
            data = json.load(file)
            rows = []
            for u in data:
                rows.append({
                    'name': data[u].get('name'),
                    'location':data[u].get('location'),
                    'address':data[u].get('address'),
                    'capacity':data[u].get('capacity'),
                    'reserved':data[u].get('reserved'),
                    'tariff':data[u].get('tariff'),
                    'daytariff':data[u].get('daytariff'),
                    'created_at': load_data.time_convert(data[u].get('created_at')),
                    'lat':data[u]['coordinates'].get('lat'),
                    'lng':data[u]['coordinates'].get('lng')
                })
            return rows
        
    def load_parking_sessions():
        route = pathlib.Path('../data/pdata')
        files = []
        for (root, dirs, file) in os.walk(route):
            for f in file:
                if '.json' in f:
                    files.append(f)

        files.sort(key = lambda f : int(f.replace("-sessions.json","").replace("p","")))
        rows = []
        for t in files:
            with open(f'../data/pdata/{t}', 'r') as file:
                data = json.load(file)               
                for u in data:
                    rows.append({
                        "parking_lot_id": data[u]["parking_lot_id"],
                        "licenseplate":data[u]["licenseplate"],
                        "started":load_data.parking_sesh_time_convert(data[u]["started"]),
                        "stopped":load_data.parking_sesh_time_convert(data[u]["stopped"]),
                        "user":data[u]["user"],
                        "duration_minutes":data[u]["duration_minutes"],
                        "cost":data[u]["cost"],
                        "payment_status":data[u]["payment_status"],

                    })
        return rows
            
    def load_payments():
        with open('../data/payments.json', 'r') as f:
            txt = f.read()

        # Try to recover everything before the corruption
        try:
            data = json.loads(txt)
        except json.JSONDecodeError as e:
            cut = e.pos
            recovered = txt[:cut]

            # Try to wrap it in a valid array
            if recovered.rstrip().endswith('}'):
                recovered += ']'
        
            data = json.loads(recovered)
            rows = []
            for u in data:
               
                rows.append({
                    "transaction": u.get("transaction"),
                    "amount":  u.get("amount"),
                    "initiator":  u.get("initiator"),
                    "created_at": load_data.payment_time_convert(u.get('created_at')),
                    "completed": load_data.payment_time_convert(u.get('completed')),
                    "date":load_data.time_convert(u["t_data"].get('date')),
                    "method":u["t_data"].get('method'),
                    "issuer":u["t_data"].get('issuer'),
                    "bank":u["t_data"].get('bank'),
                    "hash": u.get("hash"),
                    "session_id":u.get("session_id"),
                    "parking_lot_id":u.get("parking_lot_id")
                })
            return rows

# ps = load_data.load_parking_sessions()
# print(ps[0])
#  transaction VARCHAR(255) NOT NULL UNIQUE,
#     amount DECIMAL(12,2) DEFAULT 0,
#     initiator VARCHAR(255),

#     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
#     completed DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
#     date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
#     method VARCHAR(255) NOT NULL,
#     issuer VARCHAR(255) NOT NULL,
#     bank VARCHAR(255) NOT NULL,
#     hash VARCHAR(255) NOT NULL,
#     session_id INT,
#     parking_lot_id INT,
# payments = load_data.load_payments()
# print(payments[0])
# # for i in payments:
# #     if i['transaction'] or i['amount'] or i['issuer'] or ['session_id']== None :
# #         print(i)

print(len(load_data.load_payments()))
print(4370256)
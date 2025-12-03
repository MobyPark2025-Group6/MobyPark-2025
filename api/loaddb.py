import json 
import pathlib
import os 
from datetime import datetime

class load_data :

    def time_convert(time : str):
        if not time:
            return None 
        return datetime.fromisoformat(time.replace("Z", "+00:00"))
    
    def load_users():
        with open('../data/users.json', 'r') as file:
            data = json.load(file)
            rows = []
            for u in data:
               
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
        for t in files:
            with open(f'../data/pdata/{t}', 'r') as file:
                data = json.load(file)
                rows = []
                for u in data:
                    rows.append((
                        ##
                    ))
                return rows
            
    def load_payments():
        with open('../data/payments.json', 'r') as file:
            data = file.read()
            return data
# print(load_data.load_payments())
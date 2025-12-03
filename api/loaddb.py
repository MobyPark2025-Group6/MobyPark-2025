import json 
import pathlib
import os 

class load_data :
    def load_users():
        with open('../data/users.json', 'r') as file:
            data = json.load(file)
            rows = []
            for u in data:
                rows.append((
                    u.get('username'),
                    u.get('password'),
                    u.get('name'),
                    u.get('email'),
                    u.get('phone'),
                    u.get('role'),
                    u.get('created_at'),
                    u.get('birth_year'),
                    1 if u.get('active', True) else 0,
                ))

            return rows

    def load_vehicles():
        with open('../data/vehicles.json', 'r') as file:
            data = json.load(file)
            rows = []
            for u in data:
                rows.append((
                    u.get('user_id'),
                    u.get('license_plate'),
                    u.get('make'),
                    u.get('model'),
                    u.get('color'),
                    u.get('created_at')
                ))
            return rows

    def load_reservations():
        with open('../data/reservations.json', 'r') as file:
            data = json.load(file)
            rows = []
            for u in data:
                rows.append((
                    u.get('user_id'),
                    u.get('parking_lot_id'),
                    u.get('vehicle_id'),
                    u.get('start_time'),
                    u.get('end_time'),
                    u.get('created_at'),
                    u.get('cost')
                ))

            return rows
        
    def load_parkinglots():
        with open('../data/parking-lots.json', 'r') as file:
            data = json.load(file)
            rows = []
            for u in data:
                rows.append((
                    data[u].get('name'),
                    data[u].get('location'),
                    data[u].get('address'),
                    data[u].get('capacity'),
                    data[u].get('reserved'),
                    data[u].get('tariff'),
                    data[u].get('daytariff'),
                    data[u].get('created_at'),
                    data[u]['coordinates'].get('lat'),
                    data[u]['coordinates'].get('lng')
                ))

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
print(load_data.load_payments())
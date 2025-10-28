#{"id":"1","user_id":"1","license_plate":"76-KQQ-7","make":"Peugeot","model":"308","color":"Brown","year":2024,"created_at":"2024-08-13"}
from typing import Optional
from pydantic import BaseModel

class Vehicle(BaseModel):
    id : str
    user_id : str
    license_plate : str 
    make : str 
    model : str 
    color : str
    year : int 
    created_at : str

class UpdateVehicle(BaseModel):
    license_plate: Optional[str] = None
    model: Optional[str] = None
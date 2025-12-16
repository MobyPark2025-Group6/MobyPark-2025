from datetime import datetime
from pydantic import BaseModel

class DiscountBase(BaseModel):
    amount : int
    created_at : str
    lot_id : str 
    code : str 

class DiscountTime(DiscountBase):
    expiration_date : datetime 


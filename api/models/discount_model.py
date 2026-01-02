from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class DiscountBase(BaseModel):
    amount : Optional[int] = None
    created_at : datetime
    lot_id : Optional[str]
    code : str 
    percentage : Optional[float]
    expiration_date : Optional[datetime ]
    user_id : Optional[int]

class DiscountCreate(BaseModel):
    amount : Optional[int] = None
    lot_id : Optional[int] = None
    code : Optional[str] = None 
    percentage : Optional[float]= None
    expiration_date : Optional[datetime]= None
    user_id : Optional[int]= None
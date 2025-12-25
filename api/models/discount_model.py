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
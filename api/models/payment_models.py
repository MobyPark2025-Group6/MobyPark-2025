from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class PaymentBase(BaseModel):
    id : int
    transaction: str
    amount: float
    initiator: Optional[str] = None
    created_at: str
    completed: Optional[str] = None
    date : str 
    method : str 
    issuer : str 
    bank : str 
    hash : str 
    session_id : int 
    parking_lot_id : int 


class PaymentCreate(BaseModel):
    """Used for creating new payments"""
    parking_lot_id : int 
    license_plate : str 
    session_id : str 

class PaymentRefund(PaymentBase):
    """Used for refunding payments"""
    pass

class PaymentUpdate(BaseModel):
    """Used for completing transactions"""
    disc_code : str 
    method : str 
    issuer : str 
    bank : str 

class PaymentOut(BaseModel):
    transaction: str
    amount: float
    initiator: Optional[str] = None
    processed_by: Optional[str] = None
    created_at: str
    completed: Optional[str] = None
    coupled_to: Optional[str] = None
    hash: str
    license_plate : str 

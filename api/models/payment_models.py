from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class PaymentBase(BaseModel):
    transaction: str
    amount: float
    initiator: Optional[str] = None
    created_at: str
    completed: Optional[str] = None
    hash: str


class PaymentCreate(BaseModel):
    """Used for creating new payments"""
    amount: float


class PaymentRefund(BaseModel):
    """Used for refunding payments"""
    amount: float
    coupled_to: str


class PaymentUpdate(BaseModel):
    """Used for completing transactions"""
    t_data: Dict[str, Any]
    validation: str

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

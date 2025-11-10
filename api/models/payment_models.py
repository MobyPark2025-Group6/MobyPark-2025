from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class PaymentBase(BaseModel):
    transaction: Optional[str] = None
    amount: float
    coupled_to: Optional[str] = None

class PaymentCreate(PaymentBase):
    """Used for creating new payments"""
    pass

class PaymentRefund(PaymentBase):
    """Used for refunding payments"""
    pass

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

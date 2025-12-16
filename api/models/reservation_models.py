from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class ReservationRegister(BaseModel):
    user_id: Optional[str] = None
    lot_id: str
    vehicle_id: str
    start_time: int
    end_time: int

class ReservationResponse(BaseModel):
    id: str
    user_id: str
    parking_lot_id: str
    vehicle_id: str
    start_time: datetime
    end_time: datetime
    created_at: datetime
    cost: Optional[float] = None
    status: str

class ReservationOut(BaseModel):
    id: Optional[str] = None
    user_id: str
    lot_id: str
    vehicle_id: str
    start_time: datetime
    end_time: datetime
    created_at: Optional[datetime] = None
    cost: Optional[float] = None
    status: Optional[str] = None
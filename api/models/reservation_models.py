from pydantic import BaseModel
from typing import Optional

class ReservationRegister(BaseModel):
    user_id: Optional[str] = None
    lot_id: str
    vehicle_id: str
    start_time: int
    end_time: int
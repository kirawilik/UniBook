from datetime import date, time, datetime
from typing import Literal, Optional
from pydantic import BaseModel


class ReservationEvent(BaseModel):
    event_type: Literal["ReservationCreated", "ReservationCancelled"]
    reservation_id: int
    user_id: int
    resource_id: int
    date: date
    start_time: time
    end_time: time
    created_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
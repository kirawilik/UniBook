from datetime import date, time, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, model_validator


class ReservationCreate(BaseModel):
    user_id: int
    resource_id: int
    date: date
    start_time: time
    end_time: time

    @model_validator(mode="after")
    def check_times(self):
        if self.start_time >= self.end_time:
            raise ValueError("start_time doit être avant end_time")
        return self


class ReservationUpdate(BaseModel):
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None


class ReservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    resource_id: int
    date: date
    start_time: time
    end_time: time
    status: str
    created_at: Optional[datetime] = None
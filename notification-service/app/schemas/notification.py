from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    reservation_id: int
    user_id: int
    resource_id: int
    message: str
    status: str
    created_at: datetime
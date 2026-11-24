from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import NotificationOut
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationOut])
def list_all(user_id: Optional[int] = None, skip: int = 0, limit: int = 50,
             db: Session = Depends(get_db)):
    return notification_service.list_notifications(db, user_id, skip, limit)


@router.get("/{notification_id}", response_model=NotificationOut)
def get_one(notification_id: int, db: Session = Depends(get_db)):
    notification = notification_service.get_notification(db, notification_id)
    if not notification:
        raise HTTPException(404, "Notification introuvable")
    return notification
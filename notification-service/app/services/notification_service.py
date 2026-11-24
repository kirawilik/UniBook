from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Notification
from app.schemas import ReservationEvent


def build_message(event: ReservationEvent) -> str:
    slot = f"le {event.date} de {event.start_time:%H:%M} à {event.end_time:%H:%M}"
    if event.event_type == "ReservationCreated":
        return f"Réservation #{event.reservation_id} créée : ressource {event.resource_id}, {slot}"
    return f"Réservation #{event.reservation_id} annulée : ressource {event.resource_id}, {slot}"


def process_event(db: Session, event: ReservationEvent) -> Notification:
    """كتسجل إشعار من حدث. إلا وصل نفس الحدث مرتين، كترجع الإشعار القديم."""
    existing = db.scalars(
        select(Notification).where(
            Notification.event_type == event.event_type,
            Notification.reservation_id == event.reservation_id,
        )
    ).first()
    if existing:
        return existing

    notification = Notification(
        event_type=event.event_type,
        reservation_id=event.reservation_id,
        user_id=event.user_id,
        resource_id=event.resource_id,
        message=build_message(event),
        status="Sent",
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def list_notifications(db: Session, user_id: int | None = None, skip: int = 0, limit: int = 50):
    stmt = select(Notification)
    if user_id is not None:
        stmt = stmt.where(Notification.user_id == user_id)
    return db.scalars(stmt.order_by(Notification.id.desc()).offset(skip).limit(limit)).all()


def get_notification(db: Session, notification_id: int) -> Notification | None:
    return db.get(Notification, notification_id)
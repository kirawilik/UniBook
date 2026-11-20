from datetime import date, time
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.reservation import Reservation
from schemas.reservation import ReservationCreate, ReservationUpdate
from services.resource_client import check_resource, check_user


def _check_conflict(db: Session, resource_id: int, day: date,
                    start: time, end: time, exclude_id: Optional[int] = None):
    query = db.query(Reservation).filter(
        Reservation.resource_id == resource_id,
        Reservation.date == day,
        Reservation.status == "CONFIRMED",
        Reservation.start_time < end,
        Reservation.end_time > start,
    )
    if exclude_id is not None:
        query = query.filter(Reservation.id != exclude_id)
    if query.first():
        raise HTTPException(status_code=409, detail="Créneau déjà réservé pour cette ressource")


def create_reservation(db: Session, data: ReservationCreate) -> Reservation:
    check_user(data.user_id)
    check_resource(data.resource_id)
    _check_conflict(db, data.resource_id, data.date, data.start_time, data.end_time)

    reservation = Reservation(
        user_id=data.user_id,
        resource_id=data.resource_id,
        date=data.date,
        start_time=data.start_time,
        end_time=data.end_time,
        status="CONFIRMED",
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    # Epic 4 : publish_event("ReservationCreated", reservation)
    return reservation


def get_reservation(db: Session, reservation_id: int) -> Reservation:
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation introuvable")
    return reservation


def update_reservation(db: Session, reservation_id: int, data: ReservationUpdate) -> Reservation:
    reservation = get_reservation(db, reservation_id)
    if reservation.status == "CANCELLED":
        raise HTTPException(status_code=400, detail="Une réservation annulée ne peut pas être modifiée")

    new_date = data.date or reservation.date
    new_start = data.start_time or reservation.start_time
    new_end = data.end_time or reservation.end_time
    if new_start >= new_end:
        raise HTTPException(status_code=422, detail="start_time doit être avant end_time")

    _check_conflict(db, reservation.resource_id, new_date, new_start, new_end,
                    exclude_id=reservation.id)

    reservation.date = new_date
    reservation.start_time = new_start
    reservation.end_time = new_end
    db.commit()
    db.refresh(reservation)
    return reservation


def cancel_reservation(db: Session, reservation_id: int) -> Reservation:
    reservation = get_reservation(db, reservation_id)
    if reservation.status == "CANCELLED":
        raise HTTPException(status_code=400, detail="Réservation déjà annulée")
    reservation.status = "CANCELLED"
    db.commit()
    db.refresh(reservation)
    # Epic 4 : publish_event("ReservationCancelled", reservation)
    return reservation


def list_reservations(db: Session, user_id: Optional[int] = None,
                      resource_id: Optional[int] = None):
    query = db.query(Reservation)
    if user_id is not None:
        query = query.filter(Reservation.user_id == user_id)
    if resource_id is not None:
        query = query.filter(Reservation.resource_id == resource_id)
    return query.order_by(Reservation.date.desc(), Reservation.start_time.desc()).all()
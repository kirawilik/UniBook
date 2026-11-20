from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas.reservation import ReservationCreate, ReservationUpdate, ReservationOut
from services import reservation_service as service

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.post("", response_model=ReservationOut, status_code=201)
def create(data: ReservationCreate, db: Session = Depends(get_db)):
    return service.create_reservation(db, data)


@router.get("", response_model=List[ReservationOut])
def history(user_id: Optional[int] = None, resource_id: Optional[int] = None,
            db: Session = Depends(get_db)):
    return service.list_reservations(db, user_id, resource_id)


@router.get("/{reservation_id}", response_model=ReservationOut)
def get_one(reservation_id: int, db: Session = Depends(get_db)):
    return service.get_reservation(db, reservation_id)


@router.put("/{reservation_id}", response_model=ReservationOut)
def update(reservation_id: int, data: ReservationUpdate, db: Session = Depends(get_db)):
    return service.update_reservation(db, reservation_id, data)


@router.patch("/{reservation_id}/cancel", response_model=ReservationOut)
def cancel(reservation_id: int, db: Session = Depends(get_db)):
    return service.cancel_reservation(db, reservation_id)
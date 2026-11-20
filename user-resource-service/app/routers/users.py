from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UserCreate, UserUpdate, UserOut
from app.services import user_service
from app.services.user_service import EmailAlreadyExists

router = APIRouter(prefix="/users", tags=["Users"])


def _get_or_404(db: Session, user_id: int):
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(404, "Utilisateur introuvable")
    return user


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create(data: UserCreate, db: Session = Depends(get_db)):
    try:
        return user_service.create_user(db, data)
    except EmailAlreadyExists:
        raise HTTPException(409, "Cet email existe déjà")


@router.get("", response_model=list[UserOut])
def list_all(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return user_service.list_users(db, skip, limit)


@router.get("/{user_id}", response_model=UserOut)
def get_one(user_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, user_id)


@router.put("/{user_id}", response_model=UserOut)
def update(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    user = _get_or_404(db, user_id)
    try:
        return user_service.update_user(db, user, data)
    except EmailAlreadyExists:
        raise HTTPException(409, "Cet email existe déjà")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(user_id: int, db: Session = Depends(get_db)):
    user_service.deactivate_user(db, _get_or_404(db, user_id))
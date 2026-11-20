from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.services.security import hash_password


class EmailAlreadyExists(Exception):
    pass


def create_user(db: Session, data: UserCreate) -> User:
    user = User(
        full_name=data.full_name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise EmailAlreadyExists()
    db.refresh(user)
    return user


def list_users(db: Session, skip: int = 0, limit: int = 50):
    return db.scalars(select(User).order_by(User.id).offset(skip).limit(limit)).all()


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def update_user(db: Session, user: User, data: UserUpdate) -> User:
    changes = data.model_dump(exclude_unset=True)
    if "password" in changes:
        user.password_hash = hash_password(changes.pop("password"))
    for field, value in changes.items():
        setattr(user, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise EmailAlreadyExists()
    db.refresh(user)
    return user


def deactivate_user(db: Session, user: User) -> None:
    user.is_active = False
    db.commit()
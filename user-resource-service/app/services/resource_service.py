from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Resource
from app.schemas import ResourceCreate, ResourceUpdate


def create_resource(db: Session, data: ResourceCreate) -> Resource:
    resource = Resource(**data.model_dump())
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


def list_resources(db: Session, type=None, only_active=True, skip=0, limit=50):
    stmt = select(Resource)
    if type:
        stmt = stmt.where(Resource.type == type)
    if only_active:
        stmt = stmt.where(Resource.is_active == True)  # noqa: E712
    return db.scalars(stmt.order_by(Resource.id).offset(skip).limit(limit)).all()


def get_resource(db: Session, resource_id: int) -> Resource | None:
    return db.get(Resource, resource_id)


def update_resource(db: Session, resource: Resource, data: ResourceUpdate) -> Resource:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(resource, field, value)
    db.commit()
    db.refresh(resource)
    return resource


def deactivate_resource(db: Session, resource: Resource) -> None:
    resource.is_active = False
    db.commit()
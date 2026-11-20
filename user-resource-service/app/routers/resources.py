from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ResourceCreate, ResourceUpdate, ResourceOut, ResourceType
from app.services import resource_service

router = APIRouter(prefix="/resources", tags=["Resources"])


def _get_or_404(db: Session, resource_id: int):
    resource = resource_service.get_resource(db, resource_id)
    if not resource:
        raise HTTPException(404, "Ressource introuvable")
    return resource


@router.post("", response_model=ResourceOut, status_code=status.HTTP_201_CREATED)
def create(data: ResourceCreate, db: Session = Depends(get_db)):
    return resource_service.create_resource(db, data)


@router.get("", response_model=list[ResourceOut])
def list_all(type: Optional[ResourceType] = None, only_active: bool = True,
             skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return resource_service.list_resources(db, type, only_active, skip, limit)


@router.get("/{resource_id}", response_model=ResourceOut)
def get_one(resource_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, resource_id)


@router.put("/{resource_id}", response_model=ResourceOut)
def update(resource_id: int, data: ResourceUpdate, db: Session = Depends(get_db)):
    return resource_service.update_resource(db, _get_or_404(db, resource_id), data)


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(resource_id: int, db: Session = Depends(get_db)):
    resource_service.deactivate_resource(db, _get_or_404(db, resource_id))
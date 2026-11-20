from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, ConfigDict

ResourceType = Literal["Classroom", "Laboratory", "Equipment"]


class ResourceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    type: ResourceType
    description: Optional[str] = Field(default=None, max_length=500)
    location: str = Field(min_length=1, max_length=200)
    capacity: Optional[int] = Field(default=None, ge=0)


class ResourceUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    type: Optional[ResourceType] = None
    description: Optional[str] = Field(default=None, max_length=500)
    location: Optional[str] = Field(default=None, min_length=1, max_length=200)
    capacity: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None


class ResourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: ResourceType
    description: Optional[str]
    location: str
    capacity: Optional[int]
    is_active: bool
    created_at: datetime
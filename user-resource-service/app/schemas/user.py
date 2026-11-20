from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

RoleType = Literal["Student", "Teacher", "Admin"]


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    role: RoleType


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=6, max_length=72)
    role: Optional[RoleType] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    role: RoleType
    is_active: bool
    created_at: datetime
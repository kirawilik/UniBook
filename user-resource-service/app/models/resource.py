from sqlalchemy import Integer, Unicode, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Resource(Base):
    __tablename__ = "Resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Unicode(150), nullable=False)
    type: Mapped[str] = mapped_column(Unicode(30), nullable=False)
    description: Mapped[str | None] = mapped_column(Unicode(500), nullable=True)
    location: Mapped[str] = mapped_column(Unicode(200), nullable=False)
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.sysdatetime())
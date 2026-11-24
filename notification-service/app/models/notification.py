from sqlalchemy import Integer, Unicode, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Notification(Base):
    __tablename__ = "Notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(Unicode(50), nullable=False)
    reservation_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    resource_id: Mapped[int] = mapped_column(Integer, nullable=False)
    message: Mapped[str] = mapped_column(Unicode(500), nullable=False)
    status: Mapped[str] = mapped_column(Unicode(20), nullable=False, default="Sent")
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.sysdatetime())
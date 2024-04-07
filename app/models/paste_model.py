from app.models.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import ForeignKey


class Paste(Base):
    __tablename__ = "pastes"

    id: Mapped[str] = mapped_column(primary_key=True, unique=True, nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    username: Mapped[str] = mapped_column(ForeignKey("users.username"), nullable=True)
    role: Mapped[str] = mapped_column()
    title: Mapped[str] = mapped_column(nullable=True)
    category: Mapped[str] = mapped_column(nullable=True)
    password: Mapped[str] = mapped_column(nullable=True)
    exposure: Mapped[str] = mapped_column()
    expiration: Mapped[timedelta] = mapped_column(nullable=True)
    expires_at: Mapped[datetime] = mapped_column(nullable=True)

    user_by_id: Mapped["User"] = relationship(back_populates="pastes_by_id", foreign_keys="[Paste.user_id]")
    user_by_username: Mapped["User"] = relationship(back_populates="pastes_by_username", foreign_keys="[Paste.username]")


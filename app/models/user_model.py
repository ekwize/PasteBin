from typing import List
from app.models.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from enum import Enum


class PortalRole(str, Enum):
    ROLE_PORTAL_GUEST = "ROLE_PORTAL_GUEST"
    ROLE_PORTAL_USER = "ROLE_PORTAL_USER"
    ROLE_PORTAL_ADMIN = "ROLE_PORTAL_ADMIN"


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True, nullable=False, default=uuid4)
    role: Mapped[str] = mapped_column(nullable=False, default=PortalRole.ROLE_PORTAL_USER)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)

    pastes_by_id: Mapped[List["Paste"]] = relationship(back_populates="user_by_id", foreign_keys="[Paste.user_id]")
    pastes_by_username: Mapped[List["Paste"]] = relationship(back_populates="user_by_username", foreign_keys="[Paste.username]")



from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.chats import ChatThread


class User(TimestampMixin, Base):
    """Application user. `id` is the Supabase auth user id.

    No foreign key to `auth.users`: that schema is owned by Supabase Auth,
    not by these migrations.
    """

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    threads: Mapped[list[ChatThread]] = relationship(back_populates="user")

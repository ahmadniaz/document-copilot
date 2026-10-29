from enum import StrEnum
from typing import Any
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base, TimestampMixin, uuid_primary_key
from app.database.models.documents import DocumentChunk
from app.database.models.users import User


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class ChatThread(TimestampMixin, Base):
    __tablename__ = "chat_threads"

    id: Mapped[UUID] = uuid_primary_key()
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="threads")
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="thread",
        cascade="all, delete-orphan",
        order_by="ChatMessage.position",
    )


class ChatMessage(TimestampMixin, Base):
    __tablename__ = "chat_messages"
    __table_args__ = (
        UniqueConstraint(
            "thread_id",
            "position",
            name="uq_chat_messages_thread_id_position",
        ),
    )

    id: Mapped[UUID] = uuid_primary_key()
    thread_id: Mapped[UUID] = mapped_column(
        ForeignKey("chat_threads.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[MessageRole] = mapped_column(
        Enum(
            MessageRole,
            values_callable=lambda roles: [role.value for role in roles],
            native_enum=False,
            length=16,
        ),
        nullable=False,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    parts: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    thread: Mapped[ChatThread] = relationship(back_populates="messages")
    citations: Mapped[list["MessageCitation"]] = relationship(
        back_populates="message",
        cascade="all, delete-orphan",
        order_by="MessageCitation.position",
    )


class MessageCitation(TimestampMixin, Base):
    __tablename__ = "message_citations"
    __table_args__ = (
        UniqueConstraint(
            "message_id",
            "position",
            name="uq_message_citations_message_id_position",
        ),
    )

    id: Mapped[UUID] = uuid_primary_key()
    message_id: Mapped[UUID] = mapped_column(
        ForeignKey("chat_messages.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_chunks.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    excerpt: Mapped[str] = mapped_column(Text, nullable=False)

    message: Mapped[ChatMessage] = relationship(back_populates="citations")
    chunk: Mapped[DocumentChunk] = relationship(back_populates="citations")

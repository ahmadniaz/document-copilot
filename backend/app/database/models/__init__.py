"""SQLAlchemy models. Importing this package registers every table on `Base.metadata`."""

from app.database.models.base import Base
from app.database.models.chats import (
    ChatMessage,
    ChatThread,
    MessageCitation,
    MessageRole,
)
from app.database.models.documents import DocumentChunk, SourceDocument
from app.database.models.users import User

__all__ = [
    "Base",
    "ChatMessage",
    "ChatThread",
    "DocumentChunk",
    "MessageCitation",
    "MessageRole",
    "SourceDocument",
    "User",
]

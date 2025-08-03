# src/models.py
from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class ConversationDocument(SQLModel, table=True):
    conversation_id: int = Field(
        foreign_key="conversation.id", primary_key=True
    )
    document_id: int = Field(
        foreign_key="document.id", primary_key=True
    )


class Document(SQLModel, table=True):
    """Archivo subido por el usuario (PDF/TXT)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    chunks: List["DocumentChunk"] = Relationship(back_populates="document")
    conversations: List["Conversation"] = Relationship(
        back_populates="documents",
        link_model=ConversationDocument,
    )


class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    documents: List[Document] = Relationship(
        back_populates="conversations",
        link_model=ConversationDocument,
    )
    messages: List["Message"] = Relationship(back_populates="conversation")


class DocumentChunk(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="document.id")
    content: str

    document: Document = Relationship(back_populates="chunks")


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    role: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    conversation: Conversation = Relationship(back_populates="messages")

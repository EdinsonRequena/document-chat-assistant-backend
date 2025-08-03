from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # one-to-many
    chunks: List["DocumentChunk"] = Relationship(back_populates="document")
    conversations: List["Conversation"] = Relationship(back_populates="document")


class DocumentChunk(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="document.id")
    content: str

    document: Document = Relationship(back_populates="chunks")


class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="document.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    document: Document = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    role: str  # "user" | "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    conversation: Conversation = Relationship(back_populates="messages")

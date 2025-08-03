from datetime import datetime
from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: int
    filename: str
    uploaded_at: datetime


class MessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime


class ConversationOut(BaseModel):
    id: int
    created_at: datetime
    documents: list[DocumentOut]
    messages: list[MessageOut]

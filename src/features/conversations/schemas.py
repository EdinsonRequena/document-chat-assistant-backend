from datetime import datetime
from pydantic import BaseModel


class MessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime


class ConversationOut(BaseModel):
    id: int
    document_id: int
    created_at: datetime
    messages: list[MessageOut]

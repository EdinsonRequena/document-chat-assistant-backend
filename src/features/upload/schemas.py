from uuid import UUID
from pydantic import BaseModel


class UploadResponse(BaseModel):
    conversation_id: int
    document_id: int
    chunks: int

from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str


class ChatChunk(BaseModel):
    type: str = "chunk"
    content: str


class ChatEnd(BaseModel):
    type: str = "end"

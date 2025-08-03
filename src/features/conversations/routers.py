from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.deps import get_db_session
from models import Conversation, ConversationDocument, Document, Message
from .schemas import ConversationOut, DocumentOut, MessageOut

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/{conv_id}", response_model=ConversationOut)
async def get_conversation(
    conv_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    convo = await session.get(Conversation, conv_id)
    if convo is None:
        raise HTTPException(404, "Conversation not found")

    doc_stmt = (
        select(Document)
        .join(ConversationDocument)
        .where(ConversationDocument.conversation_id == conv_id)
    )
    docs_res = await session.execute(doc_stmt)
    docs = docs_res.scalars().all()

    msg_stmt = (
        select(Message)
        .where(Message.conversation_id == conv_id)
        .order_by(Message.created_at)
    )
    msg_res = await session.execute(msg_stmt)
    msgs = msg_res.scalars().all()

    return ConversationOut(
        id=convo.id,
        created_at=convo.created_at,
        documents=[
            DocumentOut(
                id=d.id,
                filename=d.filename,
                uploaded_at=d.created_at,
            )
            for d in docs
        ],
        messages=[
            MessageOut(
                role=m.role,
                content=m.content,
                created_at=m.created_at,
            )
            for m in msgs
        ],
    )

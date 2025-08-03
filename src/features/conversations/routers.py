from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.deps import get_db_session
from models import Conversation, Message
from .schemas import ConversationOut, MessageOut

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/{conv_id}", response_model=ConversationOut)
async def get_conversation(
    conv_id: int, session: AsyncSession = Depends(get_db_session)
):
    convo = await session.get(Conversation, conv_id)
    if not convo:
        raise HTTPException(404, "Conversation not found")

    stmt = (
        select(Message)
        .where(Message.conversation_id == conv_id)
        .order_by(Message.created_at)
    )
    result = await session.execute(stmt)
    messages = result.scalars().all()

    return ConversationOut(
        id=convo.id,
        document_id=convo.document_id,
        created_at=convo.created_at,
        messages=[
            MessageOut(
                role=m.role,
                content=m.content,
                created_at=m.created_at,
            )
            for m in messages
        ],
    )

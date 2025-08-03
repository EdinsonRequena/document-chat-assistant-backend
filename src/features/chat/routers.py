# src/features/chat/routers.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_db_session
from models import Conversation
from .services import stream_answer

router = APIRouter(prefix="/ws", tags=["chat"])


@router.websocket("/conversation/{conv_id}")
async def chat_ws(
    websocket: WebSocket,
    conv_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    await websocket.accept()
    await websocket.send_json({"type": "open"})

    convo = None
    if conv_id > 0:
        convo = await session.get(Conversation, conv_id)

    if convo is None:
        convo = Conversation()
        session.add(convo)
        await session.flush()
        conv_id = convo.id
        await websocket.send_json(
            {"type": "info", "conversation_id": conv_id}
        )

    try:
        while True:
            data = await websocket.receive_json()
            question = data.get("question")
            if not question:
                continue

            async for text in stream_answer(conv_id, question, session):
                await websocket.send_json({"type": "answer", "content": text})
            await websocket.send_json({"type": "end"})

    except WebSocketDisconnect:
        return

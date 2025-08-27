import json
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
    print("WS accepted – conv", conv_id)
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
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except ValueError:
                print("WS invalid JSON:", raw)
                continue

            print("WS received:", data)
            question = data.get("question", "").strip()
            if not question:
                continue
            async for text in stream_answer(conv_id, question, session):
                await websocket.send_json({"type": "answer", "content": text})
            await websocket.send_json({"type": "end"})

    except WebSocketDisconnect:
        return


@router.post("/conversation", status_code=201)
async def create_conversation(
    session: AsyncSession = Depends(get_db_session),
):
    """
    Crea una conversación vacía y devuelve su ID.
    """
    convo = Conversation()
    session.add(convo)
    await session.commit()
    await session.refresh(convo)
    return {"conversation_id": convo.id}

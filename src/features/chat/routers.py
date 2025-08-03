from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_db_session
from .services import stream_answer

router = APIRouter(prefix="/ws", tags=["chat"])


@router.websocket("/conversation/{conv_id}")
async def chat_ws(
    websocket: WebSocket,
    conv_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            question = data.get("question")
            if not question:
                continue

            async for answer in stream_answer(conv_id, question, session):
                await websocket.send_json(
                    {"type": "answer", "content": answer}
                )

            await websocket.send_json({"type": "end"})

    except WebSocketDisconnect:
        return

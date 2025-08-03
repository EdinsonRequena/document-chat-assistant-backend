from fastapi import APIRouter, UploadFile, File, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_db_session
from models import Conversation, ConversationDocument
from .services import extract_text, split_into_chunks, persist
from .schemas import UploadResponse

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", response_model=UploadResponse, status_code=201)
async def upload_document(
    *,
    file: UploadFile = File(...),
    conversation_id: int | None = Query(
        default=None,
        description="Si se pasa, anexará el doc a la conversación existente.",
    ),
    session: AsyncSession = Depends(get_db_session),
):
    if conversation_id is not None:
        convo = await session.get(Conversation, conversation_id)
        if convo is None:
            raise HTTPException(404, "Conversation does not exist")
    else:
        convo = Conversation()
        session.add(convo)
        await session.flush()

    raw_text = await extract_text(file)
    chunks = split_into_chunks(raw_text)
    doc_id, _ = await persist(filename=file.filename, chunks=chunks, session=session)

    link = ConversationDocument(conversation_id=convo.id, document_id=doc_id)
    session.add(link)
    await session.commit()

    return UploadResponse(
        conversation_id=convo.id,
        document_id=doc_id,
        chunks=len(chunks),
    )

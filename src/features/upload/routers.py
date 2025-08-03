from .schemas import UploadResponse
from .services import extract_text, split_into_chunks, persist
from core.deps import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, UploadFile, Depends, File


router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", response_model=UploadResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
):
    raw_text = await extract_text(file)
    chunks = split_into_chunks(raw_text)
    doc_id, convo_id = await persist(
        filename=file.filename, chunks=chunks, session=session
    )
    return UploadResponse(
        conversation_id=convo_id,
        document_id=doc_id,
        chunks=len(chunks),
    )

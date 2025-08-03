import io
from typing import List

from pypdf import PdfReader
from fastapi import UploadFile, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from langchain_text_splitters import RecursiveCharacterTextSplitter

from models import Document, DocumentChunk, Conversation


async def extract_text(file: UploadFile) -> str:
    if file.filename.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(await file.read()))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif file.filename.lower().endswith((".txt", ".md")):
        return (await file.read()).decode()
    raise HTTPException(400, "Unsupported file type")


def split_into_chunks(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_text(text)


async def persist(
    *, filename: str, chunks: List[str], session: AsyncSession
) -> tuple[int, int]:
    doc = Document(filename=filename)
    session.add(doc)
    await session.flush()  # get doc.id

    session.add_all(
        [DocumentChunk(document_id=doc.id, content=chunk) for chunk in chunks]
    )

    convo = Conversation(document_id=doc.id)
    session.add(convo)
    await session.commit()
    return doc.id, convo.id

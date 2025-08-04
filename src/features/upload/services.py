import io
from typing import List

from fastapi import UploadFile, HTTPException
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from sqlmodel.ext.asyncio.session import AsyncSession

from models import Document, DocumentChunk


async def extract_text(file: UploadFile) -> str:
    name = file.filename.lower()
    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(await file.read()))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if name.endswith((".txt", ".md")):
        return (await file.read()).decode()
    raise HTTPException(400, "Unsupported file type")


def split_into_chunks(
    text: str,
    chunk_size: int = 800,
    overlap: int = 100,
) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_text(text)


async def persist(
    *,
    filename: str,
    chunks: List[str],
    session: AsyncSession,
) -> int:
    doc = Document(filename=filename)
    session.add(doc)
    await session.flush()

    session.add_all(
        [DocumentChunk(document_id=doc.id, content=chunk) for chunk in chunks]
    )
    return doc.id

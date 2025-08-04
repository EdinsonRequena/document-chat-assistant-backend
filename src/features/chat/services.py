import traceback
from itertools import zip_longest
from typing import AsyncIterator

from openai import AsyncOpenAI, RateLimitError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.settings import settings
from models import (
    Document,
    DocumentChunk,
    ConversationDocument,
    Message,
)

client = AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = (
    "You are an assistant that answers questions about user-uploaded documents "
    "when available. If no document has been provided yet, answer generically "
    "and suggest uploading one for better context."
)


def interleave(chunks_lists: list[list[str]]) -> list[str]:
    return [c for tup in zip_longest(*chunks_lists) for c in tup if c]


async def recent_doc_ids(
    conversation_id: int,
    session: AsyncSession,
    max_docs: int = 3,
) -> list[int]:
    stmt = (
        select(ConversationDocument.document_id)
        .where(ConversationDocument.conversation_id == conversation_id)
        .order_by(ConversationDocument.document_id.desc())
        .limit(max_docs)
    )
    res = await session.execute(stmt)
    return [row[0] for row in res]


async def fetch_context(
    conversation_id: int,
    session: AsyncSession,
    chunk_budget: int = 100,
    recent_docs: int = 3,
) -> list[str]:
    doc_ids = await recent_doc_ids(conversation_id, session, recent_docs)
    if not doc_ids:
        return []

    per_doc = max(1, chunk_budget // len(doc_ids))

    full_blocks: list[str] = []
    for doc_id in doc_ids:
        title_stmt = select(Document.filename).where(Document.id == doc_id)
        filename = (await session.scalar(title_stmt)) or f"Doc {doc_id}"

        chunks_stmt = (
            select(DocumentChunk.content)
            .where(DocumentChunk.document_id == doc_id)
            .order_by(DocumentChunk.id)
            .limit(per_doc)
        )
        chunks = (await session.scalars(chunks_stmt)).all()

        full_blocks.append(f"### {filename}\n" + "\n".join(chunks))

    joined = "\n\n".join(full_blocks)
    return joined.splitlines()[:chunk_budget]


async def stream_answer(
    conversation_id: int,
    question: str,
    session: AsyncSession,
) -> AsyncIterator[str]:
    print("-> stream_answer START")
    context_chunks = await fetch_context(conversation_id, session)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    if context_chunks:
        messages.append(
            {"role": "system", "content": "\n\n".join(context_chunks)})
    messages.append({"role": "user", "content": question})

    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
            stream=False,
        )
        full_answer: str = response.choices[0].message.content
        print("-> stream_answer GOT:", full_answer[:60])
        yield full_answer

    except Exception as exc:
        traceback.print_exc()
        yield "Error interno, inténtalo luego."
        full_answer = "internal error"

    except RateLimitError:
        full_answer = (
            "Lo siento, la API está saturada. Intenta nuevamente en unos minutos."
        )
        yield full_answer

    session.add_all(
        [
            Message(
                conversation_id=conversation_id,
                role="user",
                content=question
            ),
            Message(
                conversation_id=conversation_id,
                role="assistant",
                content=full_answer
            ),
        ]
    )
    await session.commit()

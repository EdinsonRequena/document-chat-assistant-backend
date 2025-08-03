from typing import AsyncIterator, List
from openai import AsyncOpenAI, RateLimitError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.settings import settings
from models import (
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


async def fetch_context(
    conversation_id: int,
    session: AsyncSession,
    limit: int = 15
) -> List[str]:
    stmt = (
        select(DocumentChunk.content)
        .join(DocumentChunk.document)
        .join(ConversationDocument)
        .where(ConversationDocument.conversation_id == conversation_id)
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def stream_answer(
    conversation_id: int,
    question: str,
    session: AsyncSession
) -> AsyncIterator[str]:
    context_chunks = await fetch_context(conversation_id, session)

    if context_chunks:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": "\n\n".join(context_chunks[:5])},
            {"role": "user", "content": question},
        ]
    else:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]

    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=False,
        )
        full_answer: str = response.choices[0].message.content
        yield full_answer

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

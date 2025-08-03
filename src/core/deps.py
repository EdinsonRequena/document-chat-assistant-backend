from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_session


async def get_db_session(session: AsyncSession = Depends(get_session)):
    yield session

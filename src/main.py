from fastapi import FastAPI

from core.db import init_db
from features.chat.routers import router as chat_router
from features.upload.routers import router as upload_router
from features.conversations.routers import router as conversations_router

app = FastAPI(title="Document Chat Assistant Backend")

app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(conversations_router)


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


@app.get("/healthcheck", tags=["meta"])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}

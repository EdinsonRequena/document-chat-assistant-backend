from fastapi import FastAPI

from core.db import init_db
from features.chat.routers import router as chat_router
from features.upload.routers import router as upload_router


app = FastAPI(title="Document Chat Assistant Backend")

app.include_router(chat_router)
app.include_router(upload_router)


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()  # crea tablas si no existen (dev only)


@app.get("/healthcheck", tags=["meta"])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}

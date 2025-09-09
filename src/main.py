from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.db import init_db
from core.settings import settings
from features.chat.routers import router as chat_router
from features.upload.routers import router as upload_router
from features.conversations.routers import router as conversations_router

app = FastAPI(title="Document Chat Assistant Backend")

allow_all = settings.allowed_origins.strip() == "*"
origins = ["*"] if allow_all else [o.strip()
                                   for o in settings.allowed_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(conversations_router)


@app.get("/", tags=["meta"])
async def root():
    return {"status": "ok", "service": "document-chat-assistant"}


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


@app.get("/healthz", tags=["meta"])
def healthz() -> dict[str, str]:
    return {"ok": "true"}


@app.get("/healthcheck", tags=["meta"])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}

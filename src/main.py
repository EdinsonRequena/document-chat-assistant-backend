from fastapi import FastAPI

from core.db import init_db

app = FastAPI(title="Document Chat Assistant Backend")


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()  # crea tablas si no existen (dev only)


@app.get("/healthcheck", tags=["meta"])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
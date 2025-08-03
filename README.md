# Document-Chat-Assistant • Backend (FastAPI + Postgres)

API que permite:
1. Crear un chat en blanco, o al primer mensaje.
2. Subir uno o varios PDF/TXT a la misma conversación.
3. Preguntar en tiempo real vía WebSocket; la IA responde con o sin contexto.
4. Rehidratar historial completo.

---

## Tabla de contenidos
1. [Demo rápida](#demo-rápida)
2. [Requisitos](#requisitos)
3. [Arranque local](#arranque-local)
4. [Arranque con Docker](#arranque-con-docker)
5. [Variables de entorno](#variables-de-entorno)
6. [Endpoints](#endpoints)
7. [Estructura de carpetas](#estructura-de-carpetas)
8. [TODO/Futuro](#todofuturo)

---

## Demo rápida

```bash
# 1. Levanta servicios
docker compose up --build

# 2. Sube un documento
curl -F file=@doc.pdf http://localhost:8000/upload
# → { "conversation_id": 1, "document_id": 1, "chunks": 42 }

# 3. Abre un WebSocket (ej. wscat)
wscat -c ws://localhost:8000/ws/conversation/1
> {"question":"¿De qué trata el documento?"}
< {"type":"answer","content":"Es una factura de..."}
< {"type":"end"}
```

## Requisitos
	•	Python ≥ 3.11 (si corres sin Docker)
	•	PostgreSQL 15 (o contenedor oficial)
	•	Cuenta OpenAI (clave sk-... con acceso a gpt-3.5-turbo)
	•	pipenv para entorno local

## Arranque local
```bash
# Clona
git clone https://github.com/edinsonrequena/document-chat-assistant-backend.git
cd document-chat-assistant-backend

pipenv install --dev
pipenv shell

# Variables
cp .env           # edita OPENAI_API_KEY y DATABASE_URL

# DB local
createdb document_chat

# Run
uvicorn src.main:app --reload --app-dir src
```


## Arranque con Docker
```bash
export OPENAI_API_KEY=sk-...
docker compose up --build
# FastAPI       → http://localhost:8000/docs
# Postgres      → localhost:5432 (user/pass: postgres)
# WebSocket     → ws://localhost:8000/ws/conversation/{id}
```

## Variables de entorno
| Variable            |  Ejemplo                                     | Descripción |
|---------------------|---------------------------------------------|-------------|
| OPENAI_API_KEY      | sk-...                                      | Clave de API de OpenAI para GPT-3.5-turbo |
| DATABASE_URL        | postgresql://postgres:postgres@localhost:5432/document_chat | URL de conexión a la base de datos PostgreSQL |


## Endpoints
| Método | Endpoint                          | Descripción |
|--------|-----------------------------------|-------------|
| POST   | /upload                           | Sube un archivo PDF/TXT a una conversación. |
| GET    | /conversation/{id}                | Obtiene el historial de mensajes de una conversación. |
| WS   | /ws/conversation/{id}          | Chat en tiempo real• id = 0 crea conversación al vuelo. |
| GET   | /docs            | Swagger UI |

## Protocolo WS
Cliente → Servidor
```json
{"question": "¿Qué es el documento?"}
```
Servidor → Cliente
```json
{"type": "answer", "content": "El documento es una factura de..."}
{"type": "end"}  # Indica que no hay más respuestas
```

## Estructura de carpetas
```
src/
 ├ core/            # settings, DB engine, deps
 ├ features/
 │   ├ upload/      # POST /upload
 │   ├ chat/        # WS /conversation
 │   └ conversations/  # GET /conversations/{id}
 ├ models.py        # SQLModel ORM (many-to-many)
 └ main.py          # FastAPI bootstrap
```

## TODO/Futuro
	•	Embeddings con PGVector para chunks relevantes.
	•	Alembic migrations automáticas.
	•	Tests de integración (pytest-asyncio + pytest-docker).
	•	Rate-limiter y backoff ante errores 429 de OpenAI.
	•	Observabilidad: Prometheus metrics + structured logging.

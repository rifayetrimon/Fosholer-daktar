# ফসলের ডাক্তার — Fosholer Daktar

An AI-powered crop disease detection and advisory backend for Bangladeshi farmers.

**Target customer:** Small and medium-scale farmers in rural Bangladesh who cannot easily access agricultural extension officers. The system lets a farmer photograph a diseased leaf, get an instant AI diagnosis, and receive treatment advice in simple language — all via a mobile app or web interface.

**Problem solved:** Crop disease causes 20–40% yield loss for Bangladeshi farmers every year. Early detection and correct treatment cuts that loss. No affordable, offline-ready, Bangla-aware tool exists for smallholders.

**Business model:** SaaS subscription for agro-service companies and NGOs (per-district license), or freemium direct-to-farmer with premium disease-knowledge subscriptions.

---

## Features

- Leaf image upload → ML model classifies the disease → confidence score returned
- RAG knowledge base: upload PDF disease guides → auto-chunk, embed, store in pgvector
- LLM chat agent (Gemini) answers farming questions using retrieved knowledge chunks
- Tool-calling: agent queries the scan history and knowledge base in real time
- MCP server: exposes tools, resources and prompts over HTTP and stdio
- JWT authentication with admin and user roles
- Full CRUD for crops and disease scans

---

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI, Python 3.12 |
| Database | PostgreSQL 16 + pgvector |
| ORM / Migrations | SQLAlchemy (async) + Alembic |
| LLM | Google Gemini 2.5 Flash |
| Embeddings | Gemini Embedding-001 (768-dim) |
| ML Classifier | PyTorch + HuggingFace Transformers |
| Auth | JWT (python-jose) + argon2 (passlib) |
| MCP | mcp[cli] — HTTP + stdio transports |
| Package manager | uv |
| Container | Docker + docker-compose |

---

## Setup

### 1. Clone

```bash
git clone <repo-url>
cd fosholer-daktar
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — fill in SECRET_KEY, GEMINI_API_KEY, and DB credentials
```

### 3. Run with Docker (recommended)

```bash
docker compose up --build
```

Then run migrations and seed inside the running container:

```bash
docker compose exec api uv run alembic upgrade head
docker compose exec api uv run python scripts/seed.py
```

The API is now live at `http://localhost:8000`. Swagger docs: `http://localhost:8000/docs`

### 4. Run locally (without Docker)

```bash
uv sync
uv run alembic upgrade head
uv run python scripts/seed.py
uv run uvicorn app.main:app --reload
```

---

## Seed credentials

| Role | Email | Password |
|---|---|---|
| Admin | admin@gmail.com | rimon123 |

---

## API Endpoints

### Auth

```
POST /api/v1/auth/register
Body: { "email": "...", "full_name": "...", "password": "..." }

POST /api/v1/auth/login
Body: { "email": "...", "password": "..." }
Response: { "access_token": "...", "token_type": "bearer" }

GET /api/v1/auth/me
Header: Authorization: Bearer <token>
```

### Crops (admin write, all read)

```
POST   /api/v1/crops/          — create crop (admin)
GET    /api/v1/crops/          — list crops (optional ?search=rice)
GET    /api/v1/crops/{id}      — get one crop
PATCH  /api/v1/crops/{id}      — update crop (admin)
DELETE /api/v1/crops/{id}      — delete crop (admin)
```

### Disease Scans

```
POST   /api/v1/scans/          — upload leaf image, get diagnosis
GET    /api/v1/scans/          — list scans (?crop_name= &disease_name=)
GET    /api/v1/scans/{id}      — get one scan
PATCH  /api/v1/scans/{id}      — update notes/treatment
DELETE /api/v1/scans/{id}      — delete scan
```

### Knowledge Base (RAG)

```
POST /api/v1/knowledge/                — add single knowledge entry (admin)
POST /api/v1/knowledge/upload-document — upload PDF/TXT, auto-chunk and embed (admin)
GET  /api/v1/knowledge/                — list knowledge (?disease_name=)
```

### Chat

```
POST /api/v1/chat/
Body: {
  "message": "আমার ধান গাছের পাতায় বাদামী দাগ হচ্ছে",
  "history": []
}
```

### MCP

```
HTTP transport:  POST /mcp
stdio transport: uv run python -m app.mcp.stdio
```

### Health

```
GET /health      — { "status": "ok", "app": "Fosholer Daktar" }
GET /health/db   — database connection + pgvector status
```

---

## Ingest a knowledge document

```bash
curl -X POST http://localhost:8000/api/v1/knowledge/upload-document \
  -H "Authorization: Bearer <admin-token>" \
  -F "file=@rice_blast_guide.pdf" \
  -F "disease_name=Rice Blast" \
  -F "crop_name=Rice"
```

---

## Links

- **Git repo:** _add link here_
- **Live Swagger:** _add Render link here_
- **Demo video:** _add Google Drive link here_
# Fosholer-daktar

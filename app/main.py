import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions.handler import register_exception_handlers
from app.db.session import session_manager
from app.mcp.server import mcp_asgi_app

settings = get_settings()
logger = logging.getLogger("uvicorn.error")


async def _repair_schema() -> None:
    """Idempotent fix for columns/tables that alembic may have stamped but never created."""
    stmts = [
        # disease_scans missing columns (migration 0004 may have been stamped)
        "ALTER TABLE disease_scans ADD COLUMN IF NOT EXISTS confidence FLOAT NOT NULL DEFAULT 0.0",
        "ALTER TABLE disease_scans ADD COLUMN IF NOT EXISTS treatment_advice TEXT",
        "ALTER TABLE disease_scans ADD COLUMN IF NOT EXISTS notes TEXT",
        # conversations table (migration 0005 may have been stamped)
        """CREATE TABLE IF NOT EXISTS conversations (
            id         UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id    UUID         NOT NULL REFERENCES users(id),
            title      VARCHAR(100) NOT NULL,
            messages   JSONB        NOT NULL DEFAULT '[]',
            created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
        )""",
        "CREATE INDEX IF NOT EXISTS ix_conversations_user_id    ON conversations(user_id)",
        "CREATE INDEX IF NOT EXISTS ix_conversations_updated_at ON conversations(updated_at)",
    ]
    for stmt in stmts:
        try:
            async with session_manager.session() as db:
                await db.execute(text(stmt))
            logger.info("Schema repair OK: %s", stmt[:60])
        except Exception as exc:
            logger.error("Schema repair FAILED for: %s — %s", stmt[:60], exc)


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with session_manager.run():
        await _repair_schema()
        yield


app = FastAPI(
    title=settings.APP_NAME,
    description="AI crop disease detection and advisory for Bangladeshi farmers",
    version="1.0.0",
    lifespan=lifespan,
)

register_exception_handlers(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
app.mount("/mcp", mcp_asgi_app)


@app.get("/")
async def root():
    return {"message": "Fosholer Daktar API — ফসলের ডাক্তার", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

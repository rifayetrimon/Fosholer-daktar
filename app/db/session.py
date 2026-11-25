from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()


class DatabaseSessionManager:
    def __init__(self):
        self._engine = None
        self._session_maker = None

    def init(self, url: str):
        connect_args = {"statement_cache_size": 0}
        if settings.DB_SSL:
            connect_args["ssl"] = True
        self._engine = create_async_engine(url, echo=settings.DEBUG, connect_args=connect_args)
        self._session_maker = async_sessionmaker(self._engine, expire_on_commit=False)

    @asynccontextmanager
    async def run(self):
        self.init(settings.DATABASE_URL.render_as_string(hide_password=False))
        yield
        await self.close()

    async def close(self):
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_maker = None

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        if not self._session_maker:
            raise RuntimeError("DatabaseSessionManager not initialized. Call init() first.")
        async with self._session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

session_manager = DatabaseSessionManager()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with session_manager.session() as session:
        yield session

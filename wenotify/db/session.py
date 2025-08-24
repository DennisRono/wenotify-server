import asyncio
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_scoped_session
from typing import AsyncGenerator
from wenotify.core.config import settings
from wenotify.core.logging import logger

logger.info(settings.SQLALCHEMY_DATABASE_URI)

async_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    pool_size=32,
    max_overflow=64,
    connect_args={"statement_cache_size": 0},
    future=True,
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

async_session_factory = async_scoped_session(
    AsyncSessionLocal,
    scopefunc=asyncio.current_task,
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

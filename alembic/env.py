from logging.config import fileConfig
import sys
from pathlib import Path
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from wenotify.core.logging import logger
 
project_root = Path(__file__).parents[1]
sys.path.append(str(project_root))

 
from wenotify.core.config import settings
from wenotify.models import Base   

logger.info(settings.SQLALCHEMY_DATABASE_URI)
 
config = context.config
 
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
 
target_metadata = Base.metadata   

async_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    pool_size=32,
    max_overflow=64,
    connect_args={"statement_cache_size": 0},
)


def run_migrations_offline() -> None:
    context.configure(
        url=settings.SQLALCHEMY_DATABASE_URI,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    async with async_engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await async_engine.dispose()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

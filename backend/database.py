from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import settings

engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_session():
    async with async_session_factory() as session:
        yield session


async def init_db():
    from models import Patient  # noqa: F401 — registers model with Base
    from sqlalchemy import text
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Create message_store explicitly so index is ready before first request.
        # SQLChatMessageHistory would create this lazily; we do it here to own the index.
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS message_store (
                id      SERIAL PRIMARY KEY,
                session_id TEXT,
                message TEXT
            )
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_message_store_session
            ON message_store (session_id, id DESC)
        """))

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import OperationalError, DisconnectionError
from app.config import settings

DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=300,        # Recycle toutes les 5 min (évite connexions stales)
    pool_pre_ping=True,
    pool_use_lifo=True,      # Préfère les connexions récentes (plus chaudes)
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except (OperationalError, DisconnectionError):
            await session.rollback()
            raise
        except Exception:
            await session.rollback()
            raise
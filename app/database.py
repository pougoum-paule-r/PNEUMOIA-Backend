from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,        # connexions persistantes
    max_overflow=10,    # connexions supplémentaires max (total 15)
    pool_timeout=30,    # secondes d'attente avant TimeoutError
    pool_recycle=1800,  # recycler après 30 min (évite les connexions mortes)
    pool_pre_ping=True, # tester la connexion avant usage
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
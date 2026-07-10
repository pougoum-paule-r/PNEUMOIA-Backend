import asyncio
import subprocess
from sqlalchemy import text
from app.database import engine, Base
import app.models  # registers all models with Base


async def main():
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT to_regclass('public.alembic_version')")
        )
        alembic_exists = result.scalar() is not None

    if not alembic_exists:
        print("[docker_init] Fresh database — creating all tables from models...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("[docker_init] Tables created. Stamping Alembic to head...")
        subprocess.run(["alembic", "stamp", "head"], check=True)
        print("[docker_init] Ready.")
    else:
        print("[docker_init] Existing database — running pending migrations...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("[docker_init] Ready.")


asyncio.run(main())

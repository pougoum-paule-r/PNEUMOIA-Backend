import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.main import app
from app.database import engine
from app.models.admin import Admin
from app.core.security import create_access_token

ADMIN_EMAIL = "adminpneumoia@gmail.com"
ADMIN_PHONE = "+237656544163"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    """Client HTTP partagé pour toute la session (startup FastAPI exécuté une seule fois)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture(scope="session")
async def admin_token(client):
    """Token JWT admin valide, généré à partir de l'ID réel en BDD."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        result = await db.execute(select(Admin).where(Admin.email == ADMIN_EMAIL))
        admin = result.scalar_one()
    return create_access_token({
        "sub":   str(admin.id),
        "email": admin.email,
        "phone": admin.phone or ADMIN_PHONE,
        "role":  "admin",
    })


@pytest.fixture(scope="session")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

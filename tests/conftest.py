import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.main import app
from app.database import engine
from app.models.admin import Admin
from app.models.medecin import Medecin
from app.models.aide_soignant import AideSoignant
from app.core.security import create_access_token, hash_password

ADMIN_EMAIL = "adminpneumoia@gmail.com"
ADMIN_PHONE = "+237656616801"

MEDECIN_EMAIL = "docteur.test@pneumoia.com"
MEDECIN_PASSWORD = "Test1234!"


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


@pytest.fixture(scope="session")
async def medecin_token(client):
    """Crée un médecin de test validé en BDD et retourne son token JWT."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        result = await db.execute(select(Medecin).where(Medecin.email == MEDECIN_EMAIL))
        medecin = result.scalar_one_or_none()
        if not medecin:
            medecin = Medecin(
                nom           = "TEST",
                prenom        = "Docteur",
                email         = MEDECIN_EMAIL,
                password_hash = hash_password(MEDECIN_PASSWORD),
                specialite    = "Pneumologie",
                statut        = "valide",
            )
            db.add(medecin)
            await db.commit()
            await db.refresh(medecin)
    return create_access_token({
        "sub":   str(medecin.id),
        "email": medecin.email,
        "role":  "medecin",
    })


@pytest.fixture(scope="session")
def medecin_headers(medecin_token):
    return {"Authorization": f"Bearer {medecin_token}"}


AIDE_EMAIL    = "aide.test@pneumoia.com"
AIDE_PASSWORD = "Aide1234!"


@pytest.fixture(scope="session")
async def aide_token(medecin_token):
    """Crée un aide soignant de test actif lié au médecin de test."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        # Récupérer le médecin de test
        medecin = (await db.execute(
            select(Medecin).where(Medecin.email == MEDECIN_EMAIL)
        )).scalar_one()

        # Créer l'aide soignant s'il n'existe pas
        aide = (await db.execute(
            select(AideSoignant).where(AideSoignant.email == AIDE_EMAIL)
        )).scalar_one_or_none()

        if not aide:
            aide = AideSoignant(
                medecin_id    = medecin.id,
                nom           = "AIDE",
                prenom        = "Test",
                email         = AIDE_EMAIL,
                password_hash = hash_password(AIDE_PASSWORD),
                statut        = "actif",
            )
            db.add(aide)
            await db.commit()
            await db.refresh(aide)

    return create_access_token({
        "sub":   str(aide.id),
        "email": aide.email,
        "role":  "aide_soignant",
    })


@pytest.fixture(scope="session")
def aide_headers(aide_token):
    return {"Authorization": f"Bearer {aide_token}"}

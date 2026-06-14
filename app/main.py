from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import settings
from app.database import engine, Base
from app.init_db import seed_admin

from app.routers import auth, admin, diagnostics, patients, consultations, aides, ressources
from app.routers.medecins    import router_medecins
from app.routers.communautes import router_communautes
from app.routers.aides       import router as router_aides
from app.routers.monitoring  import router as router_monitoring


app = FastAPI(title="PneumoIA API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_upload_dir = Path(settings.UPLOAD_DIR)
_upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(_upload_dir)), name="uploads")

app.include_router(auth.router,        prefix="/api/v1")   # /auth → /api/v1/auth
app.include_router(admin.router)                            # has own full prefix
app.include_router(diagnostics.router, prefix="/api/v1")   # /diagnostic → /api/v1/diagnostic
app.include_router(patients.router)                         # already /api/v1/patients
app.include_router(consultations.router)                    # already /api/v1/consultations
app.include_router(router_medecins)
app.include_router(router_communautes)
app.include_router(router_aides,       prefix="/api/v1")
app.include_router(ressources.router,  prefix="/api/v1")   # /ressources → /api/v1/ressources
app.include_router(router_monitoring)                       # already /api/v1/monitoring


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as db:
        await seed_admin(db)


@app.get("/")
def root():
    return {"status": "PneumoIA API is running"}

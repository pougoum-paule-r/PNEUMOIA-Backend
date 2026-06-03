from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.routers import auth, admin, diagnostics, patients, consultations
from app.config import settings
from app.database import engine, Base
from app.init_db import seed_admin

app = FastAPI(title="PneumoIA API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_upload_dir = Path(settings.UPLOAD_DIR)
_upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(_upload_dir)), name="uploads")

app.include_router(auth.router,          prefix="/api/v1")
app.include_router(admin.router) 
app.include_router(diagnostics.router,   prefix="/api/v1")
app.include_router(patients.router,      prefix="/api/v1")
app.include_router(consultations.router, prefix="/api/v1")

@app.on_event("startup")
async def startup():
    # 1. Créer toutes les tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Créer l'admin par défaut
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as db:
        await seed_admin(db)

@app.get("/")
def root():
    return {"status": "PneumoIA API is running"}
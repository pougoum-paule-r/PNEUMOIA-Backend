from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import auth, admin, diagnostics, patients, consultations
from app.routers.medecins    import router_medecins
from app.routers.communautes import router_communautes
from app.config import settings

app = FastAPI(title="PneumoIA API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Fichiers statiques : uploads photos/documents ─────────────────
_upload_dir = Path(settings.UPLOAD_DIR)
_upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(_upload_dir)), name="uploads")

# ── Routeurs ──────────────────────────────────────────────────────
app.include_router(auth.router,  prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"status": "PneumoIA API is running"}


app.include_router(diagnostics.router, prefix="/api/v1")
app.include_router(patients.router)
app.include_router(consultations.router)
app.include_router(router_medecins)
app.include_router(router_communautes)
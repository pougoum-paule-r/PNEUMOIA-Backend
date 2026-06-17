from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import settings
from app.database import engine, Base
from app.init_db import seed_admin

from app.routers import auth, admin, diagnostics, patients, consultations, ressources
from app.routers.medecins         import router_medecins
from app.routers.communautes      import router_communautes
from app.routers.aides            import router as router_aides
from app.routers.monitoring       import router as router_monitoring
from app.routers.messages_equipe  import router as router_messages_equipe
from app.routers.publications     import router as router_publications
from app.routers.questions_admin  import router as router_questions_admin
from app.routers.notifications    import router as router_notifications


app = FastAPI(title="PneumoIA API", version="1.0.0")


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    champs_manquants = []
    for err in exc.errors():
        loc = " → ".join(str(x) for x in err["loc"] if x != "body")
        champs_manquants.append(f"{loc} : {err['msg']}")
    message = "Champs invalides : " + " | ".join(champs_manquants)
    print(f"[422] {request.url.path} — {message}")
    return JSONResponse(status_code=422, content={"detail": message})


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
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
app.include_router(router_aides,             prefix="/api/v1")
app.include_router(ressources.router,        prefix="/api/v1")
app.include_router(router_monitoring)
app.include_router(router_messages_equipe,   prefix="/api/v1")   # /equipe → /api/v1/equipe
app.include_router(router_publications,      prefix="/api/v1")   # /publications → /api/v1/publications
app.include_router(router_questions_admin,  prefix="/api/v1")   # /questions-admin → /api/v1/questions-admin
app.include_router(router_notifications,   prefix="/api/v1")   # /notifications   → /api/v1/notifications


@app.on_event("startup")
async def startup():
    from sqlalchemy import text
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        for sql in [
            "ALTER TABLE aides_soignants ADD COLUMN IF NOT EXISTS preferences JSONB DEFAULT '{}'",
            "ALTER TABLE medecins        ADD COLUMN IF NOT EXISTS preferences JSONB DEFAULT '{}'",
        ]:
            await conn.execute(text(sql))

    # ALTER TYPE ADD VALUE doit tourner en dehors d'une transaction (autocommit)
    async with engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(text("""
            DO $$ BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_enum
                    WHERE enumlabel = 'aide_soignant'
                    AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'type_destinataire')
                ) THEN
                    ALTER TYPE type_destinataire ADD VALUE 'aide_soignant';
                END IF;
            END $$
        """))
        await conn.execute(text("""
            DO $$ BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_enum
                    WHERE enumlabel = 'corbeille'
                    AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'statut_medecin')
                ) THEN
                    ALTER TYPE statut_medecin ADD VALUE 'corbeille';
                END IF;
            END $$
        """))

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as db:
        await seed_admin(db)


@app.get("/")
def root():
    return {"status": "PneumoIA API is running"}

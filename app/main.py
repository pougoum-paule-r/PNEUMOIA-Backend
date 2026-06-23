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

try:
    import asyncpg as _asyncpg
    _ASYNCPG_AVAILABLE = True
except ImportError:
    _ASYNCPG_AVAILABLE = False

from app.routers import auth, admin, diagnostics, patients, consultations, ressources
from app.routers.medecins         import router_medecins
from app.routers.communautes      import router_communautes
from app.routers.aides            import router as router_aides
from app.routers.monitoring       import router as router_monitoring
from app.routers.messages_equipe  import router as router_messages_equipe
from app.routers.publications     import router as router_publications
from app.routers.questions_admin  import router as router_questions_admin
from app.routers.notifications    import router as router_notifications
from app.routers.faq_public       import router as router_faq_public


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


@app.exception_handler(Exception)
async def global_error_handler(request: Request, exc: Exception):
    """Attrape toutes les exceptions non gérées et les logue dans le journal d'audit."""
    from starlette.exceptions import HTTPException as StarletteHTTPException
    from fastapi.exceptions import HTTPException as FastAPIHTTPException

    # Ne pas intercepter les erreurs HTTP intentionnelles (401, 403, 404…)
    if isinstance(exc, (StarletteHTTPException, FastAPIHTTPException)):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    import traceback, logging
    logging.getLogger(__name__).error(
        "Erreur système non gérée [%s %s]: %s",
        request.method, request.url.path, traceback.format_exc()
    )

    try:
        from app.models.audit_log import AuditLog
        session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with session_factory() as db:
            db.add(AuditLog(
                action  = "erreur_systeme",
                details = {
                    "type":    type(exc).__name__,
                    "message": str(exc)[:500],
                    "url":     request.url.path,
                    "method":  request.method,
                },
            ))
            await db.commit()
    except Exception:
        pass

    return JSONResponse(status_code=500, content={"detail": "Erreur interne du serveur"})
if _ASYNCPG_AVAILABLE:
    @app.exception_handler(_asyncpg.exceptions.ConnectionDoesNotExistError)
    async def _asyncpg_conn_lost(request: Request, exc: Exception):
        await engine.dispose()
        return JSONResponse(
            status_code=503,
            content={"detail": "Base de données momentanément indisponible — réessayez"},
        )

    @app.exception_handler(_asyncpg.exceptions.TooManyConnectionsError)
    async def _asyncpg_too_many(request: Request, exc: Exception):
        await engine.dispose()
        return JSONResponse(
            status_code=503,
            content={"detail": "Trop de connexions actives — réessayez dans quelques secondes"},
        )

    @app.exception_handler(_asyncpg.exceptions.PostgresConnectionError)
    async def _asyncpg_pg_conn(request: Request, exc: Exception):
        await engine.dispose()
        return JSONResponse(
            status_code=503,
            content={"detail": "Connexion PostgreSQL perdue — réessayez"},
        )


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
        "null",
    ],
    allow_origin_regex=r"(http://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.\d+\.\d+\.\d+):\d+|https://.*\.ngrok(-free)?\.app|https://.*\.ngrok\.io)",
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
app.include_router(router_faq_public,      prefix="/api/v1")   # /faq-public      → /api/v1/faq-public  (sans auth)


@app.on_event("startup")
async def startup():
    from sqlalchemy import text

    # 1. AUTOCOMMIT en premier — CREATE TYPE et ALTER TYPE ADD VALUE
    #    doivent tourner hors transaction et avant les ADD COLUMN qui les référencent
    async with engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        for sql in [
            """DO $$ BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'auteur_type_commentaire') THEN
                    CREATE TYPE auteur_type_commentaire AS ENUM ('medecin', 'aide_soignant');
                END IF;
            END $$""",
            """DO $$ BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_enum
                    WHERE enumlabel = 'aide_soignant'
                    AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'type_destinataire')
                ) THEN
                    ALTER TYPE type_destinataire ADD VALUE 'aide_soignant';
                END IF;
            END $$""",
            """DO $$ BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_enum
                    WHERE enumlabel = 'corbeille'
                    AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'statut_medecin')
                ) THEN
                    ALTER TYPE statut_medecin ADD VALUE 'corbeille';
                END IF;
            END $$""",
        ]:
            await conn.execute(text(sql))

    # 2. Transaction — création des tables + colonnes manquantes
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        for sql in [
            "ALTER TABLE aides_soignants ADD COLUMN IF NOT EXISTS preferences    JSONB    DEFAULT '{}'",
            "ALTER TABLE medecins        ADD COLUMN IF NOT EXISTS preferences    JSONB    DEFAULT '{}'",
            "ALTER TABLE publications    ALTER COLUMN communaute_id DROP NOT NULL",
            "ALTER TABLE commentaires    ADD COLUMN IF NOT EXISTS parent_id      VARCHAR(15) REFERENCES commentaires(id)    ON DELETE CASCADE",
            "ALTER TABLE commentaires    ADD COLUMN IF NOT EXISTS auteur_aide_id VARCHAR(15) REFERENCES aides_soignants(id) ON DELETE RESTRICT",
            "ALTER TABLE commentaires    ADD COLUMN IF NOT EXISTS auteur_type    auteur_type_commentaire NOT NULL DEFAULT 'medecin'",
            "ALTER TABLE commentaires    ADD COLUMN IF NOT EXISTS likes_count    INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE publications    ADD COLUMN IF NOT EXISTS ressource_id   VARCHAR(30) REFERENCES ressources_medicales(id) ON DELETE SET NULL",
            # Relier les anciennes Publications aux ressources (backfill)
            """UPDATE publications p
               SET ressource_id = r.id
               FROM ressources_medicales r
               WHERE p.ressource_id IS NULL
                 AND p.type = 'cas_clinique'
                 AND p.auteur_id = r.medecin_id
                 AND p.titre    = r.titre""",
            # Supprimer les publications orphelines (ressource dépubliée ou supprimée)
            """DELETE FROM publications
               WHERE type = 'cas_clinique'
                 AND ressource_id IS NOT NULL
                 AND ressource_id NOT IN (
                     SELECT id FROM ressources_medicales WHERE publie = TRUE
                 )""",
            # Supprimer les publications orphelines sans lien (vieux enregistrements non rétroliés)
            """DELETE FROM publications p
               WHERE p.type = 'cas_clinique'
                 AND p.ressource_id IS NULL
                 AND NOT EXISTS (
                     SELECT 1 FROM ressources_medicales r
                     WHERE r.medecin_id = p.auteur_id
                       AND r.titre      = p.titre
                       AND r.publie     = TRUE
                 )""",
        ]:
            await conn.execute(text(sql))

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as db:
        await seed_admin(db)

    # Nettoyer les chemins photo_profil orphelins (fichier absent sur disque)
    from pathlib import Path as _Ph
    from app.models.medecin import Medecin
    from sqlalchemy import select as _sel
    async with async_session() as db:
        _res = await db.execute(_sel(Medecin).where(Medecin.photo_url != None))
        _cleaned = 0
        for _m in _res.scalars().all():
            if _m.photo_url and not _Ph(_m.photo_url).exists():
                _m.photo_url = None
                _cleaned += 1
        if _cleaned:
            await db.commit()
            import logging as _lg
            _lg.getLogger(__name__).info("Nettoyage : %d chemin(s) photo orphelin(s) effacé(s)", _cleaned)


@app.get("/")
def root():
    return {"status": "PneumoIA API is running"}

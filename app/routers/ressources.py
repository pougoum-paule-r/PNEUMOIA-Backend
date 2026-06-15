# app/routers/ressources.py
import os, shutil, random, string
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from jose import JWTError

from app.database   import get_db
from app.models.ressource import RessourceMedicale, generate_ressource_id
from app.models.medecin   import Medecin
from app.core.security    import decode_token
from app.config           import settings

router = APIRouter(prefix="/ressources", tags=["Bibliothèque médicale"])
bearer = HTTPBearer(auto_error=False)

UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "ressources"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

PDF_MAX_SIZE = 20 * 1024 * 1024  # 20 Mo

PATHOLOGIES_VALIDES = [
    "Pneumonie", "Tuberculose", "Asthme", "BPCO",
    "Cancer pulmonaire", "Bronchite", "COVID-19",
    "Pneumothorax", "Fibrose pulmonaire", "Autre"
]

NIVEAUX_VALIDES = [
    "3ème année", "4ème année", "5ème année",
    "6ème année", "Interne", "Résident", "Spécialiste"
]

# ── Helper JWT ────────────────────────────────────────────────────
async def get_medecin_connecte(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db)
) -> Medecin:
    if not credentials:
        raise HTTPException(401, "Token requis")
    try:
        payload    = decode_token(credentials.credentials)
        medecin_id = payload.get("sub")
        role       = payload.get("role")
        if role != "medecin":
            raise HTTPException(403, "Accès réservé aux médecins")
    except JWTError:
        raise HTTPException(401, "Token invalide")

    result  = await db.execute(select(Medecin).where(Medecin.id == medecin_id))
    medecin = result.scalar_one_or_none()
    if not medecin:
        raise HTTPException(404, "Médecin introuvable")
    return medecin


# ══════════════════════════════════════════════════════════════════
# ROUTES PUBLIQUES — aucun token requis
# ══════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────
# GET /ressources  — liste publique (ressources publiées uniquement)
# ─────────────────────────────────────────────────────────────────
@router.get("")
async def lister_ressources(
    pathologie: Optional[str] = Query(None),
    niveau:     Optional[str] = Query(None),
    recherche:  Optional[str] = Query(None),
    page:       int           = Query(1, ge=1),
    limite:     int           = Query(9, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    base_filter = [RessourceMedicale.publie == True]
    if pathologie:
        base_filter.append(RessourceMedicale.pathologie == pathologie)
    if niveau:
        base_filter.append(RessourceMedicale.niveau == niveau)
    if recherche:
        base_filter.append(
            RessourceMedicale.titre.ilike(f"%{recherche}%") |
            RessourceMedicale.resume.ilike(f"%{recherche}%")
        )

    count_result = await db.execute(select(RessourceMedicale).where(*base_filter))
    total = len(count_result.scalars().all())

    stmt = (
        select(RessourceMedicale)
        .where(*base_filter)
        .options(selectinload(RessourceMedicale.medecin))
        .order_by(RessourceMedicale.created_at.desc())
        .offset((page - 1) * limite)
        .limit(limite)
    )
    result = await db.execute(stmt)
    ressources = result.scalars().all()

    def _author(r):
        m = r.medecin
        if not m:
            return {"name": "Dr. Inconnu", "avatar": "?", "specialty": "", "hospital": ""}
        initials = ((m.prenom or "?")[0] + (m.nom or "?")[0]).upper()
        return {
            "name":     f"Dr. {m.prenom} {m.nom}",
            "avatar":   initials,
            "specialty": m.specialite or "Médecin",
            "hospital":  m.etablissement or "",
        }

    return {
        "total":    total,
        "page":     page,
        "limite":   limite,
        "pages":    (total + limite - 1) // limite,
        "data": [
            {
                "id":          r.id,
                "casTitle":    r.titre,
                "casId":       r.id,
                "titre":       r.titre,
                "text":        r.resume or "",
                "author":      _author(r),
                "pathologie":  r.pathologie,
                "tags":        r.tags or [],
                "niveau":      r.niveau,
                "has_pdf":     r.pdf_url is not None,
                "nb_vues":     r.nb_vues,
                "nb_telechargements": r.nb_telechargements,
                "medecin_id":  r.medecin_id,
                "time":        r.created_at.isoformat(),
                "likes":       0,
                "liked":       False,
                "pinned":      False,
                "type":        "feedback",
                "replies":     [],
            }
            for r in ressources
        ]
    }


# ─────────────────────────────────────────────────────────────────
# GET /ressources/pathologies — liste des pathologies disponibles
# ─────────────────────────────────────────────────────────────────
@router.get("/pathologies")
async def lister_pathologies():
    return {"pathologies": PATHOLOGIES_VALIDES}


# ─────────────────────────────────────────────────────────────────
# GET /ressources/{id}  — détail + incrément vues
# ─────────────────────────────────────────────────────────────────
@router.get("/{ressource_id}")
async def get_ressource(ressource_id: str, db: AsyncSession = Depends(get_db)):
    result    = await db.execute(
        select(RessourceMedicale).where(
            RessourceMedicale.id == ressource_id,
            RessourceMedicale.publie == True
        )
    )
    ressource = result.scalar_one_or_none()
    if not ressource:
        raise HTTPException(404, "Ressource introuvable")

    # Incrémenter les vues
    ressource.nb_vues += 1
    await db.commit()

    return {
        "id":         ressource.id,
        "titre":      ressource.titre,
        "resume":     ressource.resume,
        "contenu":    ressource.contenu,
        "pathologie": ressource.pathologie,
        "tags":       ressource.tags,
        "niveau":     ressource.niveau,
        "has_pdf":    ressource.pdf_url is not None,
        "nb_vues":           ressource.nb_vues,
        "nb_telechargements": ressource.nb_telechargements,
        "medecin_id": ressource.medecin_id,
        "created_at": ressource.created_at.isoformat(),
    }


# ─────────────────────────────────────────────────────────────────
# GET /ressources/{id}/telecharger — télécharger le PDF
# ─────────────────────────────────────────────────────────────────
@router.get("/{ressource_id}/telecharger")
async def telecharger_pdf(ressource_id: str, db: AsyncSession = Depends(get_db)):
    result    = await db.execute(
        select(RessourceMedicale).where(
            RessourceMedicale.id == ressource_id,
            RessourceMedicale.publie == True
        )
    )
    ressource = result.scalar_one_or_none()

    if not ressource:
        raise HTTPException(404, "Ressource introuvable")
    if not ressource.pdf_url:
        raise HTTPException(404, "Aucun PDF disponible pour cette ressource")

    pdf_path = Path(ressource.pdf_url)
    if not pdf_path.exists():
        raise HTTPException(404, "Fichier PDF introuvable sur le serveur")

    # Incrémenter les téléchargements
    ressource.nb_telechargements += 1
    await db.commit()

    nom_fichier = f"pneumoia-{ressource.pathologie or 'ressource'}-{ressource.id}.pdf"
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=nom_fichier
    )


# ══════════════════════════════════════════════════════════════════
# ROUTES PROTÉGÉES — token médecin requis
# ══════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────
# GET /ressources/medecin/mes-ressources — toutes mes ressources
# ─────────────────────────────────────────────────────────────────
@router.get("/medecin/mes-ressources")
async def mes_ressources(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db)
):
    medecin = await get_medecin_connecte(credentials, db)
    result  = await db.execute(
        select(RessourceMedicale)
        .where(RessourceMedicale.medecin_id == medecin.id)
        .order_by(RessourceMedicale.created_at.desc())
    )
    ressources = result.scalars().all()

    return [
        {
            "id":         r.id,
            "titre":      r.titre,
            "resume":     r.resume,
            "pathologie": r.pathologie,
            "tags":       r.tags,
            "niveau":     r.niveau,
            "has_pdf":    r.pdf_url is not None,
            "publie":     r.publie,
            "nb_vues":           r.nb_vues,
            "nb_telechargements": r.nb_telechargements,
            "created_at": r.created_at.isoformat(),
            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
        }
        for r in ressources
    ]


# ─────────────────────────────────────────────────────────────────
# POST /ressources/medecin/creer — créer une ressource
# ─────────────────────────────────────────────────────────────────
@router.post("/medecin/creer", status_code=201)
async def creer_ressource(
    titre:      str           = Form(...),
    resume:     str           = Form(...),
    contenu:    str           = Form(""),
    pathologie: str           = Form(...),
    niveau:     str           = Form("3ème année"),
    tags:       str           = Form(""),       # JSON string ex: ["tag1","tag2"]
    publier:    bool          = Form(False),
    pdf:        Optional[UploadFile] = File(None),
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db)
):
    medecin = await get_medecin_connecte(credentials, db)

    # Validation pathologie
    if pathologie not in PATHOLOGIES_VALIDES:
        raise HTTPException(400, f"Pathologie invalide. Valides : {PATHOLOGIES_VALIDES}")

    # Parser les tags
    import json
    try:
        tags_list = json.loads(tags) if tags else []
        if not isinstance(tags_list, list):
            tags_list = []
    except Exception:
        tags_list = []

    # Sauvegarder le PDF si fourni
    pdf_url = None
    if pdf and pdf.filename:
        if not pdf.filename.lower().endswith(".pdf"):
            raise HTTPException(400, "Seuls les fichiers PDF sont acceptés")

        contenu_pdf = await pdf.read()
        if len(contenu_pdf) > PDF_MAX_SIZE:
            raise HTTPException(400, f"PDF trop lourd (max 20 Mo)")

        res_id      = generate_ressource_id()
        dossier     = UPLOAD_DIR / res_id
        dossier.mkdir(parents=True, exist_ok=True)
        chemin_pdf  = dossier / "document.pdf"
        with open(chemin_pdf, "wb") as f:
            f.write(contenu_pdf)
        pdf_url = str(chemin_pdf)
    else:
        res_id = generate_ressource_id()

    ressource = RessourceMedicale(
        id         = res_id,
        medecin_id = medecin.id,
        titre      = titre,
        resume     = resume,
        contenu    = contenu,
        pathologie = pathologie,
        niveau     = niveau,
        tags       = tags_list,
        pdf_url    = pdf_url,
        publie     = publier,
    )
    db.add(ressource)
    await db.commit()

    return {
        "message":  "Ressource créée avec succès",
        "id":       ressource.id,
        "publie":   ressource.publie,
    }


# ─────────────────────────────────────────────────────────────────
# PUT /ressources/medecin/{id}/modifier — modifier une ressource
# ─────────────────────────────────────────────────────────────────
@router.put("/medecin/{ressource_id}/modifier")
async def modifier_ressource(
    ressource_id: str,
    titre:      Optional[str]  = Form(None),
    resume:     Optional[str]  = Form(None),
    contenu:    Optional[str]  = Form(None),
    pathologie: Optional[str]  = Form(None),
    niveau:     Optional[str]  = Form(None),
    tags:       Optional[str]  = Form(None),
    pdf:        Optional[UploadFile] = File(None),
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db)
):
    medecin   = await get_medecin_connecte(credentials, db)
    result    = await db.execute(
        select(RessourceMedicale).where(
            RessourceMedicale.id         == ressource_id,
            RessourceMedicale.medecin_id == medecin.id
        )
    )
    ressource = result.scalar_one_or_none()
    if not ressource:
        raise HTTPException(404, "Ressource introuvable")

    if titre:      ressource.titre      = titre
    if resume:     ressource.resume     = resume
    if contenu:    ressource.contenu    = contenu
    if pathologie: ressource.pathologie = pathologie
    if niveau:     ressource.niveau     = niveau

    if tags:
        import json
        try:
            ressource.tags = json.loads(tags)
        except Exception:
            pass

    # Nouveau PDF
    if pdf and pdf.filename:
        if not pdf.filename.lower().endswith(".pdf"):
            raise HTTPException(400, "Seuls les fichiers PDF sont acceptés")
        contenu_pdf = await pdf.read()
        if len(contenu_pdf) > PDF_MAX_SIZE:
            raise HTTPException(400, "PDF trop lourd (max 20 Mo)")

        # Supprimer l'ancien
        if ressource.pdf_url:
            ancien = Path(ressource.pdf_url)
            if ancien.exists():
                ancien.unlink()

        dossier = UPLOAD_DIR / ressource_id
        dossier.mkdir(parents=True, exist_ok=True)
        chemin_pdf = dossier / "document.pdf"
        with open(chemin_pdf, "wb") as f:
            f.write(contenu_pdf)
        ressource.pdf_url = str(chemin_pdf)

    ressource.updated_at = datetime.utcnow()
    await db.commit()
    return {"message": "Ressource modifiée avec succès"}


# ─────────────────────────────────────────────────────────────────
# POST /ressources/medecin/{id}/publier — publier / dépublier
# ─────────────────────────────────────────────────────────────────
@router.post("/medecin/{ressource_id}/publier")
async def publier_ressource(
    ressource_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db)
):
    medecin   = await get_medecin_connecte(credentials, db)
    result    = await db.execute(
        select(RessourceMedicale).where(
            RessourceMedicale.id         == ressource_id,
            RessourceMedicale.medecin_id == medecin.id
        )
    )
    ressource = result.scalar_one_or_none()
    if not ressource:
        raise HTTPException(404, "Ressource introuvable")

    ressource.publie     = not ressource.publie
    ressource.updated_at = datetime.utcnow()
    await db.commit()

    action = "publiée" if ressource.publie else "dépubliée"
    return {
        "message": f"Ressource {action} avec succès",
        "publie":  ressource.publie
    }


# ─────────────────────────────────────────────────────────────────
# DELETE /ressources/medecin/{id} — supprimer une ressource
# ─────────────────────────────────────────────────────────────────
@router.delete("/medecin/{ressource_id}")
async def supprimer_ressource(
    ressource_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db)
):
    medecin   = await get_medecin_connecte(credentials, db)
    result    = await db.execute(
        select(RessourceMedicale).where(
            RessourceMedicale.id         == ressource_id,
            RessourceMedicale.medecin_id == medecin.id
        )
    )
    ressource = result.scalar_one_or_none()
    if not ressource:
        raise HTTPException(404, "Ressource introuvable")

    # Supprimer le PDF si existant
    if ressource.pdf_url:
        chemin = Path(ressource.pdf_url)
        if chemin.exists():
            chemin.unlink()
        dossier = chemin.parent
        if dossier.exists() and not any(dossier.iterdir()):
            dossier.rmdir()

    await db.delete(ressource)
    await db.commit()
    return {"message": "Ressource supprimée avec succès"}
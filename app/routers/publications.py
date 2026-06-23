# app/routers/publications.py
"""
Feed des publications médicales + commentaires pour l'interface médecin/aide.
Accessible par : médecin (poster, commenter, réagir) et aide soignant (lire, commenter).
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional, List
from jose import JWTError

from app.database import get_db
from app.core.security import decode_token
from app.models.medecin import Medecin
from app.models.aide_soignant import AideSoignant
from app.models.publication import Publication
from app.models.commentaire import Commentaire, LikeCommentaire
from app.models.reaction import Reaction

router = APIRouter(prefix="/publications", tags=["Publications & Commentaires"])
bearer = HTTPBearer()


# ── Schemas ───────────────────────────────────────────────────────
class CommentaireCreate(BaseModel):
    contenu: str


class ReactionCreate(BaseModel):
    type: str  # utile | insightful | accord | desaccord


class PublicationCreate(BaseModel):
    titre:          str
    contenu:        Optional[str] = None
    type:           str           # cas_clinique | question | article | discussion
    communaute_id:  Optional[str] = None
    tags:           List[str]     = []
    consultation_id: Optional[str] = None


# ── Dépendance mixte médecin / aide ──────────────────────────────
async def get_actor(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise HTTPException(401, "Token invalide ou expiré")

    role = payload.get("role")

    if role == "medecin":
        medecin = await db.get(Medecin, payload.get("sub"))
        if not medecin or medecin.statut != "valide":
            raise HTTPException(403, "Compte médecin non autorisé")
        return {
            "type":       "medecin",
            "id":         medecin.id,
            "medecin_id": medecin.id,
            "nom":        f"Dr. {medecin.prenom} {medecin.nom}",
            "specialty":  getattr(medecin, "specialite", "Pneumologue"),
        }

    if role == "aide_soignant":
        aide = await db.get(AideSoignant, payload.get("sub"))
        if not aide or aide.statut != "actif":
            raise HTTPException(403, "Compte aide soignant non autorisé")
        return {
            "type":       "aide_soignant",
            "id":         aide.id,
            "medecin_id": aide.medecin_id,
            "nom":        f"{aide.prenom} {aide.nom}",
            "specialty":  "Aide soignant",
        }

    raise HTTPException(401, "Rôle non reconnu")


# ── GET /publications ─────────────────────────────────────────────
@router.get("")
async def list_publications(
    q:             Optional[str]  = Query(None, description="Recherche texte libre"),
    type_p:        Optional[str]  = Query(None, alias="type"),
    mine:          bool           = Query(False, description="Uniquement mes publications"),
    with_comments: bool           = Query(False, description="Inclure les commentaires"),
    limit:         int            = Query(50, le=200),
    offset:        int            = Query(0, ge=0),
    actor:         dict           = Depends(get_actor),
    db:            AsyncSession   = Depends(get_db),
):
    """
    Feed de publications pour l'onglet Confrères (médecin) et Posts médecins (aide).
    Retourne toutes les publications accessibles, ordonnées par date décroissante.
    """
    stmt = (
        select(Publication)
        .options(
            selectinload(Publication.auteur),
            selectinload(Publication.commentaires)
                .selectinload(Commentaire.auteur),
            selectinload(Publication.commentaires)
                .selectinload(Commentaire.auteur_aide),
            selectinload(Publication.commentaires)
                .selectinload(Commentaire.likes),
            selectinload(Publication.reactions),
        )
        .order_by(desc(Publication.created_at))
        .limit(limit)
        .offset(offset)
    )

    if mine:
        stmt = stmt.where(Publication.auteur_id == actor["id"])
    # else: pas de filtre publie (le modèle n'a pas ce champ — toutes les publications sont visibles)

    if type_p and type_p in ("cas_clinique", "question", "article", "discussion"):
        stmt = stmt.where(Publication.type == type_p)

    if q:
        q_lower = f"%{q.lower()}%"
        from sqlalchemy import or_, func
        stmt = stmt.where(
            or_(
                func.lower(Publication.titre).like(q_lower),
                func.lower(Publication.contenu).like(q_lower),
            )
        )

    result = await db.execute(stmt)
    pubs = result.scalars().all()
    return [_serialize_publication(p, actor, with_comments=(with_comments or mine)) for p in pubs]


# ── GET /publications/{id} ────────────────────────────────────────
@router.get("/{pub_id}")
async def get_publication(
    pub_id: str,
    actor:  dict        = Depends(get_actor),
    db:     AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Publication)
        .where(Publication.id == pub_id)
        .options(
            selectinload(Publication.auteur),
            selectinload(Publication.commentaires)
                .selectinload(Commentaire.auteur),
            selectinload(Publication.commentaires)
                .selectinload(Commentaire.auteur_aide),
            selectinload(Publication.commentaires)
                .selectinload(Commentaire.likes),
            selectinload(Publication.reactions),
        )
    )
    pub = result.scalar_one_or_none()
    if not pub:
        raise HTTPException(404, "Publication introuvable")
    return _serialize_publication(pub, actor, with_comments=True)


# ── POST /publications ────────────────────────────────────────────
@router.post("", status_code=201)
async def create_publication(
    body:  PublicationCreate,
    actor: dict        = Depends(get_actor),
    db:    AsyncSession = Depends(get_db),
):
    if actor["type"] != "medecin":
        raise HTTPException(403, "Seuls les médecins peuvent publier")
    valid_types = ("cas_clinique", "question", "article", "discussion")
    if body.type not in valid_types:
        raise HTTPException(422, f"Type invalide. Valeurs : {valid_types}")

    pub = Publication(
        communaute_id   = body.communaute_id,
        auteur_id       = actor["id"],
        consultation_id = body.consultation_id,
        titre           = body.titre.strip(),
        contenu         = body.contenu,
        type            = body.type,
        tags            = body.tags,
    )
    db.add(pub)
    await db.flush()

    # Notifier tous les aides actifs du médecin
    try:
        from app.services.notification_service import push_notif as _pn
        from app.models.aide_soignant import AideSoignant as _AS
        _aides_r = await db.execute(
            select(_AS).where(_AS.medecin_id == actor["id"], _AS.statut == "actif")
        )
        for _aide in _aides_r.scalars().all():
            await _pn(db, dest_id=_aide.id, type_dest="aide_soignant",
                      type_notif="nouveau_post", titre="Nouvelle publication",
                      message=f"{actor['nom']} a publié « {pub.titre} ».",
                      meta={"lien": "/aide/publications", "pub_id": pub.id})
    except Exception as _e:
        import logging; logging.getLogger(__name__).warning("push_notif pub: %s", _e)

    # Notifier tous les admins
    try:
        from app.services.notification_service import push_notif as _pn
        from app.models.admin import Admin as _Admin
        from app.models.notification import Notification as _Notif
        _admins_r = await db.execute(select(_Admin.id))
        for _admin_id in _admins_r.scalars().all():
            db.add(_Notif(
                destinataire_id = _admin_id,
                type_dest       = "admin",
                type_notif      = "nouvelle_publication",
                titre           = f"Nouvelle publication — {actor['nom']}",
                message         = f"« {pub.titre} » ({pub.type.replace('_', ' ')})",
                meta            = {"pub_id": pub.id, "lien": "/administrateur/commentaires"},
            ))
    except Exception as _e:
        import logging; logging.getLogger(__name__).warning("notif admin pub: %s", _e)

    await db.commit()
    return {
        "id":             pub.id,
        "auteur_id":      pub.auteur_id,
        "casTitle":       pub.titre,
        "casId":          pub.id,
        "author":         {"name": actor["nom"], "avatar": "?", "specialty": actor.get("specialty", "")},
        "text":           pub.contenu or "",
        "time":           pub.created_at.isoformat() + "Z",
        "type":           pub.type,
        "tags":           pub.tags or [],
        "nb_commentaires": 0,
        "nb_reactions":   0,
        "liked":          False,
        "my_reaction":    None,
        "pinned":         False,
    }


# ── GET /publications/{id}/commentaires ──────────────────────────
@router.get("/{pub_id}/commentaires")
async def list_commentaires(
    pub_id: str,
    actor:  dict        = Depends(get_actor),
    db:     AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Commentaire)
        .where(
            Commentaire.publication_id == pub_id,
            Commentaire.parent_id == None,
        )
        .options(
            selectinload(Commentaire.auteur),
            selectinload(Commentaire.auteur_aide),
            selectinload(Commentaire.likes),
            selectinload(Commentaire.replies)
                .selectinload(Commentaire.auteur),
            selectinload(Commentaire.replies)
                .selectinload(Commentaire.auteur_aide),
            selectinload(Commentaire.replies)
                .selectinload(Commentaire.likes),
        )
        .order_by(Commentaire.created_at.asc())
    )
    comments = result.scalars().all()
    return [_serialize_commentaire(c, actor["id"]) for c in comments]


# ── POST /publications/{id}/commentaires ─────────────────────────
@router.post("/{pub_id}/commentaires", status_code=201)
async def add_commentaire(
    pub_id: str,
    body:   CommentaireCreate,
    actor:  dict        = Depends(get_actor),
    db:     AsyncSession = Depends(get_db),
):
    pub = await db.get(Publication, pub_id)
    if not pub:
        raise HTTPException(404, "Publication introuvable")
    if not body.contenu.strip():
        raise HTTPException(422, "Le commentaire ne peut pas être vide")

    c = Commentaire(
        publication_id = pub_id,
        auteur_type    = actor["type"],
        auteur_id      = actor["id"] if actor["type"] == "medecin" else None,
        auteur_aide_id = actor["id"] if actor["type"] == "aide_soignant" else None,
        contenu        = body.contenu.strip(),
    )
    db.add(c)
    pub.nb_commentaires += 1
    await db.flush()

    try:
        from app.services.notification_service import push_notif
        from app.models.aide_soignant import AideSoignant
        # 1. Notifier l'auteur de la publication si c'est quelqu'un d'autre
        if pub.auteur_id and pub.auteur_id != actor["id"]:
            await push_notif(
                db,
                dest_id   = pub.auteur_id,
                type_dest = "medecin",
                type_notif= "nouveau_commentaire",
                titre     = "Nouveau commentaire sur votre publication",
                message   = f"{actor['nom']} a commenté votre publication « {pub.titre} ».",
                meta      = {"lien": "/medecin/commentaires"},
            )
        # 2. Notifier les aides soignants actifs du commentateur (médecin)
        if actor["type"] == "medecin":
            aides_res = await db.execute(
                select(AideSoignant).where(
                    AideSoignant.medecin_id == actor["id"],
                    AideSoignant.statut     == "actif",
                )
            )
            for aide in aides_res.scalars().all():
                await push_notif(
                    db,
                    dest_id   = aide.id,
                    type_dest = "aide_soignant",
                    type_notif= "nouveau_commentaire",
                    titre     = "Votre médecin a commenté une publication",
                    message   = f"{actor['nom']} a commenté la publication « {pub.titre} ».",
                    meta      = {"lien": "/aide/commentaires"},
                )
    except Exception as _e:
        import logging; logging.getLogger(__name__).warning("notif commentaire: %s", _e)

    await db.commit()
    await db.refresh(c)
    return _serialize_commentaire(c, actor["id"])


# ── POST /publications/{pub_id}/commentaires/{cid}/reply ─────────
@router.post("/{pub_id}/commentaires/{cid}/reply", status_code=201)
async def reply_to_commentaire(
    pub_id: str,
    cid:    str,
    body:   CommentaireCreate,
    actor:  dict        = Depends(get_actor),
    db:     AsyncSession = Depends(get_db),
):
    parent = await db.get(Commentaire, cid)
    if not parent or parent.publication_id != pub_id:
        raise HTTPException(404, "Commentaire introuvable")
    if parent.parent_id is not None:
        raise HTTPException(422, "Impossible de répondre à une réponse")

    c = Commentaire(
        publication_id = pub_id,
        parent_id      = cid,
        auteur_type    = actor["type"],
        auteur_id      = actor["id"] if actor["type"] == "medecin" else None,
        auteur_aide_id = actor["id"] if actor["type"] == "aide_soignant" else None,
        contenu        = body.contenu.strip(),
    )
    db.add(c)
    await db.flush()

    try:
        from app.services.notification_service import push_notif as _pn
        pub_obj = await db.get(Publication, pub_id)
        # Notifier l'auteur de la publication (médecin) si c'est l'aide qui répond
        if actor["type"] == "aide_soignant" and pub_obj and pub_obj.auteur_id:
            await _pn(db, dest_id=pub_obj.auteur_id, type_dest="medecin",
                      type_notif="nouveau_commentaire", titre="Réponse sur votre publication",
                      message=f"{actor['nom']} a répondu à un commentaire sur « {pub_obj.titre} ».",
                      meta={"lien": "/medecin/commentaires"})
        # Notifier l'aide auteur du commentaire parent si le médecin lui répond
        if actor["type"] == "medecin" and parent.auteur_type == "aide_soignant" and parent.auteur_aide_id:
            await _pn(db, dest_id=parent.auteur_aide_id, type_dest="aide_soignant",
                      type_notif="nouveau_commentaire", titre="Réponse à votre commentaire",
                      message=f"{actor['nom']} a répondu à votre commentaire{' sur « ' + pub_obj.titre + ' »' if pub_obj else ''}.",
                      meta={"lien": "/aide/publications", "pub_id": pub_id})
    except Exception as _e:
        import logging; logging.getLogger(__name__).warning("push_notif reply: %s", _e)

    await db.commit()
    await db.refresh(c)
    return _serialize_commentaire(c, actor["id"])


# ── POST /publications/{pub_id}/commentaires/{cid}/like ──────────
@router.post("/{pub_id}/commentaires/{cid}/like")
async def toggle_like_commentaire(
    pub_id: str,
    cid:    str,
    actor:  dict        = Depends(get_actor),
    db:     AsyncSession = Depends(get_db),
):
    c = await db.get(Commentaire, cid)
    if not c or c.publication_id != pub_id:
        raise HTTPException(404, "Commentaire introuvable")

    existing = await db.execute(
        select(LikeCommentaire).where(
            LikeCommentaire.commentaire_id == cid,
            LikeCommentaire.auteur_id == actor["id"],
        )
    )
    like = existing.scalar_one_or_none()

    if like:
        await db.delete(like)
        c.likes_count = max(0, c.likes_count - 1)
        liked = False
    else:
        db.add(LikeCommentaire(
            commentaire_id = cid,
            auteur_type    = actor["type"],
            auteur_id      = actor["id"],
        ))
        c.likes_count += 1
        liked = True

        # Notifier l'aide soignant si c'est lui l'auteur du commentaire
        if c.auteur_type == "aide_soignant" and c.auteur_aide_id and c.auteur_aide_id != actor["id"]:
            try:
                await db.flush()
                from app.services.notification_service import push_notif as _pn
                await _pn(db, dest_id=c.auteur_aide_id, type_dest="aide_soignant",
                          type_notif="referent_like", titre="Votre commentaire a été aimé",
                          message=f"{actor['nom']} a aimé votre commentaire.",
                          meta={"lien": "/aide/publications", "pub_id": c.publication_id})
            except Exception as _e:
                import logging; logging.getLogger(__name__).warning("push_notif like: %s", _e)

    await db.commit()
    return {"liked": liked, "likes_count": c.likes_count}


# ── DELETE /publications/{pub_id}/commentaires/{cid} ─────────────
@router.delete("/{pub_id}/commentaires/{cid}", status_code=204)
async def delete_commentaire(
    pub_id: str,
    cid:    str,
    actor:  dict        = Depends(get_actor),
    db:     AsyncSession = Depends(get_db),
):
    c = await db.get(Commentaire, cid)
    if not c or c.publication_id != pub_id:
        raise HTTPException(404, "Commentaire introuvable")

    auteur_id = c.auteur_id if c.auteur_type == "medecin" else c.auteur_aide_id
    if auteur_id != actor["id"]:
        raise HTTPException(403, "Vous ne pouvez supprimer que vos propres commentaires")

    pub = await db.get(Publication, pub_id)
    if pub:
        pub.nb_commentaires = max(0, pub.nb_commentaires - 1)

    await db.delete(c)
    await db.commit()


# ── POST /publications/{id}/react ─────────────────────────────────
@router.post("/{pub_id}/react")
async def react_to_publication(
    pub_id: str,
    body:   ReactionCreate,
    actor:  dict        = Depends(get_actor),
    db:     AsyncSession = Depends(get_db),
):
    """Toggle like/réaction sur une publication. Médecin uniquement."""
    if actor["type"] != "medecin":
        raise HTTPException(403, "Les réactions sont réservées aux médecins")

    pub = await db.get(Publication, pub_id)
    if not pub:
        raise HTTPException(404, "Publication introuvable")

    valid_types = ("utile", "insightful", "accord", "desaccord")
    if body.type not in valid_types:
        raise HTTPException(422, f"Type invalide. Valeurs : {valid_types}")

    existing = await db.execute(
        select(Reaction).where(
            Reaction.publication_id == pub_id,
            Reaction.medecin_id     == actor["id"],
        )
    )
    reaction = existing.scalar_one_or_none()

    is_new_reaction = False
    if reaction:
        if reaction.type == body.type:
            await db.delete(reaction)
            pub.nb_reactions = max(0, pub.nb_reactions - 1)
            reacted = False
        else:
            reaction.type = body.type
            reacted = True
    else:
        db.add(Reaction(publication_id=pub_id, medecin_id=actor["id"], type=body.type))
        pub.nb_reactions += 1
        reacted = True
        is_new_reaction = True

    if is_new_reaction and pub.auteur_id and pub.auteur_id != actor["id"]:
        await db.flush()
        from app.services.notification_service import push_notif
        labels = {"utile": "Utile", "insightful": "Intéressant", "accord": "D'accord", "desaccord": "En désaccord"}
        await push_notif(
            db,
            dest_id   = pub.auteur_id,
            type_dest = "medecin",
            type_notif= "referent_like",
            titre     = "Réaction sur votre publication",
            message   = f"{actor['nom']} a réagi « {labels.get(body.type, body.type)} » à votre publication « {pub.titre} ».",
            meta      = {"lien": "/medecin/commentaires"},
        )

    await db.commit()
    return {"reacted": reacted, "type": body.type if reacted else None, "nb_reactions": pub.nb_reactions}


# ── Sérialisation ─────────────────────────────────────────────────
def _author_from_pub(pub: Publication) -> dict:
    m = pub.auteur
    if not m:
        return {"name": "Inconnu", "avatar": "?", "specialty": "", "hospital": ""}
    return {
        "name":     f"Dr. {m.prenom} {m.nom}",
        "avatar":   (m.prenom[0] + m.nom[0]).upper() if m.prenom and m.nom else "?",
        "specialty": getattr(m, "specialite", "Pneumologue"),
        "hospital":  getattr(m, "etablissement", ""),
    }


def _author_from_com(c: Commentaire) -> dict:
    if c.auteur_type == "medecin" and c.auteur:
        m = c.auteur
        return {
            "name":    f"Dr. {m.prenom} {m.nom}",
            "avatar":  (m.prenom[0] + m.nom[0]).upper() if m.prenom and m.nom else "?",
            "role":    getattr(m, "specialite", "Médecin"),
        }
    if c.auteur_type == "aide_soignant" and c.auteur_aide:
        a = c.auteur_aide
        return {
            "name":   f"{a.prenom} {a.nom}",
            "avatar": (a.prenom[0] + a.nom[0]).upper() if a.prenom and a.nom else "?",
            "role":   "Aide soignant",
        }
    return {"name": "Inconnu", "avatar": "?", "role": ""}


def _serialize_commentaire(c: Commentaire, current_user_id: str) -> dict:
    liked_ids = {lk.auteur_id for lk in c.likes} if c.likes else set()
    return {
        "id":      c.id,
        "author":  _author_from_com(c),
        "text":    c.contenu,
        "time":    c.created_at.isoformat() + "Z",
        "likes":   c.likes_count,
        "liked":   current_user_id in liked_ids,
        "isMe":    (c.auteur_id == current_user_id or c.auteur_aide_id == current_user_id),
        "replies": [_serialize_commentaire(r, current_user_id) for r in (c.replies or [])],
    }


def _serialize_publication(pub: Publication, actor: dict, with_comments: bool = False) -> dict:
    # Réaction de l'utilisateur courant (médecin seulement)
    my_reaction = None
    if actor["type"] == "medecin" and pub.reactions:
        for r in pub.reactions:
            if r.medecin_id == actor["id"]:
                my_reaction = r.type
                break

    base = {
        "id":             pub.id,
        "auteur_id":      pub.auteur_id,
        "casTitle":       pub.titre,
        "casId":          pub.id,
        "author":         _author_from_pub(pub),
        "text":           pub.contenu or "",
        "time":           pub.created_at.isoformat() + "Z",
        "type":           pub.type,
        "tags":           pub.tags or [],
        "nb_commentaires": pub.nb_commentaires,
        "nb_reactions":   pub.nb_reactions,
        "liked":          my_reaction is not None,
        "my_reaction":    my_reaction,
        "pinned":         False,
    }

    if with_comments and pub.commentaires is not None:
        top_level = [c for c in pub.commentaires if c.parent_id is None]
        base["commentaires"] = [_serialize_commentaire(c, actor["id"]) for c in top_level]

    return base

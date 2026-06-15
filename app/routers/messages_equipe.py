# app/routers/messages_equipe.py
"""
Canal équipe : médecin ↔ aides soignants
Routes accessibles par les deux types d'utilisateurs.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional
from jose import JWTError

from app.database import get_db
from app.core.security import decode_token
from app.models.medecin import Medecin
from app.models.aide_soignant import AideSoignant
from app.models.message_equipe import MessageEquipe, LikeMessageEquipe

router = APIRouter(prefix="/equipe", tags=["Canal Équipe"])
bearer = HTTPBearer()


# ── Schemas ───────────────────────────────────────────────────────
class MessageCreate(BaseModel):
    contenu:  str
    type_msg: str = "rapport"  # rapport | alerte | info


class ReplyCreate(BaseModel):
    contenu: str


# ── Dépendance mixte médecin / aide ──────────────────────────────
async def get_actor(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Retourne un dict commun aux deux types d'utilisateurs :
    { type, id, medecin_id, nom_complet }
    """
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
        }

    raise HTTPException(401, "Rôle non reconnu")


# ── GET /equipe/messages ──────────────────────────────────────────
@router.get("/messages")
async def list_messages(
    actor: dict      = Depends(get_actor),
    db:    AsyncSession = Depends(get_db),
):
    """Récupère tous les messages de l'équipe (sans les réponses — niveau racine)."""
    result = await db.execute(
        select(MessageEquipe)
        .where(
            MessageEquipe.medecin_referent_id == actor["medecin_id"],
            MessageEquipe.parent_id == None,
        )
        .options(
            selectinload(MessageEquipe.auteur_medecin),
            selectinload(MessageEquipe.auteur_aide),
            selectinload(MessageEquipe.likes),
            selectinload(MessageEquipe.replies).selectinload(MessageEquipe.auteur_medecin),
            selectinload(MessageEquipe.replies).selectinload(MessageEquipe.auteur_aide),
            selectinload(MessageEquipe.replies).selectinload(MessageEquipe.likes),
        )
        .order_by(MessageEquipe.pinned.desc(), MessageEquipe.created_at.desc())
    )
    messages = result.scalars().all()
    return [_serialize_message(m, actor["id"]) for m in messages]


# ── POST /equipe/messages ─────────────────────────────────────────
@router.post("/messages", status_code=201)
async def create_message(
    body:  MessageCreate,
    actor: dict         = Depends(get_actor),
    db:    AsyncSession = Depends(get_db),
):
    if body.type_msg not in ("rapport", "alerte", "info"):
        raise HTTPException(422, "type_msg invalide")

    msg = MessageEquipe(
        medecin_referent_id = actor["medecin_id"],
        auteur_type         = actor["type"],
        auteur_medecin_id   = actor["id"] if actor["type"] == "medecin" else None,
        auteur_aide_id      = actor["id"] if actor["type"] == "aide_soignant" else None,
        contenu             = body.contenu.strip(),
        type_msg            = body.type_msg,
    )
    db.add(msg)
    await db.flush()

    from app.services.notification_service import push_notif
    if actor["type"] == "aide_soignant":
        await push_notif(
            db,
            dest_id   = actor["medecin_id"],
            type_dest = "medecin",
            type_notif= "nouveau_message_equipe",
            titre     = "Nouveau message dans l'équipe",
            message   = f"{actor['nom']} a posté un message dans le canal équipe.",
            meta      = {"lien": "/medecin/commentaires"},
        )
    else:
        aides_r = await db.execute(
            select(AideSoignant).where(
                AideSoignant.medecin_id == actor["medecin_id"],
                AideSoignant.statut    == "actif",
            )
        )
        for aide in aides_r.scalars().all():
            await push_notif(
                db,
                dest_id   = aide.id,
                type_dest = "aide_soignant",
                type_notif= "nouveau_message_medecin",
                titre     = "Message du médecin référent",
                message   = f"{actor['nom']} a posté un message dans le canal équipe.",
                meta      = {"lien": "/aide/commentaires"},
            )

    await db.commit()
    await db.refresh(msg)
    return _build_new_msg(msg, actor)


# ── POST /equipe/messages/{id}/reply ─────────────────────────────
@router.post("/messages/{msg_id}/reply", status_code=201)
async def reply_to_message(
    msg_id: str,
    body:   ReplyCreate,
    actor:  dict        = Depends(get_actor),
    db:     AsyncSession = Depends(get_db),
):
    parent = await db.get(MessageEquipe, msg_id)
    if not parent or parent.medecin_referent_id != actor["medecin_id"]:
        raise HTTPException(404, "Message introuvable")
    if parent.parent_id is not None:
        raise HTTPException(422, "Impossible de répondre à une réponse")

    reply = MessageEquipe(
        medecin_referent_id = actor["medecin_id"],
        auteur_type         = actor["type"],
        auteur_medecin_id   = actor["id"] if actor["type"] == "medecin" else None,
        auteur_aide_id      = actor["id"] if actor["type"] == "aide_soignant" else None,
        parent_id           = msg_id,
        contenu             = body.contenu.strip(),
        type_msg            = parent.type_msg,
    )
    db.add(reply)
    await db.flush()

    from app.services.notification_service import push_notif
    if actor["type"] == "aide_soignant":
        await push_notif(
            db,
            dest_id   = actor["medecin_id"],
            type_dest = "medecin",
            type_notif= "nouveau_commentaire",
            titre     = "Réponse dans le canal équipe",
            message   = f"{actor['nom']} a répondu à un message dans le canal équipe.",
            meta      = {"lien": "/medecin/commentaires"},
        )
    else:
        aides_r = await db.execute(
            select(AideSoignant).where(
                AideSoignant.medecin_id == actor["medecin_id"],
                AideSoignant.statut    == "actif",
            )
        )
        for aide in aides_r.scalars().all():
            await push_notif(
                db,
                dest_id   = aide.id,
                type_dest = "aide_soignant",
                type_notif= "nouveau_commentaire",
                titre     = "Réponse du médecin référent",
                message   = f"{actor['nom']} a répondu dans le canal équipe.",
                meta      = {"lien": "/aide/commentaires"},
            )

    await db.commit()
    await db.refresh(reply)
    return _build_new_reply(reply, actor)


# ── POST /equipe/messages/{id}/like ──────────────────────────────
@router.post("/messages/{msg_id}/like")
async def toggle_like(
    msg_id: str,
    actor:  dict        = Depends(get_actor),
    db:     AsyncSession = Depends(get_db),
):
    msg = await db.get(MessageEquipe, msg_id)
    if not msg or msg.medecin_referent_id != actor["medecin_id"]:
        raise HTTPException(404, "Message introuvable")

    existing = await db.execute(
        select(LikeMessageEquipe).where(
            LikeMessageEquipe.message_id == msg_id,
            LikeMessageEquipe.auteur_id  == actor["id"],
        )
    )
    like = existing.scalar_one_or_none()

    if like:
        await db.delete(like)
        msg.likes_count = max(0, msg.likes_count - 1)
        liked = False
    else:
        db.add(LikeMessageEquipe(
            message_id  = msg_id,
            auteur_type = actor["type"],
            auteur_id   = actor["id"],
        ))
        msg.likes_count += 1
        liked = True

    await db.commit()
    return {"liked": liked, "likes_count": msg.likes_count}


# ── DELETE /equipe/messages/{id} ──────────────────────────────────
@router.delete("/messages/{msg_id}", status_code=204)
async def delete_message(
    msg_id: str,
    actor:  dict        = Depends(get_actor),
    db:     AsyncSession = Depends(get_db),
):
    msg = await db.get(MessageEquipe, msg_id)
    if not msg or msg.medecin_referent_id != actor["medecin_id"]:
        raise HTTPException(404, "Message introuvable")

    # Seul l'auteur peut supprimer son message
    auteur_id = msg.auteur_medecin_id if msg.auteur_type == "medecin" else msg.auteur_aide_id
    if auteur_id != actor["id"]:
        raise HTTPException(403, "Vous ne pouvez supprimer que vos propres messages")

    await db.delete(msg)
    await db.commit()


# ── PATCH /equipe/messages/{id}/pin ──────────────────────────────
@router.patch("/messages/{msg_id}/pin")
async def toggle_pin(
    msg_id: str,
    actor:  dict        = Depends(get_actor),
    db:     AsyncSession = Depends(get_db),
):
    if actor["type"] != "medecin":
        raise HTTPException(403, "Seul le médecin peut épingler un message")

    msg = await db.get(MessageEquipe, msg_id)
    if not msg or msg.medecin_referent_id != actor["medecin_id"]:
        raise HTTPException(404, "Message introuvable")

    msg.pinned = not msg.pinned
    await db.commit()
    return {"pinned": msg.pinned}


# ── Helpers retour immédiat (sans lazy load) ──────────────────────
def _actor_author(actor: dict) -> dict:
    nom = actor["nom"]
    parts = [p for p in nom.split() if p and p != "Dr."]
    avatar = "".join(p[0].upper() for p in parts[:2]) if parts else "?"
    return {
        "name":     nom,
        "avatar":   avatar,
        "role":     "Médecin référent" if actor["type"] == "medecin" else "Aide soignant",
        "isDoctor": actor["type"] == "medecin",
    }


def _build_new_reply(r: MessageEquipe, actor: dict) -> dict:
    return {
        "id":     r.id,
        "author": _actor_author(actor),
        "text":   r.contenu,
        "time":   r.created_at.isoformat(),
        "likes":  0,
        "liked":  False,
        "isMe":   True,
    }


def _build_new_msg(m: MessageEquipe, actor: dict) -> dict:
    return {
        "id":      m.id,
        "author":  _actor_author(actor),
        "text":    m.contenu,
        "time":    m.created_at.isoformat(),
        "type":    m.type_msg,
        "pinned":  False,
        "likes":   0,
        "liked":   False,
        "isMe":    True,
        "replies": [],
    }


# ── Sérialisation ─────────────────────────────────────────────────
def _serialize_author(msg: MessageEquipe) -> dict:
    if msg.auteur_type == "medecin" and msg.auteur_medecin:
        m = msg.auteur_medecin
        return {
            "name":     f"Dr. {m.prenom} {m.nom}",
            "avatar":   (m.prenom[0] + m.nom[0]).upper() if m.prenom and m.nom else "?",
            "role":     "Médecin référent",
            "isDoctor": True,
        }
    if msg.auteur_type == "aide_soignant" and msg.auteur_aide:
        a = msg.auteur_aide
        return {
            "name":     f"{a.prenom} {a.nom}",
            "avatar":   (a.prenom[0] + a.nom[0]).upper() if a.prenom and a.nom else "?",
            "role":     "Aide soignant",
            "isDoctor": False,
        }
    return {"name": "Inconnu", "avatar": "?", "role": "", "isDoctor": False}


def _serialize_reply(r: MessageEquipe, current_user_id: str) -> dict:
    liked_ids = {lk.auteur_id for lk in r.likes} if r.likes else set()
    return {
        "id":     r.id,
        "author": _serialize_author(r),
        "text":   r.contenu,
        "time":   r.created_at.isoformat(),
        "likes":  r.likes_count,
        "liked":  current_user_id in liked_ids,
    }


def _serialize_message(m: MessageEquipe, current_user_id: str) -> dict:
    liked_ids = {lk.auteur_id for lk in m.likes} if m.likes else set()
    auteur_id = m.auteur_medecin_id if m.auteur_type == "medecin" else m.auteur_aide_id
    return {
        "id":      m.id,
        "author":  _serialize_author(m),
        "text":    m.contenu,
        "time":    m.created_at.isoformat(),
        "type":    m.type_msg,
        "pinned":  m.pinned,
        "likes":   m.likes_count,
        "liked":   current_user_id in liked_ids,
        "isMe":    auteur_id == current_user_id,
        "replies": [_serialize_reply(r, current_user_id) for r in (m.replies or [])],
    }

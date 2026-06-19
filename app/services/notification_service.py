"""
Helper central — crée une notification en base sans avoir à
importer directement le modèle dans chaque router.

Vérifie la préférence notif_systeme / notifRappelsSysteme avant insertion.

Usage :
    from app.services.notification_service import push_notif
    await push_notif(db, dest_id="PNEU-123", type_dest="medecin",
                     type_notif="aide_nouveau_patient",
                     titre="Nouveau patient créé",
                     message="L'aide soignant Tagne eKale a créé le dossier de Marie Curie.",
                     meta={"patient_id": "PAT-999", "lien": "/medecin/patients"})
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification


async def _prefs_allow(db: AsyncSession, dest_id: str, type_dest: str) -> bool:
    """Retourne False si le destinataire a désactivé les notifications système."""
    try:
        if type_dest == "aide_soignant":
            from app.models.aide_soignant import AideSoignant
            obj = await db.get(AideSoignant, dest_id)
            if obj:
                return bool((obj.preferences or {}).get("notif_systeme", True))
        elif type_dest == "medecin":
            from app.models.medecin import Medecin
            obj = await db.get(Medecin, dest_id)
            if obj:
                return bool((obj.preferences or {}).get("notifRappelsSysteme", True))
    except Exception:
        pass
    return True


async def push_notif(
    db: AsyncSession,
    dest_id:    str,
    type_dest:  str,   # "medecin" | "aide_soignant" | "admin"
    type_notif: str,
    titre:      str,
    message:    str = "",
    meta:       dict | None = None,
    force:      bool = False,  # True = bypass préférences (notifs opérationnelles critiques)
) -> Notification | None:
    if not force and not await _prefs_allow(db, dest_id, type_dest):
        return None

    try:
        n = Notification(
            destinataire_id = dest_id,
            type_dest       = type_dest,
            type_notif      = type_notif,
            titre           = titre,
            message         = message,
            meta            = meta or {},
        )
        db.add(n)
        # Flush sans commit — le commit est fait par le router appelant
        await db.flush()
        return n
    except Exception as e:
        import sys
        print(f"[push_notif] ERREUR insertion notification {type_notif} → {dest_id}: {e}", file=sys.stderr)
        return None

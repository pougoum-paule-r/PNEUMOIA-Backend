from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def log_admin_action(
    db: AsyncSession,
    admin_id: Any,
    action: str,
    *,
    medecin_id: Optional[str] = None,
    details: Optional[dict] = None,
) -> None:
    payload = {"admin_id": str(admin_id), **(details or {})}
    log = AuditLog(action=action, medecin_id=medecin_id, details=payload)
    db.add(log)
    try:
        await db.commit()
    except Exception:
        await db.rollback()

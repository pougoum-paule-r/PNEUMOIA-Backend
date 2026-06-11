from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.admin import Admin
from app.core.security import hash_password
from app.config import settings

async def seed_admin(db: AsyncSession):
    if not settings.ADMIN_EMAIL or not settings.ADMIN_PASSWORD:
        return
    result = await db.execute(select(Admin).where(Admin.email == settings.ADMIN_EMAIL))
    if not result.scalar_one_or_none():
        new_admin = Admin(
            email=settings.ADMIN_EMAIL,
            password_hash=hash_password(settings.ADMIN_PASSWORD),
        )
        db.add(new_admin)
        await db.commit()
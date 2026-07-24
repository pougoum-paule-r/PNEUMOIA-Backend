import asyncio, sys
sys.path.insert(0, '/app')

async def check():
    from app.database import AsyncSessionLocal
    from app.models.diagnostic_ia import DiagnosticIA
    from sqlalchemy import select
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(DiagnosticIA).limit(10))
        diags = result.scalars().all()
        for d in diags:
            maladies = getattr(d, 'maladies', None) or []
            if not maladies:
                continue
            m = maladies[0] if maladies else {}
            criteres = m.get('criteres_valides', [])
            if not criteres:
                continue
            c = criteres[0]
            print("Type:", type(c))
            print("Repr:", repr(c[:80]))
            enc = c[:30].encode('utf-8')
            print("UTF-8 bytes:", enc)
            return

asyncio.run(check())

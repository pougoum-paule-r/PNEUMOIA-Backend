# app/routers/monitoring.py
from collections import OrderedDict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, Float, Integer, cast, case

from app.database import get_db
from app.core.security import get_current_medecin
from app.models.consultation import Consultation
from app.models.diagnostic_ia import DiagnosticIA
from app.models.feedback_ia import FeedbackIA

router = APIRouter(prefix="/api/v1/monitoring", tags=["Monitoring"])

JOURS_FR = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
MOIS_FR  = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
            'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

# PostgreSQL: round(float8, int) n'existe pas → on arrondit en Python
# PostgreSQL: CAST(boolean AS FLOAT) échoue → on utilise CASE WHEN … THEN 1.0 ELSE 0.0


def _bool_to_float(col):
    """boolean → float via CASE (compatible asyncpg)."""
    return case((col == True, 1.0), else_=0.0)  # noqa: E712


# ── GET /api/v1/monitoring/stats ──────────────────────────────────────────────
@router.get("/stats")
async def get_stats(
    periode: str = "week",
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    now = datetime.utcnow()
    if periode == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif periode == "month":
        start = now - timedelta(days=30)
    else:
        start = now - timedelta(days=7)

    mid     = medecin.id
    day_col = func.date_trunc("day", Consultation.created_at).label("jour")

    # ── 1. Consultations par jour ─────────────────────────────────────────────
    res = await db.execute(
        select(day_col, func.count(Consultation.id).label("cnt"))
        .where(Consultation.medecin_id == mid, Consultation.created_at >= start)
        .group_by(day_col)
        .order_by(day_col)
    )
    consult_par_jour = [
        {"jour": JOURS_FR[row.jour.weekday()], "count": row.cnt}
        for row in res.fetchall()
    ]

    # ── 2. SpO₂ par jour — avg() retourne float8, on arrondit en Python ──────
    spo2_expr = cast(Consultation.symptomes["saturation_o2"].astext, Float)
    res = await db.execute(
        select(
            day_col,
            func.avg(spo2_expr).label("avg_spo2"),
            func.min(spo2_expr).label("min_spo2"),
        )
        .where(
            Consultation.medecin_id == mid,
            Consultation.created_at >= start,
            Consultation.symptomes["saturation_o2"].astext.isnot(None),
        )
        .group_by(day_col)
        .order_by(day_col)
    )
    spo2_par_jour = [
        {
            "jour": JOURS_FR[row.jour.weekday()],
            "avg": round(float(row.avg_spo2), 1) if row.avg_spo2 is not None else None,
            "min": round(float(row.min_spo2), 1) if row.min_spo2 is not None else None,
        }
        for row in res.fetchall()
    ]

    # ── 3. Répartition pathologies — filtrée par période ─────────────────────
    patho_col = func.jsonb_extract_path_text(
        DiagnosticIA.maladies, "0", "nom"
    ).label("pathologie")
    res = await db.execute(
        select(patho_col, func.count(DiagnosticIA.id).label("cnt"))
        .join(Consultation, DiagnosticIA.consultation_id == Consultation.id)
        .where(Consultation.medecin_id == mid)
        .where(Consultation.created_at >= start)       # filtre période appliqué
        .where(DiagnosticIA.maladies.isnot(None))
        .group_by(patho_col)
        .order_by(func.count(DiagnosticIA.id).desc())
        .limit(6)
    )
    rows = res.fetchall()
    total = sum(r.cnt for r in rows) or 1
    patho_data = [
        {"name": row.pathologie, "value": round((row.cnt / total) * 100)}
        for row in rows
        if row.pathologie
    ]

    # ── 4. Concordance IA/Médecin — filtrée par période ──────────────────────
    week_col   = func.date_trunc("week", FeedbackIA.created_at).label("semaine")
    conc_float = _bool_to_float(FeedbackIA.concordance)
    res = await db.execute(
        select(
            week_col,
            func.avg(conc_float).label("taux"),
            func.count(FeedbackIA.id).label("nb"),
        )
        .join(DiagnosticIA, FeedbackIA.diagnostic_id == DiagnosticIA.id)
        .join(Consultation, DiagnosticIA.consultation_id == Consultation.id)
        .where(Consultation.medecin_id == mid)
        .where(FeedbackIA.created_at >= start)          # filtre période appliqué
        .where(FeedbackIA.concordance.isnot(None))
        .group_by(week_col)
        .order_by(week_col)
    )
    concordance_data = [
        {
            "date": f"S-{max(0, 6 - i)}",
            "val":  round(float(row.taux) * 100, 1) if row.taux is not None else 0,
            "nb":   row.nb,
        }
        for i, row in enumerate(res.fetchall())
    ]

    # ── 5. Base vs Équipe — filtrée par période ───────────────────────────────
    res = await db.execute(
        select(Consultation.created_at, Consultation.partage)
        .where(Consultation.medecin_id == mid)
        .where(Consultation.created_at >= start)        # filtre période appliqué
        .order_by(Consultation.created_at)
    )
    monthly: dict = OrderedDict()
    for row in res.fetchall():
        key   = row.created_at.strftime("%Y-%m")
        label = MOIS_FR[row.created_at.month - 1]
        if key not in monthly:
            monthly[key] = {"mois": label, "base": 0, "equipe": 0}
        partage = row.partage or {}
        if partage.get("actif"):
            monthly[key]["equipe"] += 1
        else:
            monthly[key]["base"] += 1

    return {
        "consult_par_jour": consult_par_jour,
        "spo2_par_jour":    spo2_par_jour,
        "patho_data":       patho_data,
        "concordance_data": concordance_data,
        "equipe_data":      list(monthly.values()),
    }


# ── GET /api/v1/monitoring/ia-metrics ────────────────────────────────────────
@router.get("/ia-metrics")
async def get_ia_metrics(
    db: AsyncSession = Depends(get_db),
    medecin=Depends(get_current_medecin),
):
    mid   = medecin.id
    now   = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Total diagnostics générés
    res = await db.execute(
        select(func.count(DiagnosticIA.id))
        .join(Consultation, DiagnosticIA.consultation_id == Consultation.id)
        .where(Consultation.medecin_id == mid)
    )
    total_diags = res.scalar_one() or 0

    # Taux de concordance global — CASE bool→float, arrondi en Python
    conc_float = _bool_to_float(FeedbackIA.concordance)
    res = await db.execute(
        select(func.avg(conc_float).label("taux"))
        .join(DiagnosticIA, FeedbackIA.diagnostic_id == DiagnosticIA.id)
        .join(Consultation, DiagnosticIA.consultation_id == Consultation.id)
        .where(Consultation.medecin_id == mid)
        .where(FeedbackIA.concordance.isnot(None))
    )
    raw = res.scalar_one()
    concordance_rate = round(float(raw) * 100, 1) if raw is not None else 0.0

    # Temps moyen d'inférence (ms → s), arrondi en Python
    res = await db.execute(
        select(func.avg(cast(DiagnosticIA.duree_inference_ms, Float)).label("avg_ms"))
        .join(Consultation, DiagnosticIA.consultation_id == Consultation.id)
        .where(Consultation.medecin_id == mid)
        .where(DiagnosticIA.duree_inference_ms.isnot(None))
    )
    raw_ms = res.scalar_one()
    avg_inference = round(float(raw_ms) / 1000.0, 2) if raw_ms is not None else 0.0

    # Alertes déclenchées aujourd'hui (cas urgents/critiques mis à jour ce jour)
    res = await db.execute(
        select(func.count(Consultation.id))
        .where(Consultation.medecin_id == mid)
        .where(Consultation.statut_clinique.in_(["urgent", "critique"]))
        .where(Consultation.updated_at >= today)
    )
    alertes_today = res.scalar_one() or 0

    # Delta diagnostics 7 derniers jours vs 7 jours précédents
    last_7 = now - timedelta(days=7)
    prev_7 = now - timedelta(days=14)

    res_cur = await db.execute(
        select(func.count(DiagnosticIA.id))
        .join(Consultation, DiagnosticIA.consultation_id == Consultation.id)
        .where(Consultation.medecin_id == mid, DiagnosticIA.created_at >= last_7)
    )
    res_prv = await db.execute(
        select(func.count(DiagnosticIA.id))
        .join(Consultation, DiagnosticIA.consultation_id == Consultation.id)
        .where(
            Consultation.medecin_id == mid,
            DiagnosticIA.created_at >= prev_7,
            DiagnosticIA.created_at < last_7,
        )
    )
    delta = (res_cur.scalar_one() or 0) - (res_prv.scalar_one() or 0)

    return {
        "total_diagnostics": total_diags,
        "concordance_rate":  concordance_rate,
        "avg_inference_s":   avg_inference,
        "alertes_today":     alertes_today,
        "delta_diags_7j":    delta,
    }

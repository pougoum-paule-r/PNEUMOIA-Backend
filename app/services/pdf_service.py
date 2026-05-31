# app/services/pdf_service.py
"""
Génère le bilan PDF d'une consultation.
Utilise WeasyPrint (pip install weasyprint).
Si WeasyPrint n'est pas installé, retourne un PDF minimal avec reportlab.
"""
from __future__ import annotations
import io
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.consultation import Consultation
    from app.models.patient import Patient


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: Arial, sans-serif; font-size: 12px; color: #1e293b; margin: 40px; }}
  .header {{ text-align: center; border-bottom: 2px solid #2563eb; padding-bottom: 16px; margin-bottom: 24px; }}
  .header h1 {{ color: #2563eb; font-size: 20px; margin: 0; }}
  .header p {{ color: #64748b; margin: 4px 0; }}
  .badge {{ display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: bold; }}
  .badge-urgent   {{ background: #fef2f2; color: #dc2626; border: 1px solid #dc2626; }}
  .badge-surveille {{ background: #fffbeb; color: #d97706; border: 1px solid #d97706; }}
  .badge-stable   {{ background: #f0fdf4; color: #16a34a; border: 1px solid #16a34a; }}
  section {{ margin-bottom: 20px; }}
  section h2 {{ font-size: 13px; color: #2563eb; border-left: 4px solid #2563eb; padding-left: 8px; margin-bottom: 8px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 11px; }}
  td {{ padding: 5px 8px; border-bottom: 1px solid #e2e8f0; }}
  td:first-child {{ font-weight: 600; color: #475569; width: 40%; }}
  .diag-box {{ background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 12px; }}
  .diag-name {{ font-size: 16px; font-weight: bold; color: #1d4ed8; }}
  .pct {{ font-size: 13px; color: #2563eb; }}
  ul {{ margin: 4px 0 0 0; padding-left: 18px; }}
  li {{ margin-bottom: 3px; }}
  .alerte {{ background: #fef2f2; border: 1px solid #fca5a5; border-radius: 6px; padding: 10px; color: #991b1b; margin-bottom: 8px; }}
  .footer {{ border-top: 1px solid #e2e8f0; padding-top: 10px; color: #94a3b8; font-size: 10px; text-align: center; }}
</style>
</head>
<body>
<div class="header">
  <h1>🫁 PneumoIA — Bilan de Consultation</h1>
  <p>Généré le {date_generation} | Consultation #{consultation_id}</p>
</div>

<section>
  <h2>👤 Patient</h2>
  <table>
    <tr><td>Nom complet</td><td>{civilite} {prenom} {nom}</td></tr>
    <tr><td>Date de naissance</td><td>{date_naissance}</td></tr>
    <tr><td>Téléphone</td><td>{telephone}</td></tr>
    <tr><td>Groupe sanguin</td><td>{groupe_sanguin}</td></tr>
    <tr><td>Religion</td><td>{religion}</td></tr>
    {alerte_religieuse}
  </table>
</section>

<section>
  <h2>🤖 Diagnostic IA</h2>
  {bloc_diagnostic}
</section>

{bloc_criteres}

{bloc_examens}

<section>
  <h2>💊 Prescription médicale</h2>
  <table>
    <tr><td>Médicaments</td><td>{medicaments}</td></tr>
    <tr><td>Conseils à domicile</td><td>{conseils_maison}</td></tr>
    <tr><td>Recommandations</td><td>{recommandations}</td></tr>
    <tr><td>Arrêt de travail</td><td>{arret_travail}</td></tr>
    <tr><td>Hospitalisation</td><td>{hospitalisation}</td></tr>
    <tr><td>Prochain suivi</td><td>{suivi}</td></tr>
  </table>
</section>

{bloc_observations}

<div class="footer">
  Document généré par PneumoIA — Plateforme de diagnostic pneumologique assisté par IA<br>
  Ce document est confidentiel et destiné exclusivement au patient et à son équipe médicale.
</div>
</body>
</html>
"""


async def generer_bilan_pdf(consultation: "Consultation", patient: "Patient") -> bytes:
    diag = consultation.diagnostic
    maladies = diag.maladies if diag else []
    prescriptions = consultation.prescriptions or {}
    principale = maladies[0] if maladies else {}

    # ── Bloc diagnostic ──────────────────────────────────────────
    etat = principale.get("etat", "stable")
    badge_class = {"critique": "badge-urgent", "urgent": "badge-urgent",
                   "surveille": "badge-surveille"}.get(etat, "badge-stable")

    if principale:
        differentials = "".join(
            f"<tr><td>{m['nom']}</td><td>{m['pct']}%</td></tr>"
            for m in maladies[1:]
        )
        bloc_diagnostic = f"""
        <div class="diag-box">
          <div class="diag-name">{principale.get('nom','—')}</div>
          <div class="pct">Confiance : {principale.get('pct',0)}%
            <span class="badge {badge_class}">{etat.upper()}</span>
          </div>
        </div>
        {f'<table style="margin-top:8px"><tr><td colspan="2"><b>Diagnostics différentiels</b></td></tr>{differentials}</table>' if differentials else ''}
        """
    else:
        bloc_diagnostic = "<p>Diagnostic non disponible</p>"

    # ── Critères validés ─────────────────────────────────────────
    criteres = principale.get("criteres_valides", [])
    if criteres:
        items = "".join(f"<li>{c}</li>" for c in criteres)
        bloc_criteres = f"<section><h2>✅ Critères cliniques validés</h2><ul>{items}</ul></section>"
    else:
        bloc_criteres = ""

    # ── Examens recommandés ──────────────────────────────────────
    examens = principale.get("examens_suggeres", [])
    if examens:
        items = "".join(f"<li>{e}</li>" for e in examens)
        bloc_examens = f"<section><h2>🔬 Examens recommandés</h2><ul>{items}</ul></section>"
    else:
        bloc_examens = ""

    # ── Alerte religieuse ────────────────────────────────────────
    alerte_relig = ""
    if patient.religion == "temoin_jehovah":
        alerte_relig = '<tr><td colspan="2"><div class="alerte">⚠️ TÉMOIN DE JÉHOVAH — Refus de transfusion sanguine</div></td></tr>'

    # ── Observations médecin ─────────────────────────────────────
    if consultation.observations:
        bloc_obs = f"""
        <section>
          <h2>📝 Observations du médecin</h2>
          <p style="background:#f8fafc;padding:10px;border-radius:6px;border:1px solid #e2e8f0">
            {consultation.observations}
          </p>
        </section>"""
    else:
        bloc_obs = ""

    html = HTML_TEMPLATE.format(
        date_generation  = datetime.now().strftime("%d/%m/%Y à %H:%M"),
        consultation_id  = consultation.id,
        civilite         = patient.civilite or "",
        prenom           = patient.prenom,
        nom              = patient.nom,
        date_naissance   = str(patient.date_naissance) if patient.date_naissance else "Non renseignée",
        telephone        = patient.telephone or "Non renseigné",
        groupe_sanguin   = patient.groupe_sanguin or "Non renseigné",
        religion         = patient.religion or "Non renseignée",
        alerte_religieuse = alerte_relig,
        bloc_diagnostic  = bloc_diagnostic,
        bloc_criteres    = bloc_criteres,
        bloc_examens     = bloc_examens,
        medicaments      = prescriptions.get("medicaments") or "—",
        conseils_maison  = prescriptions.get("conseils_maison") or "—",
        recommandations  = prescriptions.get("recommandations") or "—",
        arret_travail    = f"Oui — {prescriptions.get('duree_arret','?')} jours" if prescriptions.get("arret_travail") else "Non",
        hospitalisation  = f"Oui — {prescriptions.get('motif_hospitalisation','')}" if prescriptions.get("hospitalisation") else "Non",
        suivi            = prescriptions.get("suivi") or "À définir",
        bloc_observations = bloc_obs,
    )

    # ── Génération PDF ───────────────────────────────────────────
    try:
        from weasyprint import HTML
        return HTML(string=html).write_pdf()
    except ImportError:
        # Fallback : reportlab si WeasyPrint absent
        return _pdf_fallback_reportlab(patient, consultation, principale)


def _pdf_fallback_reportlab(patient, consultation, principale) -> bytes:
    """PDF minimal si WeasyPrint non installé."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4

        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        w, h = A4
        c.setFont("Helvetica-Bold", 16)
        c.drawString(60, h - 60, "PneumoIA — Bilan de Consultation")
        c.setFont("Helvetica", 11)
        c.drawString(60, h - 90,  f"Patient : {patient.civilite or ''} {patient.prenom} {patient.nom}")
        c.drawString(60, h - 110, f"Consultation : {consultation.id}")
        c.drawString(60, h - 130, f"Statut : {consultation.statut}")
        if principale:
            c.drawString(60, h - 160, f"Diagnostic IA : {principale.get('nom','—')} ({principale.get('pct',0)}%)")
        c.save()
        return buf.getvalue()
    except ImportError:
        return b"%PDF-1.4 minimal"
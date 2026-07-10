# app/services/pdf_service.py
"""Génère le bilan PDF d'une consultation avec ReportLab (pure Python, Windows compatible)."""
from __future__ import annotations
import io
from datetime import datetime, date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.consultation import Consultation
    from app.models.patient import Patient

RELIGIONS = {
    "temoin_jehovah": "Témoin de Jéhovah",
    "musulman":       "Musulman(e)",
    "chretien":       "Chrétien(ne)",
    "catholique":     "Catholique",
    "protestant":     "Protestant(e)",
    "autre":          "Autre",
    "aucune":         "Aucune",
}

GROUPES = {
    "A+": "A+", "A-": "A-", "B+": "B+", "B-": "B-",
    "AB+": "AB+", "AB-": "AB-", "O+": "O+", "O-": "O-",
}


_SUBSCRIPT_MAP = str.maketrans({
    '₀': '0', '₁': '1', '₂': '2', '₃': '3',
    '₄': '4', '₅': '5', '₆': '6', '₇': '7',
    '₈': '8', '₉': '9',
    '²': '2', '³': '3',
})

def _clean(s: str) -> str:
    return str(s).translate(_SUBSCRIPT_MAP)


def _age(dob) -> str:
    if not dob:
        return "—"
    try:
        today = date.today()
        d = dob if isinstance(dob, date) else datetime.strptime(str(dob), "%Y-%m-%d").date()
        return f"{today.year - d.year - ((today.month, today.day) < (d.month, d.day))} ans"
    except Exception:
        return str(dob)


async def generer_bilan_pdf(consultation: "Consultation", patient: "Patient", diag=None) -> bytes:
    maladies      = (diag.maladies if diag else []) or []
    prescriptions = consultation.prescriptions or {}
    principale    = maladies[0] if maladies else {}

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable,
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        buf = io.BytesIO()
        W_PAGE, H_PAGE = A4

        doc = SimpleDocTemplate(
            buf, pagesize=A4,
            leftMargin=18*mm, rightMargin=18*mm,
            topMargin=16*mm, bottomMargin=16*mm,
        )

        # ── Palette ───────────────────────────────────────────────
        C_BLUE      = colors.HexColor("#1d4ed8")
        C_BLUE_MID  = colors.HexColor("#2563eb")
        C_BLUE_LIGHT= colors.HexColor("#dbeafe")
        C_BLUE_PALE = colors.HexColor("#eff6ff")
        C_GRAY_HDR  = colors.HexColor("#f1f5f9")
        C_GRAY_BDR  = colors.HexColor("#cbd5e1")
        C_TEXT      = colors.HexColor("#0f172a")
        C_MUTED     = colors.HexColor("#64748b")
        C_RED       = colors.HexColor("#dc2626")
        C_RED_BG    = colors.HexColor("#fef2f2")
        C_RED_BDR   = colors.HexColor("#fca5a5")
        C_GREEN     = colors.HexColor("#16a34a")
        C_GREEN_BG  = colors.HexColor("#f0fdf4")
        C_ORANGE    = colors.HexColor("#d97706")
        C_WHITE     = colors.white

        W = W_PAGE - 36*mm  # usable width

        # ── Styles ────────────────────────────────────────────────
        def ps(name, **kw):
            return ParagraphStyle(name, **kw)

        S_HDR_TITLE = ps("ht", fontName="Helvetica-Bold", fontSize=20,
                          textColor=C_WHITE, alignment=TA_CENTER, leading=26)
        S_HDR_SUB   = ps("hs", fontName="Helvetica", fontSize=9,
                          textColor=colors.HexColor("#bfdbfe"), alignment=TA_CENTER, leading=13)
        S_SEC       = ps("sec", fontName="Helvetica-Bold", fontSize=11,
                          textColor=C_BLUE, leading=14)
        S_LBL       = ps("lbl", fontName="Helvetica-Bold", fontSize=9,
                          textColor=colors.HexColor("#334155"), leading=13)
        S_VAL       = ps("val", fontName="Helvetica", fontSize=9,
                          textColor=C_TEXT, leading=13)
        S_VAL_BLUE  = ps("valb", fontName="Helvetica-Bold", fontSize=11,
                          textColor=C_BLUE_MID, leading=14)
        S_BADGE_OK  = ps("bok", fontName="Helvetica-Bold", fontSize=9,
                          textColor=C_GREEN, leading=13)
        S_BADGE_WARN= ps("bwarn", fontName="Helvetica-Bold", fontSize=9,
                          textColor=C_ORANGE, leading=13)
        S_BADGE_ERR = ps("berr", fontName="Helvetica-Bold", fontSize=9,
                          textColor=C_RED, leading=13)
        S_ALERT_LBL = ps("al", fontName="Helvetica-Bold", fontSize=9,
                          textColor=C_RED, leading=13)
        S_ALERT_VAL = ps("av", fontName="Helvetica", fontSize=9,
                          textColor=C_RED, leading=13)
        S_BULLET    = ps("blt", fontName="Helvetica", fontSize=9,
                          textColor=C_TEXT, leading=14, leftIndent=4)
        S_FOOTER    = ps("ft", fontName="Helvetica", fontSize=8,
                          textColor=C_MUTED, alignment=TA_CENTER, leading=12)
        S_OBS       = ps("obs", fontName="Helvetica", fontSize=9,
                          textColor=C_TEXT, leading=14)

        # ── Helper: table data row ─────────────────────────────────
        def row(label, value, lbl_style=S_LBL, val_style=S_VAL):
            return [Paragraph(label, lbl_style), Paragraph(str(value) if value else "Aucun", val_style)]

        def section_table(data, col_w=(0.38, 0.62), style_extra=None):
            ts = TableStyle([
                ("GRID",         (0,0), (-1,-1), 0.5, C_GRAY_BDR),
                ("BACKGROUND",   (0,0), (0,-1),  C_GRAY_HDR),
                ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
                ("LEFTPADDING",  (0,0), (-1,-1), 9),
                ("RIGHTPADDING", (0,0), (-1,-1), 9),
                ("TOPPADDING",   (0,0), (-1,-1), 6),
                ("BOTTOMPADDING",(0,0), (-1,-1), 6),
                ("ROWBACKGROUNDS",(0,0),(-1,-1), [C_WHITE, C_GRAY_HDR]),
            ])
            if style_extra:
                ts.add(*style_extra)
            t = Table(data, colWidths=[W*col_w[0], W*col_w[1]])
            t.setStyle(ts)
            return t

        story = []

        # ── HEADER BLOCK ─────────────────────────────────────────
        hdr_data = [[
            Paragraph("PneumoIA — Bilan de Consultation", S_HDR_TITLE),
        ]]
        sub_data = [[
            Paragraph(
                f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}  ·  "
                f"Consultation #{consultation.id}  ·  "
                f"Dr. {getattr(consultation, 'medecin_nom', '')}",
                S_HDR_SUB),
        ]]
        hdr_t = Table([[Paragraph("PneumoIA — Bilan de Consultation", S_HDR_TITLE)]], colWidths=[W])
        hdr_t.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,-1), C_BLUE),
            ("TOPPADDING",   (0,0), (-1,-1), 14),
            ("BOTTOMPADDING",(0,0), (-1,-1), 8),
            ("LEFTPADDING",  (0,0), (-1,-1), 12),
            ("RIGHTPADDING", (0,0), (-1,-1), 12),
            ("ROUNDEDCORNERS", [4]),
        ]))
        sub_t = Table([[Paragraph(
            f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}  ·  Consultation #{consultation.id}"
            f"  ·  Patient ID : {patient.id}",
            S_HDR_SUB)]], colWidths=[W])
        sub_t.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,-1), colors.HexColor("#1e40af")),
            ("TOPPADDING",   (0,0), (-1,-1), 6),
            ("BOTTOMPADDING",(0,0), (-1,-1), 10),
            ("LEFTPADDING",  (0,0), (-1,-1), 12),
            ("RIGHTPADDING", (0,0), (-1,-1), 12),
        ]))
        story.append(hdr_t)
        story.append(sub_t)
        story.append(Spacer(1, 14))

        # ── PATIENT ───────────────────────────────────────────────
        story.append(Paragraph("Patient", S_SEC))
        story.append(Spacer(1, 4))

        religion_label = RELIGIONS.get(patient.religion or "", patient.religion or "Aucun")
        pat_rows = [
            row("ID Patient",       patient.id),
            row("Nom complet",      f"{patient.civilite or ''} {patient.prenom} {patient.nom}".strip()),
            row("Date de naissance", str(patient.date_naissance) if patient.date_naissance else "—"),
            row("Age",              _age(patient.date_naissance)),
            row("Telephone",        patient.telephone or "Aucun"),
            row("Groupe sanguin",   patient.groupe_sanguin or "Aucun"),
            row("Religion",         religion_label),
        ]
        if patient.religion == "temoin_jehovah":
            pat_rows.append([
                Paragraph("[!] Alerte medicale", S_ALERT_LBL),
                Paragraph("TEMOIN DE JEHOVAH - Refus formel de transfusion sanguine", S_ALERT_VAL),
            ])

        pat_t = Table(pat_rows, colWidths=[W*0.36, W*0.64])
        alert_style = TableStyle([
            ("GRID",         (0,0), (-1,-1), 0.5, C_GRAY_BDR),
            ("BACKGROUND",   (0,0), (0,-1),  C_GRAY_HDR),
            ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING",  (0,0), (-1,-1), 9),
            ("RIGHTPADDING", (0,0), (-1,-1), 9),
            ("TOPPADDING",   (0,0), (-1,-1), 6),
            ("BOTTOMPADDING",(0,0), (-1,-1), 6),
            ("ROWBACKGROUNDS",(0,0),(-1,-1), [C_WHITE, C_GRAY_HDR]),
        ])
        if patient.religion == "temoin_jehovah":
            last = len(pat_rows) - 1
            alert_style.add("BACKGROUND", (0, last), (-1, last), C_RED_BG)
            alert_style.add("GRID",       (0, last), (-1, last), 0.5, C_RED_BDR)
        pat_t.setStyle(alert_style)
        story.append(pat_t)
        story.append(Spacer(1, 14))

        # ── DIAGNOSTIC ─────────────────────────────────────────────
        story.append(Paragraph("Diagnostic", S_SEC))
        story.append(Spacer(1, 4))

        if principale:
            etat = principale.get("etat", "stable")
            etat_label = {"critique": "CRITIQUE", "urgent": "URGENT", "surveille": "SURVEILLÉ"}.get(etat, "STABLE")
            etat_style = {"critique": S_BADGE_ERR, "urgent": S_BADGE_ERR, "surveille": S_BADGE_WARN}.get(etat, S_BADGE_OK)
            etat_bg    = {"critique": C_RED_BG, "urgent": C_RED_BG, "surveille": colors.HexColor("#fffbeb")}.get(etat, C_GREEN_BG)

            diag_rows = [
                [Paragraph("Pathologie principale", S_LBL), Paragraph(principale.get("nom","—"), S_VAL_BLUE)],
                [Paragraph("État clinique",          S_LBL), Paragraph(etat_label, etat_style)],
            ]
            if len(maladies) > 1:
                diff_txt = " · ".join(m['nom'] for m in maladies[1:4])
                diag_rows.append([Paragraph("Diagnostics différentiels", S_LBL), Paragraph(diff_txt, S_VAL)])

            diag_t = Table(diag_rows, colWidths=[W*0.36, W*0.64])
            diag_ts = TableStyle([
                ("GRID",         (0,0), (-1,-1), 0.5, colors.HexColor("#bfdbfe")),
                ("BACKGROUND",   (0,0), (0,-1),  C_BLUE_LIGHT),
                ("BACKGROUND",   (1,0), (1,-1),  C_BLUE_PALE),
                ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
                ("LEFTPADDING",  (0,0), (-1,-1), 9),
                ("RIGHTPADDING", (0,0), (-1,-1), 9),
                ("TOPPADDING",   (0,0), (-1,-1), 7),
                ("BOTTOMPADDING",(0,0), (-1,-1), 7),
            ])
            # Coloriser la ligne état clinique
            etat_row_idx = 2
            diag_ts.add("BACKGROUND", (1, etat_row_idx), (1, etat_row_idx), etat_bg)
            diag_t.setStyle(diag_ts)
            story.append(diag_t)
        else:
            story.append(Paragraph("Diagnostic non encore disponible pour cette consultation.", S_VAL))

        story.append(Spacer(1, 14))

        # ── CRITÈRES ──────────────────────────────────────────────
        criteres = principale.get("criteres_valides", [])
        if criteres:
            story.append(Paragraph("Critères cliniques validés", S_SEC))
            story.append(Spacer(1, 4))
            crit_rows = [[Paragraph(f"[+]  {_clean(c)}", S_BULLET)] for c in criteres]
            crit_t = Table(crit_rows, colWidths=[W])
            crit_t.setStyle(TableStyle([
                ("GRID",         (0,0), (-1,-1), 0.5, C_GRAY_BDR),
                ("ROWBACKGROUNDS",(0,0),(-1,-1), [C_WHITE, C_GRAY_HDR]),
                ("LEFTPADDING",  (0,0), (-1,-1), 10),
                ("TOPPADDING",   (0,0), (-1,-1), 5),
                ("BOTTOMPADDING",(0,0), (-1,-1), 5),
            ]))
            story.append(crit_t)
            story.append(Spacer(1, 14))

        # ── EXAMENS ───────────────────────────────────────────────
        examens = principale.get("examens_suggeres", [])
        if examens:
            story.append(Paragraph("Examens recommandés", S_SEC))
            story.append(Spacer(1, 4))
            exam_rows = [[Paragraph(f"->  {e}", S_BULLET)] for e in examens]
            exam_t = Table(exam_rows, colWidths=[W])
            exam_t.setStyle(TableStyle([
                ("GRID",         (0,0), (-1,-1), 0.5, C_GRAY_BDR),
                ("ROWBACKGROUNDS",(0,0),(-1,-1), [C_WHITE, C_GRAY_HDR]),
                ("LEFTPADDING",  (0,0), (-1,-1), 10),
                ("TOPPADDING",   (0,0), (-1,-1), 5),
                ("BOTTOMPADDING",(0,0), (-1,-1), 5),
            ]))
            story.append(exam_t)
            story.append(Spacer(1, 14))

        # ── RECOMMANDATIONS ───────────────────────────────────────
        recommandations = (diag.recommandations if diag else None) or principale.get("recommandations", [])
        if recommandations:
            story.append(Paragraph("Recommandations médicales", S_SEC))
            story.append(Spacer(1, 4))
            reco_rows = [[Paragraph(f"[+]  {_clean(r)}", S_BULLET)] for r in recommandations]
            reco_t = Table(reco_rows, colWidths=[W])
            reco_t.setStyle(TableStyle([
                ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#bfdbfe")),
                ("BACKGROUND",    (0,0), (-1,-1), C_BLUE_PALE),
                ("ROWBACKGROUNDS",(0,0), (-1,-1), [C_BLUE_PALE, colors.HexColor("#dbeafe")]),
                ("LEFTPADDING",   (0,0), (-1,-1), 10),
                ("TOPPADDING",    (0,0), (-1,-1), 5),
                ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ]))
            story.append(reco_t)
            story.append(Spacer(1, 14))

        # ── PRESCRIPTION ──────────────────────────────────────────
        story.append(Paragraph("Prescription médicale", S_SEC))
        story.append(Spacer(1, 4))
        arret = f"Oui — {prescriptions.get('duree_arret','?')} jours" if prescriptions.get("arret_travail") else "Non"
        hospi = f"Oui — {prescriptions.get('motif_hospitalisation','')}" if prescriptions.get("hospitalisation") else "Non"
        presc_rows = [
            row("Médicaments",     prescriptions.get("medicaments") or "Aucun"),
            row("Conseils à domicile", prescriptions.get("conseils_maison") or "Aucun"),
            row("Recommandations", prescriptions.get("recommandations") or "Aucun"),
            row("Arrêt de travail", arret),
            row("Hospitalisation",  hospi),
            row("Prochain suivi",   prescriptions.get("suivi") or "À définir"),
        ]
        story.append(section_table(presc_rows, (0.36, 0.64)))
        story.append(Spacer(1, 14))

        # ── OBSERVATIONS ──────────────────────────────────────────
        if consultation.observations:
            story.append(Paragraph("Observations du médecin", S_SEC))
            story.append(Spacer(1, 4))
            obs_t = Table([[Paragraph(consultation.observations, S_OBS)]], colWidths=[W])
            obs_t.setStyle(TableStyle([
                ("BOX",         (0,0), (-1,-1), 0.5, C_GRAY_BDR),
                ("BACKGROUND",  (0,0), (-1,-1), C_GRAY_HDR),
                ("LEFTPADDING", (0,0), (-1,-1), 10),
                ("RIGHTPADDING",(0,0), (-1,-1), 10),
                ("TOPPADDING",  (0,0), (-1,-1), 8),
                ("BOTTOMPADDING",(0,0),(-1,-1), 8),
            ]))
            story.append(obs_t)
            story.append(Spacer(1, 14))

        # ── PIED DE PAGE ──────────────────────────────────────────
        story.append(HRFlowable(width="100%", thickness=0.5, color=C_GRAY_BDR, spaceAfter=6))
        story.append(Paragraph(
            "Document généré par <b>PneumoIA</b> — Plateforme de suivi pneumologique<br/>"
            "Ce document est confidentiel et destiné exclusivement au patient et à son équipe médicale.",
            S_FOOTER))

        doc.build(story)
        return buf.getvalue()

    except Exception:
        return b"%PDF-1.4\n%%EOF"


async def generer_dossier_pdf(consultations_avec_diag: list, patient) -> bytes:
    """PDF complet du dossier patient : toutes les consultations en un seul document."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable, PageBreak,
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        buf = io.BytesIO()
        W_PAGE, _ = A4
        doc = SimpleDocTemplate(buf, pagesize=A4,
            leftMargin=18*mm, rightMargin=18*mm,
            topMargin=16*mm, bottomMargin=16*mm)
        W = W_PAGE - 36*mm

        C_BLUE       = colors.HexColor("#1d4ed8")
        C_BLUE_MID   = colors.HexColor("#2563eb")
        C_BLUE_LIGHT = colors.HexColor("#dbeafe")
        C_BLUE_PALE  = colors.HexColor("#eff6ff")
        C_GRAY_HDR   = colors.HexColor("#f1f5f9")
        C_GRAY_BDR   = colors.HexColor("#cbd5e1")
        C_TEXT       = colors.HexColor("#0f172a")
        C_MUTED      = colors.HexColor("#64748b")
        C_RED        = colors.HexColor("#dc2626")
        C_RED_BG     = colors.HexColor("#fef2f2")
        C_RED_BDR    = colors.HexColor("#fca5a5")
        C_GREEN      = colors.HexColor("#16a34a")
        C_GREEN_BG   = colors.HexColor("#f0fdf4")
        C_ORANGE     = colors.HexColor("#d97706")
        C_WHITE      = colors.white

        def ps(name, **kw): return ParagraphStyle(name, **kw)
        S_HDR_TITLE = ps("ht2", fontName="Helvetica-Bold", fontSize=18, textColor=C_WHITE, alignment=TA_CENTER, leading=24)
        S_HDR_SUB   = ps("hs2", fontName="Helvetica", fontSize=9, textColor=colors.HexColor("#bfdbfe"), alignment=TA_CENTER, leading=13)
        S_SEC       = ps("s2", fontName="Helvetica-Bold", fontSize=11, textColor=C_BLUE, leading=14)
        S_SEC2      = ps("s22", fontName="Helvetica-Bold", fontSize=10, textColor=C_BLUE_MID, leading=13)
        S_LBL       = ps("l2", fontName="Helvetica-Bold", fontSize=9, textColor=colors.HexColor("#334155"), leading=13)
        S_VAL       = ps("v2", fontName="Helvetica", fontSize=9, textColor=C_TEXT, leading=13)
        S_VAL_BLUE  = ps("vb2", fontName="Helvetica-Bold", fontSize=11, textColor=C_BLUE_MID, leading=14)
        S_BADGE_OK  = ps("bok2", fontName="Helvetica-Bold", fontSize=9, textColor=C_GREEN, leading=13)
        S_BADGE_WARN= ps("bw2", fontName="Helvetica-Bold", fontSize=9, textColor=C_ORANGE, leading=13)
        S_BADGE_ERR = ps("be2", fontName="Helvetica-Bold", fontSize=9, textColor=C_RED, leading=13)
        S_BULLET    = ps("blt2", fontName="Helvetica", fontSize=9, textColor=C_TEXT, leading=14, leftIndent=4)
        S_FOOTER    = ps("ft2", fontName="Helvetica", fontSize=8, textColor=C_MUTED, alignment=TA_CENTER, leading=12)
        S_OBS       = ps("ob2", fontName="Helvetica", fontSize=9, textColor=C_TEXT, leading=14)
        S_ALERT_LBL = ps("al2", fontName="Helvetica-Bold", fontSize=9, textColor=C_RED, leading=13)
        S_ALERT_VAL = ps("av2", fontName="Helvetica", fontSize=9, textColor=C_RED, leading=13)

        def row(label, value):
            return [Paragraph(label, S_LBL), Paragraph(str(value) if value else "Aucun", S_VAL)]

        def simple_table(data, col_w=(0.36, 0.64)):
            t = Table(data, colWidths=[W*col_w[0], W*col_w[1]])
            t.setStyle(TableStyle([
                ("GRID",         (0,0),(-1,-1), 0.5, C_GRAY_BDR),
                ("BACKGROUND",   (0,0),(0,-1),  C_GRAY_HDR),
                ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
                ("LEFTPADDING",  (0,0),(-1,-1), 9),
                ("RIGHTPADDING", (0,0),(-1,-1), 9),
                ("TOPPADDING",   (0,0),(-1,-1), 6),
                ("BOTTOMPADDING",(0,0),(-1,-1), 6),
                ("ROWBACKGROUNDS",(0,0),(-1,-1),[C_WHITE, C_GRAY_HDR]),
            ]))
            return t

        story = []

        # ── Page de garde ─────────────────────────────────────────
        religion_label = RELIGIONS.get(patient.religion or "", patient.religion or "Aucune")
        hdr_t = Table([[Paragraph("PneumoIA — Dossier Patient Complet", S_HDR_TITLE)]], colWidths=[W])
        hdr_t.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,-1), C_BLUE),
            ("TOPPADDING",   (0,0),(-1,-1), 14),
            ("BOTTOMPADDING",(0,0),(-1,-1), 8),
            ("LEFTPADDING",  (0,0),(-1,-1), 12),
            ("RIGHTPADDING", (0,0),(-1,-1), 12),
        ]))
        sub_t = Table([[Paragraph(
            f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} · {len(consultations_avec_diag)} consultation(s) · Patient ID : {patient.id}",
            S_HDR_SUB)]], colWidths=[W])
        sub_t.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,-1), colors.HexColor("#1e40af")),
            ("TOPPADDING",   (0,0),(-1,-1), 6),
            ("BOTTOMPADDING",(0,0),(-1,-1), 10),
            ("LEFTPADDING",  (0,0),(-1,-1), 12),
            ("RIGHTPADDING", (0,0),(-1,-1), 12),
        ]))
        story += [hdr_t, sub_t, Spacer(1, 14)]

        story.append(Paragraph("Informations Patient", S_SEC))
        story.append(Spacer(1, 4))
        pat_rows = [
            row("Nom complet",      f"{patient.civilite or ''} {patient.prenom} {patient.nom}".strip()),
            row("Date de naissance", str(patient.date_naissance) if patient.date_naissance else "—"),
            row("Âge",              _age(patient.date_naissance)),
            row("Téléphone",        patient.telephone or "Aucun"),
            row("Groupe sanguin",   patient.groupe_sanguin or "Aucun"),
            row("Religion",         religion_label),
        ]
        if patient.religion == "temoin_jehovah":
            pat_rows.append([
                Paragraph("[!] Alerte médicale", S_ALERT_LBL),
                Paragraph("TÉMOIN DE JÉHOVAH — Refus transfusion sanguine", S_ALERT_VAL),
            ])
        pat_t = Table(pat_rows, colWidths=[W*0.36, W*0.64])
        ts = TableStyle([
            ("GRID",(0,0),(-1,-1),0.5,C_GRAY_BDR),
            ("BACKGROUND",(0,0),(0,-1),C_GRAY_HDR),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("LEFTPADDING",(0,0),(-1,-1),9),
            ("RIGHTPADDING",(0,0),(-1,-1),9),
            ("TOPPADDING",(0,0),(-1,-1),6),
            ("BOTTOMPADDING",(0,0),(-1,-1),6),
            ("ROWBACKGROUNDS",(0,0),(-1,-1),[C_WHITE, C_GRAY_HDR]),
        ])
        if patient.religion == "temoin_jehovah":
            last = len(pat_rows) - 1
            ts.add("BACKGROUND",(0,last),(-1,last),C_RED_BG)
            ts.add("GRID",(0,last),(-1,last),0.5,C_RED_BDR)
        pat_t.setStyle(ts)
        story.append(pat_t)

        # ── Une section par consultation ───────────────────────────
        for i, (c, diag) in enumerate(consultations_avec_diag):
            story.append(PageBreak())

            maladies   = (diag.maladies if diag else []) or []
            presc      = c.prescriptions or {}
            principale = maladies[0] if maladies else {}
            statut_lbl = {"terminee": "Terminée", "en_attente": "En attente", "annulee": "Annulée"}.get(c.statut, c.statut)
            date_c     = c.created_at.strftime("%d/%m/%Y à %H:%M") if c.created_at else "—"

            # En-tête consultation
            c_hdr = Table([[Paragraph(f"Consultation #{i+1} — {date_c}  [{statut_lbl}]", S_HDR_TITLE)]], colWidths=[W])
            c_hdr.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#1e40af")),
                ("TOPPADDING",(0,0),(-1,-1),10),
                ("BOTTOMPADDING",(0,0),(-1,-1),10),
                ("LEFTPADDING",(0,0),(-1,-1),12),
                ("RIGHTPADDING",(0,0),(-1,-1),12),
            ]))
            story += [c_hdr, Spacer(1, 12)]

            # Diagnostic
            story.append(Paragraph("Diagnostic IA", S_SEC))
            story.append(Spacer(1, 4))
            if principale:
                etat = principale.get("etat", "stable")
                etat_label = {"critique":"CRITIQUE","urgent":"URGENT","surveille":"SURVEILLÉ"}.get(etat,"STABLE")
                etat_style = {"critique":S_BADGE_ERR,"urgent":S_BADGE_ERR,"surveille":S_BADGE_WARN}.get(etat,S_BADGE_OK)
                diag_rows = [
                    [Paragraph("Pathologie principale", S_LBL), Paragraph(principale.get("nom","—"), S_VAL_BLUE)],
                    [Paragraph("Confiance IA",          S_LBL), Paragraph(f"{principale.get('pct', 0)}%", S_VAL)],
                    [Paragraph("État clinique",          S_LBL), Paragraph(etat_label, etat_style)],
                ]
                if len(maladies) > 1:
                    diff_txt = " · ".join(m.get('nom','') for m in maladies[1:4])
                    diag_rows.append([Paragraph("Diagnostics différentiels", S_LBL), Paragraph(diff_txt, S_VAL)])
                diag_t = Table(diag_rows, colWidths=[W*0.36, W*0.64])
                diag_t.setStyle(TableStyle([
                    ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#bfdbfe")),
                    ("BACKGROUND",(0,0),(0,-1),C_BLUE_LIGHT),
                    ("BACKGROUND",(1,0),(1,-1),C_BLUE_PALE),
                    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                    ("LEFTPADDING",(0,0),(-1,-1),9),
                    ("RIGHTPADDING",(0,0),(-1,-1),9),
                    ("TOPPADDING",(0,0),(-1,-1),7),
                    ("BOTTOMPADDING",(0,0),(-1,-1),7),
                ]))
                story.append(diag_t)
            else:
                story.append(Paragraph("Pas de diagnostic disponible pour cette consultation.", S_VAL))

            story.append(Spacer(1, 10))

            # Critères cliniques validés
            criteres = principale.get("criteres_valides", []) if principale else []
            if criteres:
                story.append(Paragraph("Critères cliniques validés", S_SEC))
                story.append(Spacer(1, 4))
                crit_rows = [[Paragraph(f"[+]  {_clean(cr)}", S_BULLET)] for cr in criteres]
                crit_t = Table(crit_rows, colWidths=[W])
                crit_t.setStyle(TableStyle([
                    ("GRID",(0,0),(-1,-1),0.5,C_GRAY_BDR),
                    ("ROWBACKGROUNDS",(0,0),(-1,-1),[C_WHITE, C_GRAY_HDR]),
                    ("LEFTPADDING",(0,0),(-1,-1),10),
                    ("TOPPADDING",(0,0),(-1,-1),5),
                    ("BOTTOMPADDING",(0,0),(-1,-1),5),
                ]))
                story.append(crit_t)
                story.append(Spacer(1, 10))

            # Examens recommandés
            examens = principale.get("examens_suggeres", []) if principale else []
            if examens:
                story.append(Paragraph("Examens recommandés", S_SEC))
                story.append(Spacer(1, 4))
                exam_rows = [[Paragraph(f"->  {e}", S_BULLET)] for e in examens]
                exam_t = Table(exam_rows, colWidths=[W])
                exam_t.setStyle(TableStyle([
                    ("GRID",(0,0),(-1,-1),0.5,C_GRAY_BDR),
                    ("ROWBACKGROUNDS",(0,0),(-1,-1),[C_WHITE, C_GRAY_HDR]),
                    ("LEFTPADDING",(0,0),(-1,-1),10),
                    ("TOPPADDING",(0,0),(-1,-1),5),
                    ("BOTTOMPADDING",(0,0),(-1,-1),5),
                ]))
                story.append(exam_t)
                story.append(Spacer(1, 10))

            # Recommandations médicales
            recommandations = (diag.recommandations if diag else None) or (principale.get("recommandations", []) if principale else [])
            if recommandations:
                story.append(Paragraph("Recommandations médicales", S_SEC))
                story.append(Spacer(1, 4))
                reco_rows = [[Paragraph(f"[+]  {_clean(r)}", S_BULLET)] for r in recommandations]
                reco_t = Table(reco_rows, colWidths=[W])
                reco_t.setStyle(TableStyle([
                    ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#bfdbfe")),
                    ("BACKGROUND",(0,0),(-1,-1),C_BLUE_PALE),
                    ("ROWBACKGROUNDS",(0,0),(-1,-1),[C_BLUE_PALE, colors.HexColor("#dbeafe")]),
                    ("LEFTPADDING",(0,0),(-1,-1),10),
                    ("TOPPADDING",(0,0),(-1,-1),5),
                    ("BOTTOMPADDING",(0,0),(-1,-1),5),
                ]))
                story.append(reco_t)
                story.append(Spacer(1, 10))

            # Prescription
            if any([presc.get("medicaments"), presc.get("conseils_maison"), presc.get("recommandations"), presc.get("suivi")]):
                story.append(Paragraph("Prescription médicale", S_SEC))
                story.append(Spacer(1, 4))
                arret = f"Oui — {presc.get('duree_arret','?')} jours" if presc.get("arret_travail") else "Non"
                hospi = f"Oui — {presc.get('motif_hospitalisation','')}" if presc.get("hospitalisation") else "Non"
                presc_rows = [
                    row("Médicaments",           presc.get("medicaments") or "Aucun"),
                    row("Conseils domicile",      presc.get("conseils_maison") or "Aucun"),
                    row("Recommandations",        presc.get("recommandations") or "Aucun"),
                    row("Arrêt de travail",       arret),
                    row("Hospitalisation",        hospi),
                    row("Suivi",                  presc.get("suivi") or "À définir"),
                ]
                story.append(simple_table(presc_rows))
                story.append(Spacer(1, 12))

            # Observations
            if c.observations:
                story.append(Paragraph("Observations du médecin", S_SEC))
                story.append(Spacer(1, 4))
                obs_t = Table([[Paragraph(c.observations, S_OBS)]], colWidths=[W])
                obs_t.setStyle(TableStyle([
                    ("BOX",(0,0),(-1,-1),0.5,C_GRAY_BDR),
                    ("BACKGROUND",(0,0),(-1,-1),C_GRAY_HDR),
                    ("LEFTPADDING",(0,0),(-1,-1),10),
                    ("RIGHTPADDING",(0,0),(-1,-1),10),
                    ("TOPPADDING",(0,0),(-1,-1),8),
                    ("BOTTOMPADDING",(0,0),(-1,-1),8),
                ]))
                story.append(obs_t)

        # Pied de page
        story.append(Spacer(1, 14))
        story.append(HRFlowable(width="100%", thickness=0.5, color=C_GRAY_BDR, spaceAfter=6))
        story.append(Paragraph(
            "Document généré par <b>PneumoIA</b> — Plateforme de suivi pneumologique<br/>"
            "Ce document est confidentiel et destiné exclusivement au patient et à son équipe médicale.",
            S_FOOTER))

        doc.build(story)
        return buf.getvalue()

    except Exception:
        return b"%PDF-1.4\n%%EOF"

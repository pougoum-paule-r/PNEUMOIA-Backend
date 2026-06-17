# app/routers/diagnostics.py
import joblib, json
import numpy as np
import pandas as pd
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.database import get_db

router = APIRouter(prefix="/diagnostic", tags=["Diagnostic IA"])
bearer = HTTPBearer()

# ── Chargement des 2 modèles ──────────────────────────────────────────────────
MODEL_DIR = Path(__file__).parent.parent / "ml_models"

try:
    model_base   = joblib.load(MODEL_DIR / "model_base.pkl")
    model_equipe = joblib.load(MODEL_DIR / "model_equipe.pkl")
    with open(MODEL_DIR / "metadata.json") as f:
        META = json.load(f)
    CLASSES         = META["classes"]
    FEATURES_BASE   = META["features_base"]
    FEATURES_EQUIPE = META["features_equipe"]
    print(" Modèles IA chargés avec succès")
    print(f"   Base   : {META['precision_base']}%")
    print(f"   Équipé : {META['precision_equipe']}%")
except Exception as e:
    print(f" Modèles IA non disponibles : {e}")
    model_base = model_equipe = CLASSES = None
    FEATURES_BASE = FEATURES_EQUIPE = []
    META = {}

# ── Données cliniques ─────────────────────────────────────────────────────────
CRITERES = {
    "Pneumonia":         ["Infiltrat alvéolaire au scanner", "Hypoxémie (O2 anormal)", "Anomalie des gaz du sang", "Débit expiratoire diminué", "Capacité vitale réduite"],
    "Asthma":            ["Obstruction bronchique réversible", "Antécédents d'asthme", "VEMS/CVF diminué", "Débit de pointe variable", "Réponse aux bronchodilatateurs"],
    "COPD":              ["Obstruction chronique des voies aériennes", "FEV1/FVC < 0.70", "Tabagisme significatif", "Hyperinflation pulmonaire"],
    "Tuberculosis":      ["Toux chronique productive", "Sueurs nocturnes et amaigrissement", "Infiltrats apicaux au scanner", "Contexte épidémiologique"],
    "COVID-19":          ["Syndrome grippal avec fièvre", "Atteinte pulmonaire bilatérale", "Hypoxémie progressive", "Scanner en verre dépoli"],
    "Influenza":         ["Début brutal avec fièvre élevée", "Myalgies et arthralgies", "Signes respiratoires supérieurs", "Contexte épidémique"],
    "Bronchitis":        ["Toux productive persistante", "Expectorations mucopurulentes", "Auscultation avec ronchi", "Absence d'infiltrat alvéolaire"],
    "Lung Cancer":       ["Toux chronique hémoptoïque", "Amaigrissement inexpliqué", "Masse pulmonaire au scanner", "Obstruction bronchique"],
    "Allergic Rhinitis": ["Rhinorrhée claire", "Éternuements en salves", "Obstruction nasale chronique", "Contexte allergique"],
    "Sinusitis":         ["Douleur sinusienne à la pression", "Obstruction nasale", "Sécrétions purulentes", "Opacité sinusienne"],
    "Cystic Fibrosis":   ["Toux productive chronique", "FVC et VEMS très diminués", "Test de la sueur positif", "Colonisation bactérienne"],
    "Sleep Apnea":       ["Ronflements nocturnes", "Apnées observées", "Somnolence diurne", "Saturation nocturne diminuée"],
    "Pneumothorax":      ["Douleur thoracique brutale", "Dyspnée aiguë", "Silence auscultatoire", "Hypoxémie soudaine"],
    "Common Cold":       ["Rhinorrhée et congestion nasale", "Légère fièvre", "Toux sèche modérée", "Évolution courte < 10 jours"],
}

RECOMMANDATIONS = {
    "Pneumonia":         ["Antibiothérapie adaptée (Amoxicilline 1g x 3/j - 7 jours)", "Surveillance saturation O2", "Hydratation abondante (>1.5L/jour)", "Kinésithérapie respiratoire", "Repos strict", "Réévaluation à 48-72h", "Hospitalisation si SpO2 < 92%"],
    "Asthma":            ["Bronchodilatateurs courte durée (Salbutamol)", "Corticostéroïdes inhalés", "Plan d'action écrit", "Éviction des allergènes", "Contrôle du débit de pointe"],
    "COPD":              ["Sevrage tabagique urgent", "Bronchodilatateurs longue durée (LABA/LAMA)", "Réhabilitation respiratoire", "Vaccination antigrippale", "Suivi semestriel spirométrie"],
    "Tuberculosis":      ["Déclaration obligatoire aux autorités sanitaires", "Traitement DOTS : Rifampicine + Isoniazide + Pyrazinamide + Éthambutol", "Isolement respiratoire", "Enquête autour du cas", "Durée minimale 6 mois"],
    "COVID-19":          ["Isolement strict 10 jours", "Surveillance saturation toutes les 4h", "Antipyrétiques si fièvre > 38.5°C", "Décubitus ventral si SpO2 < 94%", "Hospitalisation si SpO2 < 93%"],
    "Influenza":         ["Antiviraux (Oseltamivir) dans les 48h", "Repos et hydratation", "Antipyrétiques (Paracétamol)", "Éviter l'Aspirine", "Isolement 5 jours"],
    "Bronchitis":        ["Traitement symptomatique", "Mucolytiques et fluidifiants", "Antibiothérapie si purulent > 7 jours", "Hydratation", "Arrêt du tabac"],
    "Lung Cancer":       ["Bilan d'extension urgent (TDM thoraco-abdomino-pelvien)", "Biopsie bronchique", "Consultation oncologie thoracique", "Bilan biologique complet", "Arrêt tabac immédiat"],
    "Allergic Rhinitis": ["Antihistaminiques 2ème génération", "Corticostéroïdes nasaux", "Éviction des allergènes", "Tests allergologiques", "Désensibilisation possible"],
    "Sinusitis":         ["Décongestionnants nasaux (max 5 jours)", "Lavages nasaux sérum physiologique", "Antibiothérapie si bactérienne", "Antalgiques"],
    "Cystic Fibrosis":   ["Kinésithérapie respiratoire quotidienne", "Antibiotiques inhalés", "Enzymes pancréatiques", "Suivi pluridisciplinaire spécialisé"],
    "Sleep Apnea":       ["Polysomnographie pour confirmer", "PPC nocturne", "Perte de poids", "Éviction alcool et sédatifs"],
    "Pneumothorax":      ["Hospitalisation en urgence", "Exsufflation ou drainage pleural", "Surveillance radiologique", "Oxygénothérapie fort débit"],
    "Common Cold":       ["Traitement symptomatique uniquement", "Repos et hydratation", "Paracétamol si fièvre", "Pas d'antibiothérapie (viral)"],
}

EXAMENS = {
    "Pneumonia":         ["Radiographie thoracique", "NFS-CRP", "Hémocultures", "ECBC", "Gaz du sang si SpO2 < 94%"],
    "Asthma":            ["EFR (spirométrie)", "Test de réversibilité", "Tests allergologiques", "Peak-flow"],
    "COPD":              ["Spirométrie post-bronchodilatateur", "TDM thoracique", "Gaz du sang", "ECG"],
    "Tuberculosis":      ["Bacilloscopie x 3", "Culture BK", "IDR tuberculine", "TDM thoracique"],
    "COVID-19":          ["PCR SARS-CoV-2", "Scanner thoracique", "NFS-CRP-D-Dimères", "Gaz du sang"],
    "Influenza":         ["Test rapide grippe", "NFS", "PCR grippe si doute"],
    "Bronchitis":        ["Radiographie thoracique", "NFS-CRP", "ECBC si purulent"],
    "Lung Cancer":       ["TDM thoraco-AP", "PET-scan", "Fibroscopie bronchique", "Biopsie", "Bilan biologique"],
    "Allergic Rhinitis": ["Tests cutanés allergologiques", "IgE spécifiques", "NFS (éosinophiles)"],
    "Sinusitis":         ["TDM des sinus", "NFS-CRP"],
    "Cystic Fibrosis":   ["Test de la sueur", "Génotypage CFTR", "Spirométrie", "ECBC"],
    "Sleep Apnea":       ["Polysomnographie", "Oxymétrie nocturne", "ECG"],
    "Pneumothorax":      ["Radiographie thoracique urgente", "TDM thoracique", "Gaz du sang"],
    "Common Cold":       ["Aucun examen nécessaire en routine"],
}

RISQUE_PAR_MALADIE = {
    "Pneumonia": "high", "Tuberculosis": "high", "Lung Cancer": "critical",
    "COVID-19": "high", "Pneumothorax": "critical", "COPD": "medium",
    "Cystic Fibrosis": "high", "Asthma": "medium", "Sleep Apnea": "medium",
    "Influenza": "low", "Bronchitis": "low", "Sinusitis": "low",
    "Allergic Rhinitis": "low", "Common Cold": "low",
}

ALERTES_RELIGIEUSES = {
    "temoin_jehovah": {
        "titre": "ALERTE RELIGIEUSE — Témoin de Jéhovah",
        "restrictions": [
            "Refus formel de transfusion sanguine et produits dérivés du sang",
            "Refus des globules rouges, plasma, plaquettes et granulocytes",
        ],
        "recommandations_speciales": [
            "Privilégier les alternatives non sanguines (érythropoïétine, fer IV)",
            "Techniques chirurgicales d'épargne sanguine si intervention prévue",
            "Informer toute l'équipe soignante de cette restriction",
            "Documenter le refus signé dans le dossier médical",
            "Consulter le comité d'éthique si situation d'urgence vitale",
        ],
    },
    "musulman": {
        "titre": "INFORMATION RELIGIEUSE — Patient Musulman",
        "restrictions": [
            "Refus de médicaments contenant du porc (gélatine porcine, insuline porcine)",
            "Jeûne du Ramadan pouvant affecter la prise de médicaments",
        ],
        "recommandations_speciales": [
            "Vérifier la composition des médicaments (certificat halal si disponible)",
            "Adapter les horaires de prise médicamenteuse pendant le Ramadan",
            "Consulter un imam si nécessaire pour les cas d'urgence médicale",
        ],
    },
}

# Alertes groupe sanguin (informations cliniques)
ALERTES_GROUPE_SANGUIN = {
    "O-": {
        "titre": "GROUPE SANGUIN O- — Donneur universel",
        "infos": [
            "Donneur universel — sang rare et précieux",
            "Ne peut recevoir que du sang O-",
            "Prévoir stock O- en cas de chirurgie urgente",
        ],
    },
    "AB+": {
        "titre": "GROUPE SANGUIN AB+ — Receveur universel",
        "infos": ["Peut recevoir tout type de sang"],
    },
    "AB-": {
        "titre": "GROUPE SANGUIN AB-",
        "infos": [
            "Peut recevoir A-, B-, O-, AB-",
            "Groupe rare — prévoir en avance si chirurgie",
        ],
    },
}


def _appliquer_alertes(body_religion, body_groupe_sanguin, prediction, probabilities, maladies, recommandations_principales):
    """Centralise la logique d'alertes religion + groupe sanguin."""
    alertes = []

    # ── Religion ──────────────────────────────────────────────
    religion_key = (body_religion or "").lower().replace(" ", "_").replace("é", "e").replace("è", "e")
    if religion_key in ALERTES_RELIGIEUSES:
        info = ALERTES_RELIGIEUSES[religion_key]
        alertes.append({
            "type":                      "religious",
            "titre":                     info["titre"],
            "restrictions":              info["restrictions"],
            "recommandations_speciales": info["recommandations_speciales"],
        })
        recommandations_principales = [
            r for r in recommandations_principales
            if "transfusion" not in r.lower() and "sang" not in r.lower()
        ]
        recommandations_principales = info["recommandations_speciales"] + recommandations_principales
        for m in maladies:
            m["recommandations"] = [
                r for r in m["recommandations"]
                if "transfusion" not in r.lower() and "sang" not in r.lower()
            ]

    # ── Groupe sanguin ────────────────────────────────────────
    if body_groupe_sanguin and body_groupe_sanguin in ALERTES_GROUPE_SANGUIN:
        info_gs = ALERTES_GROUPE_SANGUIN[body_groupe_sanguin]
        alertes.append({
            "type":   "groupe_sanguin",
            "titre":  info_gs["titre"],
            "infos":  info_gs["infos"],
        })

    # ── Urgence médicale ──────────────────────────────────────
    confidence_val = round(float(max(probabilities)) * 100, 1)
    if prediction in ["Pneumothorax", "Lung Cancer"] and confidence_val > 60:
        alertes.append({
            "type":    "urgence",
            "titre":   "URGENCE MEDICALE",
            "message": f"{prediction} suspecté à {confidence_val}% — prise en charge immédiate requise",
        })

    return alertes, recommandations_principales


# ── Schema commun ─────────────────────────────────────────────────────────────
class ConsultationRequest(BaseModel):
    age:             float
    gender:          int
    smoke:           int   = 0
    asthma:          int   = 0
    other_diseases:  int   = 0
    religion:        Optional[str] = None
    groupe_sanguin:  Optional[str] = None
    o2:              int   = 0
    scan:            int   = 0
    pefr:            int   = 0
    fvc:             Optional[float] = None
    fec1:            Optional[float] = None
    fev1_fvc_ratio:  Optional[float] = None
    abg_po2:         Optional[int]   = None
    abg_pco2:        Optional[int]   = None
    abg_ph:          Optional[int]   = None
    peak_flow:       Optional[float] = None


class PredictAndSaveRequest(BaseModel):
    consultation_id: str
    age:             float
    gender:          int
    smoke:           int   = 0
    asthma:          int   = 0
    other_diseases:  int   = 0
    religion:        Optional[str] = None
    groupe_sanguin:  Optional[str] = None   # ← AJOUTÉ
    o2:              int   = 0
    scan:            int   = 0
    pefr:            int   = 0
    fvc:             Optional[float] = None
    fec1:            Optional[float] = None
    fev1_fvc_ratio:  Optional[float] = None
    peak_flow:       Optional[float] = None
    abg_po2:         Optional[int]   = None
    abg_pco2:        Optional[int]   = None
    abg_ph:          Optional[int]   = None


def _choisir_modele(body):
    donnees_efr = [body.fvc, body.fec1, body.fev1_fvc_ratio, body.peak_flow]
    nb_efr      = sum(1 for d in donnees_efr if d is not None)
    return nb_efr >= 2


def _criteres_depuis_symptomes(symptomes: dict, body) -> list[str]:
    """
    Génère les critères validés à partir :
      - des paramètres structurés du modèle (body)
      - des symptômes cliniques réels saisis par le médecin (symptomes, JSONB BDD)
    Conforme à l'architecture CDSS : critères = données patient, pas règles statiques.
    """
    criteres = []

    # ── Données objectives / EFR / ABG ───────────────────────────────────────────
    if body.o2 == 1:
        criteres.append("Hypoxémie confirmée (SpO₂ < 94%)")
    if body.scan == 1:
        criteres.append("Scanner thoracique réalisé — anomalie détectée")
    if body.smoke == 1:
        criteres.append("Tabagisme actif confirmé")
    if body.asthma == 1:
        criteres.append("Antécédent d'asthme documenté")
    if body.pefr == 1:
        criteres.append("Débit expiratoire de pointe anormal")
    if body.fvc and body.fvc < 3.0:
        criteres.append(f"Capacité vitale forcée réduite — FVC = {body.fvc} L")
    if body.fev1_fvc_ratio and body.fev1_fvc_ratio < 0.7:
        criteres.append(f"Obstruction bronchique — Ratio VEMS/CVF = {body.fev1_fvc_ratio:.2f}")
    if body.peak_flow and body.peak_flow < 200:
        criteres.append(f"Débit de pointe bas — Peak Flow = {body.peak_flow} L/min")
    if body.abg_po2 == 1:
        criteres.append("Hypoxémie gazeuse — ABG PO₂ anormal")
    if body.abg_pco2 == 1:
        criteres.append("Hypercapnie — ABG PCO₂ anormal")
    if body.abg_ph == 1:
        criteres.append("Trouble de l'équilibre acido-basique")

    # ── Symptômes cliniques saisis par le médecin (BDD) ──────────────────────────
    if symptomes.get("fievre"):
        t = symptomes.get("fievre_temperature")
        criteres.append(f"Fièvre documentée{f' — {t} °C' if t else ''}")
    if symptomes.get("toux"):
        toux_type = symptomes.get("toux_type", "")
        criteres.append(f"Toux {'sèche' if toux_type == 'seche' else 'productive'} confirmée")
    if symptomes.get("toux_sang") or symptomes.get("hemoptysie"):
        criteres.append("Hémoptysie — signe d'alarme")
    if symptomes.get("dyspnee"):
        stade = symptomes.get("dyspnee_stade", 1)
        criteres.append(f"Dyspnée stade {stade}/4")
    if symptomes.get("douleur_thoracique"):
        criteres.append("Douleur thoracique présente")
    if symptomes.get("wheezing"):
        criteres.append("Wheezing ausculté")
    if symptomes.get("crepitants"):
        criteres.append("Crépitants à l'auscultation")
    if symptomes.get("sibilants"):
        criteres.append("Sibilants à l'auscultation")
    if symptomes.get("sueurs_nocturnes"):
        criteres.append("Sueurs nocturnes")
    if symptomes.get("perte_poids"):
        criteres.append("Perte de poids involontaire")
    spo2_mesuree = symptomes.get("saturation_o2")
    if spo2_mesuree and float(spo2_mesuree) < 94:
        criteres.append(f"SpO₂ mesurée à {spo2_mesuree} %")
    temp_mesuree = symptomes.get("temperature")
    if temp_mesuree and float(temp_mesuree) > 38.5:
        criteres.append(f"Hyperthermie — T° = {temp_mesuree} °C")

    if not criteres:
        criteres = ["Aucune donnée clinique saisie — résultat basé sur profil démographique uniquement"]
    return criteres


# ── POST /predict ─────────────────────────────────────────────────────────────
@router.post("/predict")
async def predict(
    body: ConsultationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
):
    try:
        decode_token(credentials.credentials)
    except JWTError:
        raise HTTPException(401, "Token invalide")

    if not model_base or not model_equipe:
        raise HTTPException(503, "Modèles IA non disponibles")

    est_equipe = _choisir_modele(body)

    if est_equipe:
        features_dict = {
            'AGE': body.age, 'Gender': body.gender, 'smoke': body.smoke,
            'FVC': body.fvc if body.fvc is not None else np.nan,
            'FEC1': body.fec1 if body.fec1 is not None else np.nan,
            'FEV1_FVC_Ratio': body.fev1_fvc_ratio if body.fev1_fvc_ratio is not None else np.nan,
            'PEFR': body.pefr, 'O2': body.o2,
            'ABG-P-O2': body.abg_po2 if body.abg_po2 is not None else np.nan,
            'ABG-P-CO2': body.abg_pco2 if body.abg_pco2 is not None else np.nan,
            'ABG-pH Level': body.abg_ph if body.abg_ph is not None else np.nan,
            'Scan': body.scan, 'Asthama': body.asthma,
            'Other diseaes': body.other_diseases,
            'Peak_Flow': body.peak_flow if body.peak_flow is not None else np.nan,
        }
        X             = pd.DataFrame([features_dict])[FEATURES_EQUIPE]
        model_utilise = model_equipe
        precision     = META.get("precision_equipe", 96.8)
        type_result   = "equipe"
    else:
        features_dict = {
            'AGE': body.age, 'Gender': body.gender, 'smoke': body.smoke,
            'FVC': body.fvc if body.fvc is not None else np.nan,
            'FEC1': body.fec1 if body.fec1 is not None else np.nan,
            'FEV1_FVC_Ratio': body.fev1_fvc_ratio if body.fev1_fvc_ratio is not None else np.nan,
            'Peak_Flow': body.peak_flow if body.peak_flow is not None else np.nan,
            'PEFR': body.pefr, 'O2': body.o2, 'Scan': body.scan,
            'Asthama': body.asthma, 'Other diseaes': body.other_diseases,
        }
        X             = pd.DataFrame([features_dict])[FEATURES_BASE]
        model_utilise = model_base
        precision     = META.get("precision_base", 53.2)
        type_result   = "base"

    prediction    = model_utilise.predict(X)[0]
    probabilities = model_utilise.predict_proba(X)[0]
    classes_list  = model_utilise.classes_
    confidence    = round(float(max(probabilities)) * 100, 1)

    top3_idx = np.argsort(probabilities)[::-1][:3]
    differentials = [
        {
            "name":      classes_list[i],
            "score":     round(float(probabilities[i]) * 100, 1),
            "confiance": "Élevée" if probabilities[i] > 0.7 else
                         "Moyenne" if probabilities[i] > 0.4 else "Faible"
        }
        for i in top3_idx
    ]

    fiabilite       = ("high" if confidence >= 70 else "medium") if est_equipe else "low"
    fiabilite_label = ("Diagnostic fiable" if confidence >= 70 else "Diagnostic probable — confirmer par examens") if est_equipe else "Données insuffisantes — résultat INDICATIF uniquement"

    criteres_valides = []
    if body.scan > 0:       criteres_valides.append("Anomalie scanographique détectée")
    if body.o2 == 1:        criteres_valides.append("Hypoxémie (saturation O2 < 94%)")
    if body.smoke == 1:     criteres_valides.append("Tabagisme actif — facteur aggravant")
    if body.asthma == 1:    criteres_valides.append("Antécédent d'asthme")
    if body.pefr == 1:      criteres_valides.append("Débit expiratoire anormal")
    if body.fev1_fvc_ratio and body.fev1_fvc_ratio < 0.7:
        criteres_valides.append(f"Ratio VEMS/CVF diminué ({body.fev1_fvc_ratio:.2f})")
    if body.fvc and body.fvc < 3.0:
        criteres_valides.append(f"Capacité vitale réduite (FVC = {body.fvc} L)")
    if body.peak_flow and body.peak_flow < 200:
        criteres_valides.append(f"Débit de pointe bas ({body.peak_flow} L/min)")
    if body.abg_po2 == 1:   criteres_valides.append("PO2 sanguin anormal")
    if body.abg_pco2 == 1:  criteres_valides.append("PCO2 sanguin anormal")
    if not criteres_valides:
        criteres_valides = CRITERES.get(prediction, [])[:3]

    donnees_manquantes = []
    if not est_equipe:
        if body.fvc is None:       donnees_manquantes.append("FVC — Capacité vitale forcée (spirométrie)")
        if body.fec1 is None:      donnees_manquantes.append("FEV1 — Volume expiratoire forcé (spirométrie)")
        if body.peak_flow is None: donnees_manquantes.append("Peak Flow — Débit de pointe (débitmètre)")

    recommandations = RECOMMANDATIONS.get(prediction, [])
    maladies_dummy  = []  # /predict n'a pas de liste maladies à filtrer
    alertes, recommandations = _appliquer_alertes(
        body.religion, body.groupe_sanguin, prediction, probabilities, maladies_dummy, recommandations
    )

    return {
        "principal":          prediction,
        "confidence":         confidence,
        "type_consultation":  type_result,
        "fiabilite":          fiabilite,
        "fiabilite_label":    fiabilite_label,
        "precision_modele":   f"{precision}%",
        "differentials":      differentials,
        "riskLevel":          RISQUE_PAR_MALADIE.get(prediction, "low"),
        "criteria":           criteres_valides,
        "recommendations":    recommandations,
        "examensRecommandes": EXAMENS.get(prediction, []),
        "alertes":            alertes,
        "donnees_manquantes": donnees_manquantes,
        "message_precision":  (
            f"Fournissez les données manquantes pour améliorer la précision à {META.get('precision_equipe', 96.8)}%."
        ) if not est_equipe else None,
    }


# ── GET /status ───────────────────────────────────────────────────────────────
@router.get("/status")
async def model_status():
    return {
        "disponible":           model_base is not None and model_equipe is not None,
        "maladies_detectables": CLASSES or [],
        "nombre_maladies":      len(CLASSES) if CLASSES else 0,
        "precision_base":       f"{META.get('precision_base', 0)}%",
        "precision_equipe":     f"{META.get('precision_equipe', 0)}%",
    }


# ── POST /predict-and-save ────────────────────────────────────────────────────
@router.post("/predict-and-save")
async def predict_and_save(
    body: PredictAndSaveRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
):
    # 1. Vérifier le token
    try:
        payload = decode_token(credentials.credentials)
        role    = payload.get("role", "medecin")
        # Aide token: sub=aide_id, medecin_id=medecin lié
        medecin_id = payload.get("medecin_id") if role == "aide_soignant" else payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Token invalide")

    # 2. Vérifier que la consultation appartient à ce médecin
    from app.models.consultation import Consultation
    c = await db.get(Consultation, body.consultation_id)
    if not c or c.medecin_id != medecin_id:
        raise HTTPException(403, "Accès refusé")

    # Symptômes réels saisis par le médecin (JSONB PostgreSQL)
    symptomes_bdd = c.symptomes or {}

    if not model_base or not model_equipe:
        raise HTTPException(503, "Modèles IA non disponibles")

    # 3. Choisir le modèle — CORRECTION : seulement les EFR déclenchent équipé
    est_equipe = _choisir_modele(body)

    donnees_manquantes = []
    if not est_equipe:
        if body.fvc is None:       donnees_manquantes.append("FVC — Capacité vitale forcée (spirométrie)")
        if body.fec1 is None:      donnees_manquantes.append("FEV1 — Volume expiratoire forcé (spirométrie)")
        if body.peak_flow is None: donnees_manquantes.append("Peak Flow — Débit de pointe (débitmètre)")

    if est_equipe:
        features_dict = {
            'AGE': body.age, 'Gender': body.gender, 'smoke': body.smoke,
            'FVC': body.fvc if body.fvc is not None else np.nan,
            'FEC1': body.fec1 if body.fec1 is not None else np.nan,
            'FEV1_FVC_Ratio': body.fev1_fvc_ratio if body.fev1_fvc_ratio is not None else np.nan,
            'PEFR': body.pefr, 'O2': body.o2,
            'ABG-P-O2': body.abg_po2 if body.abg_po2 is not None else np.nan,
            'ABG-P-CO2': body.abg_pco2 if body.abg_pco2 is not None else np.nan,
            'ABG-pH Level': body.abg_ph if body.abg_ph is not None else np.nan,
            'Scan': body.scan, 'Asthama': body.asthma,
            'Other diseaes': body.other_diseases,
            'Peak_Flow': body.peak_flow if body.peak_flow is not None else np.nan,
        }
        X             = pd.DataFrame([features_dict])[FEATURES_EQUIPE]
        model_utilise = model_equipe
        precision     = META.get("precision_equipe", 96.8)
    else:
        features_dict = {
            'AGE': body.age, 'Gender': body.gender, 'smoke': body.smoke,
            'FVC': body.fvc if body.fvc is not None else np.nan,
            'FEC1': body.fec1 if body.fec1 is not None else np.nan,
            'FEV1_FVC_Ratio': body.fev1_fvc_ratio if body.fev1_fvc_ratio is not None else np.nan,
            'Peak_Flow': body.peak_flow if body.peak_flow is not None else np.nan,
            'PEFR': body.pefr, 'O2': body.o2, 'Scan': body.scan,
            'Asthama': body.asthma, 'Other diseaes': body.other_diseases,
        }
        X             = pd.DataFrame([features_dict])[FEATURES_BASE]
        model_utilise = model_base
        precision     = META.get("precision_base", 53.2)

    prediction    = model_utilise.predict(X)[0]
    probabilities = model_utilise.predict_proba(X)[0]
    top3_idx      = np.argsort(probabilities)[::-1][:3]
    classes_list  = model_utilise.classes_
    confidence_val = round(float(max(probabilities)) * 100, 1)

    maladies = [
        {
            "nom":              classes_list[i],
            "pct":              round(float(probabilities[i]) * 100, 1),
            "etat":             "critique"  if probabilities[i] > 0.7 else
                                "urgent"    if probabilities[i] > 0.5 else
                                "surveille" if probabilities[i] > 0.3 else "stable",
            "criteres_valides": _criteres_depuis_symptomes(symptomes_bdd, body),
            "recommandations":  RECOMMANDATIONS.get(classes_list[i], []),
            "examens_suggeres": EXAMENS.get(classes_list[i], []),
        }
        for i in top3_idx
    ]

    etat_patient = maladies[0]["etat"] if maladies else "stable"

    # 4. Alertes religion + groupe sanguin
    recommandations_principales = RECOMMANDATIONS.get(prediction, [])
    alertes, recommandations_principales = _appliquer_alertes(
        body.religion, body.groupe_sanguin, prediction, probabilities,
        maladies, recommandations_principales
    )

    # 5. Sauvegarder dans diagnostics_ia
    from app.models.diagnostic_ia import DiagnosticIA
    diag = DiagnosticIA(
        consultation_id    = body.consultation_id,
        maladies           = maladies,
        recommandations    = recommandations_principales,
        etat_patient       = etat_patient,
        version_modele     = "equipe" if est_equipe else "base",
        duree_inference_ms = 0,
    )
    db.add(diag)
    await db.commit()
    await db.refresh(diag)

    return {
        "diagnostic_id":       diag.id,
        "consultation_id":     body.consultation_id,
        "principal":           prediction,
        "confidence":          confidence_val,
        "maladies":            maladies,
        "etat_patient":        etat_patient,
        "risque_eleve":        etat_patient in ("urgent", "critique"),
        "recommandations":     recommandations_principales,
        "examens_recommandes": EXAMENS.get(prediction, []),
        "precision_modele":    f"{precision}%",
        "type_consultation":   "equipe" if est_equipe else "base",
        "alertes":             alertes,
        "donnees_manquantes":  donnees_manquantes,
        "message_precision":   f"Fournissez les données manquantes pour améliorer la précision à {META.get('precision_equipe', 96.8)}%." if not est_equipe else None,
    }


@router.post("/{diagnostic_id}/feedback", status_code=201)
async def soumettre_feedback(
    diagnostic_id: str,
    payload: dict,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
):
    try:
        token_data = decode_token(credentials.credentials)
        medecin_id = token_data.get("sub")
    except JWTError:
        raise HTTPException(401, "Token invalide")

    from app.models.diagnostic_ia import DiagnosticIA
    from app.models.feedback_ia import FeedbackIA

    diag = await db.get(DiagnosticIA, diagnostic_id)
    if not diag:
        raise HTTPException(404, "Diagnostic introuvable")

    feedback = FeedbackIA(
        diagnostic_id    = diagnostic_id,
        medecin_id       = medecin_id,
        concordance      = payload.get("concordance"),
        diagnostic_final = payload.get("diagnostic_final"),
        commentaire      = payload.get("commentaire"),
    )
    db.add(feedback)
    await db.commit()
    return {"message": "Feedback enregistré"}
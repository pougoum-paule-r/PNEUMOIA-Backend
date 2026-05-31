# app/schemas/consultation.py
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


# ── Création ─────────────────────────────────────────────────────
class ConsultationCreate(BaseModel):
    patient_id: str


class ConsultationOut(BaseModel):
    id:         str
    patient_id: str
    medecin_id: str
    statut:     str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Étape 2 — Antécédents ────────────────────────────────────────
class AntecedentsIn(BaseModel):
    diabete:       bool = False
    hypertension:  bool = False
    asthme:        bool = False
    bpco:          bool = False
    tuberculose:   bool = False
    vih:           bool = False
    typhoide:      bool = False
    paludisme:     bool = False
    covid19:       bool = False
    hepatite_b:    bool = False
    hepatite_c:    bool = False
    cancer_poumon: bool = False

    traitement_en_cours:  Optional[str] = None
    allergie_medicaments: Optional[str] = None

    tabagisme:           str = "non-fumeur"
    cigarettes_par_jour: int = 0
    duree_tabagisme:     int = 0
    alcool:              bool = False

    profession_risque:          bool           = False
    exposition_professionnelle: Optional[str]  = None


# ── Étape 3 — Symptômes ──────────────────────────────────────────
class SymptomesIn(BaseModel):
    # Motif
    motif:               Optional[str] = None
    debut_symptomes:     Optional[str] = None
    evolution:           Optional[str] = None
    traitement_deja_pris: Optional[str] = None

    # Signes vitaux
    temperature:            Optional[float] = None
    saturation_o2:          Optional[float] = None
    frequence_cardiaque:    Optional[float] = None
    frequence_respiratoire: Optional[float] = None
    tension_systolique:     Optional[float] = None
    tension_diastolique:    Optional[float] = None

    # Fièvre
    fievre:            bool           = False
    fievre_temperature: Optional[float] = None
    fievre_duree:      Optional[str]  = None

    # Toux
    toux:        bool           = False
    toux_type:   Optional[str]  = "seche"
    toux_sang:   bool           = False
    toux_couleur: Optional[str] = None

    # Dyspnée
    dyspnee:        bool = False
    dyspnee_stade:  int  = 1
    dyspnee_repos:  bool = False
    dyspnee_effort: bool = False

    # Douleur thoracique
    douleur_thoracique: bool          = False
    douleur_type:       Optional[str] = None

    # Autres
    wheezing:        bool = False
    hemoptysie:      bool = False
    fatigue:         bool = False
    perte_poids:     bool = False
    sueurs_nocturnes: bool = False
    courbatures:     bool = False
    maux_de_tete:    bool = False
    rhinorrhee:      bool = False

    # Examen clinique
    crepitants: bool = False
    sibilants:  bool = False

    # Examens réalisés
    scanner:     bool = False
    efr:         bool = False
    recherche_bk: bool = False

    # EFR — requis par le modèle IA équipé
    fvc:       Optional[float] = None
    fec1:      Optional[float] = None
    peak_flow: Optional[float] = None

    # Gaz du sang
    pefr_anormal:    bool = False
    abg_co2_anormal: bool = False
    abg_ph_anormal:  bool = False


# ── Étape 4 — Avis médecin + Prescription + Partage ─────────────
class PartageIn(BaseModel):
    """
    Le médecin peut partager le cas avec :
    - Un médecin spécifique (type="medecin", destinataire_id=medecin.id)
    - Une communauté (type="communaute", destinataire_id=communaute.id)
    - Personne (actif=False)
    Et envoyer le bilan par mail au patient.
    """
    actif:               bool                                     = False
    anonymiser:          bool                                     = True
    type:                Optional[Literal["medecin","communaute"]] = None
    destinataire_id:     Optional[str]                           = None
    envoyer_mail_patient: bool                                   = False


class OpinionIn(BaseModel):
    """
    POST /api/v1/consultations/:id/opinion
    Appelé depuis handleFinish() dans Consultations.jsx

    Si le médecin ne remplit pas ceci → consultation reste "en_attente"
    Si rempli → consultation passe à "terminee"
    """
    diagnostic_ia_id:      Optional[str] = None

    # Prescription
    medicaments:           Optional[str] = None
    conseils_maison:       Optional[str] = None
    recommandations:       Optional[str] = None
    arret_travail:         bool          = False
    duree_arret:           Optional[int] = None
    hospitalisation:       bool          = False
    motif_hospitalisation: Optional[str] = None
    suivi:                 Optional[str] = "7 jours"

    # Observations
    observations:          Optional[str] = None

    # Partage
    partage:               PartageIn     = PartageIn()


# ── Accès inter-médecins ─────────────────────────────────────────
class AccesRequestIn(BaseModel):
    patient_id:   str
    justificatif: Optional[str] = None


class AccesRequestOut(BaseModel):
    id:         str
    patient_id: str
    statut:     str
    created_at: datetime

    model_config = {"from_attributes": True}
// src/services/consultationApi.js
// ================================================================
// Compatible avec votre router diagnostics.py existant
// qui expose POST /diagnostic/predict
// ================================================================

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const DIAG_URL = import.meta.env.VITE_API_URL
  ? import.meta.env.VITE_API_URL.replace('/api/v1', '')
  : 'http://localhost:8000';

const getHeaders = () => {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

const apiFetch = async (url, options = {}) => {
  const res = await fetch(url, { ...options, headers: { ...getHeaders(), ...options.headers } });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: `Erreur ${res.status}` }));
    throw new Error(err.detail || `Erreur ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
};

// ── Patients ─────────────────────────────────────────────────────
export const searchPatient   = (q)   => apiFetch(`${BASE_URL}/patients/search?q=${encodeURIComponent(q)}`);
export const createPatient   = (d)   => apiFetch(`${BASE_URL}/patients`, { method: 'POST', body: JSON.stringify(d) });
export const getPatient      = (id)  => apiFetch(`${BASE_URL}/patients/${id}`);
export const requestPatientAccess = (patient_id, justificatif) =>
  apiFetch(`${BASE_URL}/patients/access-requests`, {
    method: 'POST',
    body: JSON.stringify({ patient_id, justificatif }),
  });

// ── Consultations ────────────────────────────────────────────────
export const createConsultation  = (patient_id) =>
  apiFetch(`${BASE_URL}/consultations`, { method: 'POST', body: JSON.stringify({ patient_id }) });

export const saveAntecedents = (id, data) =>
  apiFetch(`${BASE_URL}/consultations/${id}/antecedents`, { method: 'PATCH', body: JSON.stringify(data) });

export const saveSymptomes = (id, data) =>
  apiFetch(`${BASE_URL}/consultations/${id}/symptomes`, { method: 'PATCH', body: JSON.stringify(data) });

export const saveOpinion = (id, { prescription, diagnosticIaId, partage }) =>
  apiFetch(`${BASE_URL}/consultations/${id}/opinion`, {
    method: 'POST',
    body: JSON.stringify({
      diagnostic_ia_id:      diagnosticIaId,
      medicaments:           prescription.medicaments,
      conseils_maison:       prescription.conseilsMaison,
      recommandations:       prescription.recommandations,
      arret_travail:         prescription.arretTravail,
      duree_arret:           prescription.arretTravail ? parseInt(prescription.dureeArret) : null,
      hospitalisation:       prescription.hospitalisation,
      motif_hospitalisation: prescription.motifHospitalisation || null,
      suivi:                 prescription.suivi,
      observations:          prescription.observations,
      partage: {
        actif:               partage?.actif               || prescription.partageCommunaute || false,
        anonymiser:          partage?.anonymiser           || prescription.anonymiser        || true,
        type:                partage?.type                || null,
        destinataire_id:     partage?.destinataire_id     || null,
        envoyer_mail_patient: partage?.envoyerMailPatient || false,
      },
    }),
  });

export const getConsultations = () => apiFetch(`${BASE_URL}/consultations`);

// ── Diagnostic IA — appel vers votre router diagnostics.py ──────
// Votre router expose POST /diagnostic/predict
// Il gère automatiquement les 2 modèles selon les données disponibles
export const runDiagnosticIA = ({
  consultationId,
  patientInfo,
  antecedents,
  consultation,
}) => {
  const spo2      = parseFloat(consultation.saturationO2) || 97;
  const fvc       = parseFloat(consultation.fvc)          || null;
  const fec1      = parseFloat(consultation.fec1)         || null;
  const ratio     = fvc && fec1 ? parseFloat((fec1 / fvc).toFixed(3)) : null;
  const peakFlow  = parseFloat(consultation.peakFlow)     || null;

  // Calcul âge depuis dateNaissance
  let age = 50;
  if (patientInfo.dateNaissance) {
    const dn   = new Date(patientInfo.dateNaissance);
    const diff = Date.now() - dn.getTime();
    age = Math.floor(diff / (1000 * 60 * 60 * 24 * 365.25));
  }

  return apiFetch(`${DIAG_URL}/diagnostic/predict`, {
    method: 'POST',
    body: JSON.stringify({
      // Données de base (modèle_base — toujours disponibles)
      age,
      gender:         patientInfo.civilite === 'M' ? 1 : 0,
      smoke:          antecedents.tabagisme === 'fumeur' ? 1 : 0,
      asthma:         antecedents.asthme ? 1 : 0,
      other_diseases: (antecedents.diabete || antecedents.hypertension || antecedents.vih) ? 1 : 0,
      religion:       patientInfo.religion || null,
      o2:             spo2 < 94 ? 1 : 0,
      scan:           consultation.scanner ? 1 : 0,
      pefr:           consultation.pefr_anormal ? 1 : 0,

      // Données EFR (modèle_equipe — si disponibles → meilleure précision)
      fvc,
      fec1,
      fev1_fvc_ratio: ratio,
      peak_flow:      peakFlow,
      abg_po2:        consultation.saturationO2 < 94  ? 1 : 0,
      abg_pco2:       consultation.abg_co2_anormal    ? 1 : 0,
      abg_ph:         consultation.abg_ph_anormal     ? 1 : 0,
    }),
  });
};

// ── PDF ──────────────────────────────────────────────────────────
export const downloadPDF = async (consultationId) => {
  const token = localStorage.getItem('access_token');
  const res   = await fetch(`${BASE_URL}/consultations/${consultationId}/pdf`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('Erreur génération PDF');
  const blob = await res.blob();
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = `bilan_${consultationId}.pdf`;
  a.click();
  URL.revokeObjectURL(url);
};
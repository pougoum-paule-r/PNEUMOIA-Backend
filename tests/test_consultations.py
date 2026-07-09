"""
Tests consultations — PneumoIA
Couvre : création, liste, stats, historique, antécédents, symptômes, statut clinique
"""
import pytest

pytestmark = pytest.mark.anyio

PATIENT_DATA = {
    "civilite":  "Mme",
    "nom":       "Martin",
    "prenom":    "Sophie",
    "telephone": "+237600000002",
}

_patient_id      = None
_consultation_id = None


async def test_setup_patient(client, medecin_headers):
    """Crée un patient de test pour les consultations."""
    global _patient_id
    res = await client.post("/api/v1/patients", json=PATIENT_DATA, headers=medecin_headers)
    assert res.status_code == 201
    _patient_id = res.json()["id"]


async def test_creer_consultation(client, medecin_headers):
    """POST /consultations crée une consultation pour le patient."""
    global _consultation_id
    assert _patient_id
    res = await client.post("/api/v1/consultations",
                            json={"patient_id": _patient_id},
                            headers=medecin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["statut"] == "en_attente"
    _consultation_id = data["id"]


async def test_lister_consultations(client, medecin_headers):
    """GET /consultations retourne la liste des consultations du médecin."""
    res = await client.get("/api/v1/consultations", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_consultations_en_attente(client, medecin_headers):
    """GET /consultations/en-attente retourne uniquement les consultations en attente."""
    res = await client.get("/api/v1/consultations/en-attente", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_mes_stats_consultations(client, medecin_headers):
    """GET /consultations/mes-stats retourne total, terminée, en_attente."""
    res = await client.get("/api/v1/consultations/mes-stats", headers=medecin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "total" in data
    assert "terminee" in data
    assert "en_attente" in data


async def test_historique_consultations(client, medecin_headers):
    """GET /consultations/historique retourne la liste enrichie."""
    res = await client.get("/api/v1/consultations/historique", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_get_consultation(client, medecin_headers):
    """GET /consultations/:id retourne le détail de la consultation créée."""
    assert _consultation_id
    res = await client.get(f"/api/v1/consultations/{_consultation_id}", headers=medecin_headers)
    assert res.status_code == 200
    assert res.json()["id"] == _consultation_id


async def test_sauvegarder_antecedents(client, medecin_headers):
    """PATCH /consultations/:id/antecedents sauvegarde les antécédents."""
    assert _consultation_id
    payload = {"diabete": True, "hypertension": False, "tabac": "non"}
    res = await client.patch(
        f"/api/v1/consultations/{_consultation_id}/antecedents",
        json=payload,
        headers=medecin_headers,
    )
    assert res.status_code == 200


async def test_sauvegarder_symptomes(client, medecin_headers):
    """PATCH /consultations/:id/symptomes sauvegarde les symptômes."""
    assert _consultation_id
    payload = {"toux": True, "fievre": True, "temperature": 38.5}
    res = await client.patch(
        f"/api/v1/consultations/{_consultation_id}/symptomes",
        json=payload,
        headers=medecin_headers,
    )
    assert res.status_code == 200


async def test_changer_statut_clinique(client, medecin_headers):
    """PATCH /consultations/:id/statut-clinique met à jour le statut clinique."""
    assert _consultation_id
    res = await client.patch(
        f"/api/v1/consultations/{_consultation_id}/statut-clinique",
        json={"statut_clinique": "surveille"},
        headers=medecin_headers,
    )
    assert res.status_code == 200
    assert res.json()["statut_clinique"] == "surveille"


async def test_cas_graves(client, medecin_headers):
    """GET /consultations/cas-graves retourne la liste des cas urgents/critiques."""
    res = await client.get("/api/v1/consultations/cas-graves", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_consultations_sans_token_refuse(client):
    """Accéder aux consultations sans token → 401 ou 403."""
    res = await client.get("/api/v1/consultations")
    assert res.status_code in (401, 403)


async def test_consultation_inexistante(client, medecin_headers):
    """GET /consultations/:id avec un ID inconnu → 404."""
    res = await client.get("/api/v1/consultations/ID-INEXISTANT", headers=medecin_headers)
    assert res.status_code == 404

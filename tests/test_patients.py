"""
Tests patients — PneumoIA
Couvre : création, liste, recherche, détail, modification, suppression, restauration
"""
import pytest

pytestmark = pytest.mark.anyio

PATIENT_DATA = {
    "civilite":  "M",
    "nom":       "Dupont",
    "prenom":    "Jean",
    "telephone": "+237600000001",
}

# Stocke l'ID du patient créé pour les tests suivants
_patient_id = None


async def test_creer_patient(client, medecin_headers):
    """Un médecin validé peut créer un patient."""
    global _patient_id
    res = await client.post("/api/v1/patients", json=PATIENT_DATA, headers=medecin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["nom"] == "DUPONT"
    assert "id" in data
    _patient_id = data["id"]


async def test_mes_patients(client, medecin_headers):
    """GET /patients/mes-patients retourne la liste des patients du médecin."""
    res = await client.get("/api/v1/patients/mes-patients", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_rechercher_patients(client, medecin_headers):
    """GET /patients/search?q=du retourne une liste."""
    res = await client.get("/api/v1/patients/search?q=du", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_get_patient(client, medecin_headers):
    """GET /patients/:id retourne le détail du patient créé."""
    assert _patient_id, "Le patient n'a pas été créé par test_creer_patient"
    res = await client.get(f"/api/v1/patients/{_patient_id}", headers=medecin_headers)
    assert res.status_code == 200
    assert res.json()["id"] == _patient_id


async def test_modifier_patient(client, medecin_headers):
    """PATCH /patients/:id met à jour les informations du patient."""
    assert _patient_id
    payload = {**PATIENT_DATA, "prenom": "Jean-Pierre"}
    res = await client.patch(f"/api/v1/patients/{_patient_id}", json=payload, headers=medecin_headers)
    assert res.status_code == 200
    assert res.json()["prenom"] == "Jean-Pierre"


async def test_demandes_envoyees(client, medecin_headers):
    """GET /patients/access-requests/envoyees retourne une liste."""
    res = await client.get("/api/v1/patients/access-requests/envoyees", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_demandes_recues(client, medecin_headers):
    """GET /patients/access-requests/recues retourne une liste."""
    res = await client.get("/api/v1/patients/access-requests/recues", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_corbeille_patients(client, medecin_headers):
    """GET /patients/corbeille retourne une liste."""
    res = await client.get("/api/v1/patients/corbeille", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_supprimer_patient(client, medecin_headers):
    """DELETE /patients/:id déplace le patient en corbeille (204)."""
    assert _patient_id
    res = await client.delete(f"/api/v1/patients/{_patient_id}", headers=medecin_headers)
    assert res.status_code == 204


async def test_restaurer_patient(client, medecin_headers):
    """PATCH /patients/:id/restaurer remet le patient depuis la corbeille."""
    assert _patient_id
    res = await client.patch(f"/api/v1/patients/{_patient_id}/restaurer", headers=medecin_headers)
    assert res.status_code == 200
    assert res.json()["id"] == _patient_id


async def test_patients_sans_token_refuse(client):
    """Accéder aux patients sans token → 401 ou 403."""
    res = await client.get("/api/v1/patients/mes-patients")
    assert res.status_code in (401, 403)


async def test_patient_inexistant(client, medecin_headers):
    """GET /patients/:id avec un ID inconnu → 404."""
    res = await client.get("/api/v1/patients/ID-INEXISTANT", headers=medecin_headers)
    assert res.status_code == 404

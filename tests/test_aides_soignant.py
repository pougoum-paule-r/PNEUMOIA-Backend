"""
Tests côté aide soignant — PneumoIA
Couvre : profil, patients, préférences, consultations, messages équipe
"""
import pytest

pytestmark = pytest.mark.anyio

_patient_aide_id     = None
_consultation_aide_id = None


# ── Profil ────────────────────────────────────────────────────────

async def test_get_profil_aide(client, aide_headers):
    """GET /aides/me retourne le profil de l'aide soignant connecté."""
    res = await client.get("/api/v1/aides/me", headers=aide_headers)
    assert res.status_code == 200
    data = res.json()
    assert "id" in data
    assert "permissions" in data


async def test_update_profil_aide(client, aide_headers):
    """PATCH /aides/me met à jour le profil."""
    res = await client.patch("/api/v1/aides/me",
                             json={"prenom": "TestModifié"},
                             headers=aide_headers)
    assert res.status_code == 200
    assert res.json()["prenom"] == "TestModifié"


async def test_get_preferences_aide(client, aide_headers):
    """GET /aides/me/preferences retourne les préférences."""
    res = await client.get("/api/v1/aides/me/preferences", headers=aide_headers)
    assert res.status_code == 200
    data = res.json()
    assert "notif_email" in data or "theme" in data


async def test_update_preferences_aide(client, aide_headers):
    """PATCH /aides/me/preferences met à jour une préférence."""
    res = await client.patch("/api/v1/aides/me/preferences",
                             json={"theme": "dark"},
                             headers=aide_headers)
    assert res.status_code == 200


# ── Patients ──────────────────────────────────────────────────────

async def test_get_patients_aide(client, aide_headers):
    """GET /aides/patients retourne la liste des patients du médecin référent."""
    res = await client.get("/api/v1/aides/patients", headers=aide_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_creer_patient_aide(client, aide_headers):
    """POST /aides/patients crée un patient via l'aide soignant."""
    global _patient_aide_id
    res = await client.post("/api/v1/aides/patients", json={
        "nom":    "BenTest",
        "prenom": "Alice",
        "civilite": "Mme",
        "telephone": "+237600000099",
    }, headers=aide_headers)
    assert res.status_code == 201
    data = res.json()
    assert "id" in data
    _patient_aide_id = data["id"]


async def test_get_patient_aide(client, aide_headers):
    """GET /aides/patients/:id retourne le dossier d'un patient."""
    assert _patient_aide_id
    res = await client.get(f"/api/v1/aides/patients/{_patient_aide_id}", headers=aide_headers)
    assert res.status_code == 200


async def test_modifier_patient_aide(client, aide_headers):
    """PATCH /aides/patients/:id modifie les infos du patient."""
    assert _patient_aide_id
    res = await client.patch(f"/api/v1/aides/patients/{_patient_aide_id}",
                             json={"prenom": "Alice-M"},
                             headers=aide_headers)
    assert res.status_code == 200


# ── Consultations ─────────────────────────────────────────────────

async def test_creer_consultation_aide(client, aide_headers):
    """POST /aides/consultations crée une consultation pour un patient."""
    global _consultation_aide_id
    assert _patient_aide_id
    res = await client.post("/api/v1/aides/consultations",
                            json={"patient_id": _patient_aide_id},
                            headers=aide_headers)
    assert res.status_code == 201
    _consultation_aide_id = res.json()["id"]


async def test_sauvegarder_antecedents_aide(client, aide_headers):
    """PATCH /aides/consultations/:id/antecedents sauvegarde les antécédents."""
    assert _consultation_aide_id
    res = await client.patch(
        f"/api/v1/aides/consultations/{_consultation_aide_id}/antecedents",
        json={"diabete": False, "hypertension": True},
        headers=aide_headers,
    )
    assert res.status_code == 200


async def test_sauvegarder_symptomes_aide(client, aide_headers):
    """PATCH /aides/consultations/:id/symptomes sauvegarde les symptômes."""
    assert _consultation_aide_id
    res = await client.patch(
        f"/api/v1/aides/consultations/{_consultation_aide_id}/symptomes",
        json={"toux": True, "temperature": 37.5},
        headers=aide_headers,
    )
    assert res.status_code == 200


# ── Accès refusé ─────────────────────────────────────────────────

async def test_aide_ne_peut_pas_acceder_routes_medecin(client, aide_headers):
    """Un aide soignant ne peut pas accéder aux routes réservées au médecin.
    Le backend retourne 401/403 (rôle refusé) ou 404 (médecin introuvable
    avec cet ID) — dans tous les cas l'accès est bien bloqué.
    """
    res = await client.get("/api/v1/patients/mes-patients", headers=aide_headers)
    assert res.status_code in (401, 403, 404)


async def test_aide_routes_sans_token_refuse(client):
    """GET /aides/me sans token → 401 ou 403."""
    res = await client.get("/api/v1/aides/me")
    assert res.status_code in (401, 403)

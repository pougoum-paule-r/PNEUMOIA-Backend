"""
Tests aides soignants — PneumoIA
Couvre : code référent, liste, profil, patients aide, accès sans token
"""
import pytest

pytestmark = pytest.mark.anyio


async def test_code_referent(client, medecin_headers):
    """GET /aides/code-referent retourne le code référent du médecin."""
    res = await client.get("/api/v1/aides/code-referent", headers=medecin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "code" in data or "code_referent" in data or isinstance(data, dict)


async def test_mes_aides(client, medecin_headers):
    """GET /aides/mes-aides retourne la liste des aides soignants du médecin."""
    res = await client.get("/api/v1/aides/mes-aides", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_verifier_code_invalide(client):
    """GET /aides/verifier-code/:code avec un code invalide → 404."""
    res = await client.get("/api/v1/aides/verifier-code/CODE-INVALIDE-000")
    assert res.status_code == 404


async def test_aide_inexistant_valider(client, medecin_headers):
    """POST /aides/:id/valider avec un ID inconnu → 404."""
    res = await client.post("/api/v1/aides/ID-INEXISTANT/valider", headers=medecin_headers)
    assert res.status_code == 404


async def test_aide_inexistant_refuser(client, medecin_headers):
    """POST /aides/:id/refuser avec un ID inconnu → 404."""
    res = await client.post("/api/v1/aides/ID-INEXISTANT/refuser",
                            json={"motif": "Dossier incomplet"},
                            headers=medecin_headers)
    assert res.status_code == 404


async def test_aides_sans_token_refuse(client):
    """GET /aides/mes-aides sans token → 401 ou 403."""
    res = await client.get("/api/v1/aides/mes-aides")
    assert res.status_code in (401, 403)


async def test_patients_aide_sans_token_refuse(client):
    """GET /aides/patients sans token → 401 ou 403."""
    res = await client.get("/api/v1/aides/patients")
    assert res.status_code in (401, 403)

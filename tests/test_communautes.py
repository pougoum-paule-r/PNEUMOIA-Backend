"""
Tests communautés — PneumoIA
Couvre : liste, cas cliniques, rejoindre, accès sans token
"""
import pytest

pytestmark = pytest.mark.anyio

_communaute_id = None


async def test_liste_communautes(client, medecin_headers):
    """GET /communautes retourne la liste des communautés."""
    res = await client.get("/api/v1/communautes", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_liste_cas_cliniques(client, medecin_headers):
    """GET /communautes/cas-cliniques retourne la liste des cas publics."""
    res = await client.get("/api/v1/communautes/cas-cliniques", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_rejoindre_communaute_inexistante(client, medecin_headers):
    """POST /communautes/:id/rejoindre avec un ID inconnu → 404."""
    res = await client.post("/api/v1/communautes/ID-INEXISTANT/rejoindre", headers=medecin_headers)
    assert res.status_code == 404


async def test_membres_communaute_inexistante(client, medecin_headers):
    """GET /communautes/:id/membres avec un ID inconnu → 404."""
    res = await client.get("/api/v1/communautes/ID-INEXISTANT/membres", headers=medecin_headers)
    assert res.status_code == 404


async def test_communautes_sans_token_refuse(client):
    """Accéder aux communautés sans token → 401 ou 403."""
    res = await client.get("/api/v1/communautes")
    assert res.status_code in (401, 403)


async def test_cas_cliniques_sans_token_refuse(client):
    """Accéder aux cas cliniques sans token → 401 ou 403."""
    res = await client.get("/api/v1/communautes/cas-cliniques")
    assert res.status_code in (401, 403)

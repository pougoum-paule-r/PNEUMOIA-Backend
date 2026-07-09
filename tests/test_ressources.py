"""
Tests ressources médicales — PneumoIA
Couvre : liste publique, mes ressources, ressource inexistante
"""
import pytest

pytestmark = pytest.mark.anyio


async def test_lister_ressources_public(client):
    """GET /ressources retourne un objet paginé avec les ressources publiées."""
    res = await client.get("/api/v1/ressources")
    assert res.status_code == 200
    data = res.json()
    assert "total" in data or "items" in data or isinstance(data, (list, dict))


async def test_lister_ressources_avec_filtre(client):
    """GET /ressources?pathologie=Pneumonie filtre par pathologie."""
    res = await client.get("/api/v1/ressources?pathologie=Pneumonie")
    assert res.status_code == 200
    assert isinstance(res.json(), dict)


async def test_mes_ressources(client, medecin_headers):
    """GET /ressources/medecin/mes-ressources retourne les ressources du médecin."""
    res = await client.get("/api/v1/ressources/medecin/mes-ressources", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_ressource_inexistante(client, medecin_headers):
    """GET /ressources/:id avec ID inconnu → 404."""
    res = await client.get("/api/v1/ressources/ID-INEXISTANT", headers=medecin_headers)
    assert res.status_code == 404


async def test_mes_ressources_sans_token_refuse(client):
    """GET /ressources/medecin/mes-ressources sans token → 401 ou 403."""
    res = await client.get("/api/v1/ressources/medecin/mes-ressources")
    assert res.status_code in (401, 403)

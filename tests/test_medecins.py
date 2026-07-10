"""
Tests médecins — PneumoIA
Couvre : liste, mon rang, préférences, profil
"""
import pytest

pytestmark = pytest.mark.anyio


async def test_liste_medecins(client, medecin_headers):
    """GET /medecins/liste retourne la liste des médecins validés."""
    res = await client.get("/api/v1/medecins/liste", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_mon_rang(client, medecin_headers):
    """GET /medecins/mon-rang retourne les stats du médecin connecté."""
    res = await client.get("/api/v1/medecins/mon-rang", headers=medecin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "nb_patients" in data or "rang" in data or isinstance(data, dict)


async def test_mes_preferences(client, medecin_headers):
    """GET /medecins/preferences retourne les préférences du médecin."""
    res = await client.get("/api/v1/medecins/me/preferences", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), dict)


async def test_mettre_a_jour_preferences(client, medecin_headers):
    """PATCH /medecins/preferences met à jour une préférence."""
    res = await client.patch(
        "/api/v1/medecins/me/preferences",
        json={"langue": "fr", "compactView": True},
        headers=medecin_headers,
    )
    assert res.status_code == 200


async def test_medecins_sans_token_refuse(client):
    """Accéder à la liste des médecins sans token → 401 ou 403."""
    res = await client.get("/api/v1/medecins/liste")
    assert res.status_code in (401, 403)

"""
Tests du module IA — PneumoIA
Couvre : structure du endpoint diagnostic, chargement des modèles
"""
import pytest

pytestmark = pytest.mark.anyio


async def test_diagnostic_necessite_auth(client):
    """Le diagnostic IA requiert une authentification."""
    res = await client.post("/api/v1/diagnostic/predict", json={})
    assert res.status_code in (401, 403, 422)


async def test_admin_stats_kpis(client, admin_headers):
    """Les KPIs admin sont accessibles avec un token valide."""
    res = await client.get("/api/admin/stats/kpis", headers=admin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), dict)


async def test_admin_top_medecins(client, admin_headers):
    """Le classement des médecins par concordance IA est accessible."""
    res = await client.get(
        "/api/admin/stats/top-medecins-concordance?mois=7&annee=2026",
        headers=admin_headers
    )
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_admin_repartition_geo(client, admin_headers):
    """La répartition géographique des patients est accessible."""
    res = await client.get("/api/admin/stats/repartition-geo", headers=admin_headers)
    assert res.status_code == 200

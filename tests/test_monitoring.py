"""
Tests monitoring — PneumoIA
Couvre : stats consultations, métriques IA, accès sans token
"""
import pytest

pytestmark = pytest.mark.anyio


async def test_monitoring_stats_semaine(client, medecin_headers):
    """GET /monitoring/stats?periode=week retourne les stats de la semaine."""
    res = await client.get("/api/v1/monitoring/stats?periode=week", headers=medecin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "consult_par_jour" in data
    assert "concordance_data" in data


async def test_monitoring_stats_mois(client, medecin_headers):
    """GET /monitoring/stats?periode=month retourne les stats du mois."""
    res = await client.get("/api/v1/monitoring/stats?periode=month", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), dict)


async def test_monitoring_stats_aujourd_hui(client, medecin_headers):
    """GET /monitoring/stats?periode=today retourne les stats du jour."""
    res = await client.get("/api/v1/monitoring/stats?periode=today", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), dict)


async def test_ia_metrics(client, medecin_headers):
    """GET /monitoring/ia-metrics retourne les métriques IA."""
    res = await client.get("/api/v1/monitoring/ia-metrics", headers=medecin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_diagnostics" in data
    assert "concordance_rate" in data


async def test_monitoring_sans_token_refuse(client):
    """Accéder au monitoring sans token → 401 ou 403."""
    res = await client.get("/api/v1/monitoring/stats")
    assert res.status_code in (401, 403)

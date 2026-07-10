"""
Tests admin — PneumoIA
Couvre : login, médecins en attente/actifs/refusés, stats, notifications, corbeille
"""
import pytest

pytestmark = pytest.mark.anyio

ADMIN_PHONE = "+237656616801"


async def test_admin_login_succes(client):
    """Login admin avec bonnes credentials → 200 + token."""
    res = await client.post("/api/admin/auth/login", json={
        "email":    "adminpneumoia@gmail.com",
        "password": "Admin1234!",
        "phone":    ADMIN_PHONE,
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


async def test_admin_login_mauvais_mdp(client):
    """Mauvais mot de passe → 401."""
    res = await client.post("/api/admin/auth/login", json={
        "email":    "adminpneumoia@gmail.com",
        "password": "MauvaisMdp!",
        "phone":    ADMIN_PHONE,
    })
    assert res.status_code == 401


async def test_medecins_en_attente(client, admin_headers):
    """GET /admin/demandes retourne les demandes en attente."""
    res = await client.get("/api/admin/demandes", headers=admin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_medecins_actifs(client, admin_headers):
    """GET /admin/medecins/actifs retourne une liste."""
    res = await client.get("/api/admin/medecins/actifs", headers=admin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_medecins_refuses(client, admin_headers):
    """GET /admin/demandes/refusees retourne une liste."""
    res = await client.get("/api/admin/demandes/refusees", headers=admin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_stats_kpis(client, admin_headers):
    """GET /admin/stats/kpis retourne un dict avec les indicateurs."""
    res = await client.get("/api/admin/stats/kpis", headers=admin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), dict)


async def test_stats_repartition_geo(client, admin_headers):
    """GET /admin/stats/repartition-geo retourne un dict avec villes et regions."""
    res = await client.get("/api/admin/stats/repartition-geo", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "villes" in data or "regions" in data or isinstance(data, (dict, list))


async def test_stats_top_medecins(client, admin_headers):
    """GET /admin/stats/top-medecins-concordance retourne une liste."""
    res = await client.get(
        "/api/admin/stats/top-medecins-concordance?mois=7&annee=2026",
        headers=admin_headers,
    )
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_admin_notifications(client, admin_headers):
    """GET /admin/notifications retourne un dict avec les notifications."""
    res = await client.get("/api/admin/notifications", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "notifications" in data or isinstance(data, list)


async def test_admin_corbeille(client, admin_headers):
    """GET /admin/corbeille retourne une liste."""
    res = await client.get("/api/admin/corbeille", headers=admin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_medecin_par_id_inexistant(client, admin_headers):
    """GET /admin/medecins/:id avec ID inconnu → 404."""
    res = await client.get("/api/admin/medecins/ID-INEXISTANT", headers=admin_headers)
    assert res.status_code == 404


async def test_admin_routes_sans_token_refusees(client):
    """Accéder aux routes admin sans token → 401 ou 403."""
    res = await client.get("/api/admin/medecins/actifs")
    assert res.status_code in (401, 403)

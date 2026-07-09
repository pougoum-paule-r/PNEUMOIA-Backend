"""
Tests notifications — PneumoIA
Couvre : liste, compteur, marquer lue, tout lire, supprimer
"""
import pytest

pytestmark = pytest.mark.anyio


async def test_get_notifications(client, medecin_headers):
    """GET /notifications retourne la liste des notifications."""
    res = await client.get("/api/v1/notifications", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_count_non_lues(client, medecin_headers):
    """GET /notifications/count retourne le nombre de non lues."""
    res = await client.get("/api/v1/notifications/count", headers=medecin_headers)
    assert res.status_code == 200
    assert "count" in res.json()


async def test_tout_marquer_lu(client, medecin_headers):
    """PATCH /notifications/tout-lire marque toutes les notifs comme lues."""
    res = await client.patch("/api/v1/notifications/tout-lire", headers=medecin_headers)
    assert res.status_code == 200


async def test_supprimer_toutes_lues(client, medecin_headers):
    """DELETE /notifications supprime toutes les notifications lues."""
    res = await client.delete("/api/v1/notifications", headers=medecin_headers)
    assert res.status_code == 200


async def test_notification_inexistante(client, medecin_headers):
    """PATCH /notifications/:id/lire avec ID inconnu → 404."""
    res = await client.patch("/api/v1/notifications/ID-INEXISTANT/lire", headers=medecin_headers)
    assert res.status_code == 404


async def test_notifications_sans_token_refuse(client):
    """Accéder aux notifications sans token → 401 ou 403."""
    res = await client.get("/api/v1/notifications")
    assert res.status_code in (401, 403)

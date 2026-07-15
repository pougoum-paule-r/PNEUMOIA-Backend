"""
Tests canal équipe — PneumoIA
Couvre : liste messages, créer, répondre, liker, épingler, supprimer
"""
import pytest

pytestmark = pytest.mark.anyio

_message_id = None


async def test_liste_messages(client, medecin_headers):
    """GET /equipe/messages retourne la liste des messages de l'équipe."""
    res = await client.get("/api/v1/equipe/messages", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_creer_message(client, medecin_headers):
    """POST /equipe/messages crée un nouveau message."""
    global _message_id
    res = await client.post("/api/v1/equipe/messages", json={
        "contenu":  "Rapport de garde — tout est stable.",
        "type_msg": "rapport",
    }, headers=medecin_headers)
    assert res.status_code == 201
    data = res.json()
    assert "id" in data
    _message_id = data["id"]


async def test_creer_message_type_invalide(client, medecin_headers):
    """POST /equipe/messages avec type_msg invalide → 422."""
    res = await client.post("/api/v1/equipe/messages", json={
        "contenu":  "Message test",
        "type_msg": "type_invalide",
    }, headers=medecin_headers)
    assert res.status_code == 422


async def test_repondre_message(client, medecin_headers):
    """POST /equipe/messages/:id/reply répond à un message."""
    assert _message_id
    res = await client.post(
        f"/api/v1/equipe/messages/{_message_id}/reply",
        json={"contenu": "Bien reçu, merci."},
        headers=medecin_headers,
    )
    assert res.status_code == 201


async def test_liker_message(client, medecin_headers):
    """POST /equipe/messages/:id/like toggle le like."""
    assert _message_id
    res = await client.post(
        f"/api/v1/equipe/messages/{_message_id}/like",
        headers=medecin_headers,
    )
    assert res.status_code == 200
    assert "liked" in res.json()


async def test_epingler_message(client, medecin_headers):
    """PATCH /equipe/messages/:id/pin épingle le message."""
    assert _message_id
    res = await client.patch(
        f"/api/v1/equipe/messages/{_message_id}/pin",
        headers=medecin_headers,
    )
    assert res.status_code == 200
    assert "pinned" in res.json()


async def test_supprimer_message(client, medecin_headers):
    """DELETE /equipe/messages/:id supprime le message."""
    assert _message_id
    res = await client.delete(
        f"/api/v1/equipe/messages/{_message_id}",
        headers=medecin_headers,
    )
    assert res.status_code == 204


async def test_message_inexistant(client, medecin_headers):
    """POST /equipe/messages/:id/reply avec ID inconnu → 404."""
    res = await client.post(
        "/api/v1/equipe/messages/ID-INEXISTANT/reply",
        json={"contenu": "test"},
        headers=medecin_headers,
    )
    assert res.status_code == 404


async def test_messages_sans_token_refuse(client):
    """GET /equipe/messages sans token → 401 ou 403."""
    res = await client.get("/api/v1/equipe/messages")
    assert res.status_code in (401, 403)

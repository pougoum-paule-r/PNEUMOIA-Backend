"""
Tests publications — PneumoIA
Couvre : liste du feed, créer une publication, réactions, accès sans token
"""
import pytest

pytestmark = pytest.mark.anyio

_publication_id = None


async def test_feed_publications(client, medecin_headers):
    """GET /publications retourne le feed des publications."""
    res = await client.get("/api/v1/publications", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_creer_publication(client, medecin_headers):
    """POST /publications crée une nouvelle publication."""
    global _publication_id
    res = await client.post("/api/v1/publications", json={
        "titre":   "Test publication pneumonie",
        "contenu": "Discussion sur la pneumonie bactérienne.",
        "type":    "discussion",
        "tags":    ["pneumonie", "bacterie"],
    }, headers=medecin_headers)
    assert res.status_code in (200, 201)
    data = res.json()
    assert "id" in data
    _publication_id = data["id"]


async def test_get_publication(client, medecin_headers):
    """GET /publications/:id retourne le détail d'une publication."""
    assert _publication_id
    res = await client.get(f"/api/v1/publications/{_publication_id}", headers=medecin_headers)
    assert res.status_code == 200


async def test_reagir_publication(client, medecin_headers):
    """POST /publications/:id/reactions ajoute une réaction."""
    assert _publication_id
    res = await client.post(
        f"/api/v1/publications/{_publication_id}/react",
        json={"type": "utile"},
        headers=medecin_headers,
    )
    assert res.status_code in (200, 201)


async def test_commenter_publication(client, medecin_headers):
    """POST /publications/:id/commentaires ajoute un commentaire."""
    assert _publication_id
    res = await client.post(
        f"/api/v1/publications/{_publication_id}/commentaires",
        json={"contenu": "Très intéressant, merci !"},
        headers=medecin_headers,
    )
    assert res.status_code in (200, 201)


async def test_publication_inexistante(client, medecin_headers):
    """GET /publications/:id avec ID inconnu → 404."""
    res = await client.get("/api/v1/publications/ID-INEXISTANT", headers=medecin_headers)
    assert res.status_code == 404


async def test_publications_sans_token_refuse(client):
    """Accéder au feed sans token → 401 ou 403."""
    res = await client.get("/api/v1/publications")
    assert res.status_code in (401, 403)

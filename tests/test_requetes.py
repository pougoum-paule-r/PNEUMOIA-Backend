"""
Tests requêtes médecins — PneumoIA
Couvre : soumettre une requête, lister mes requêtes, accès sans token
"""
import pytest

pytestmark = pytest.mark.anyio


async def test_soumettre_requete(client, medecin_headers):
    """POST /requetes soumet une requête au support."""
    res = await client.post("/api/v1/requetes", json={
        "titre":       "Problème de connexion",
        "description": "Je n'arrive pas à accéder au module de diagnostic.",
        "categorie":   "probleme_acces",
    }, headers=medecin_headers)
    assert res.status_code in (200, 201)


async def test_mes_requetes(client, medecin_headers):
    """GET /requetes/mes-requetes retourne la liste des requêtes du médecin."""
    res = await client.get("/api/v1/requetes/mes-requetes", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_requete_sans_titre_refuse(client, medecin_headers):
    """POST /requetes sans titre → 400."""
    res = await client.post("/api/v1/requetes", json={
        "titre":       "",
        "description": "Description valide.",
        "categorie":   "bug_technique",
    }, headers=medecin_headers)
    assert res.status_code == 400


async def test_requetes_sans_token_refuse(client):
    """Accéder aux requêtes sans token → 401 ou 403."""
    res = await client.get("/api/v1/requetes/mes-requetes")
    assert res.status_code in (401, 403)

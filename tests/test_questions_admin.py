"""
Tests questions admin — PneumoIA
Couvre : poser une question, mes questions, FAQ publiées, accès sans token
"""
import pytest

pytestmark = pytest.mark.anyio


async def test_poser_question(client, medecin_headers):
    """POST /questions-admin soumet une question à l'admin."""
    res = await client.post("/api/v1/questions-admin", json={
        "titre":   "Comment modifier mon profil ?",
        "message": "Je n'arrive pas à modifier ma photo de profil.",
    }, headers=medecin_headers)
    assert res.status_code == 201
    data = res.json()
    assert "id" in data
    assert data["titre"] == "Comment modifier mon profil ?"


async def test_mes_questions(client, medecin_headers):
    """GET /questions-admin/mes-questions retourne les questions du médecin."""
    res = await client.get("/api/v1/questions-admin/mes-questions", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) >= 1


async def test_faq_publiees(client, medecin_headers):
    """GET /questions-admin/faq-publiees retourne les FAQ publiées."""
    res = await client.get("/api/v1/questions-admin/faq-publiees", headers=medecin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_question_titre_vide_refuse(client, medecin_headers):
    """POST /questions-admin avec titre vide → 422."""
    res = await client.post("/api/v1/questions-admin", json={
        "titre":   "",
        "message": "Description valide.",
    }, headers=medecin_headers)
    assert res.status_code == 422


async def test_questions_sans_token_refuse(client):
    """GET /questions-admin/mes-questions sans token → 401 ou 403."""
    res = await client.get("/api/v1/questions-admin/mes-questions")
    assert res.status_code in (401, 403)

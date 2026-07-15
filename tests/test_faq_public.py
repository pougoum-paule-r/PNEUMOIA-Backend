"""
Tests FAQ publique — PneumoIA
Couvre : accès sans token, format de réponse
"""
import pytest

pytestmark = pytest.mark.anyio


async def test_faq_public_accessible_sans_token(client):
    """GET /faq-public est accessible sans authentification."""
    res = await client.get("/api/v1/faq-public")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_faq_public_format(client):
    """Chaque entrée FAQ contient les champs attendus."""
    res = await client.get("/api/v1/faq-public")
    assert res.status_code == 200
    faqs = res.json()
    for faq in faqs:
        assert "id" in faq
        assert "question" in faq
        assert "reponse" in faq

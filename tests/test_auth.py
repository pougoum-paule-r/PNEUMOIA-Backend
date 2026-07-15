"""
Tests d'authentification — PneumoIA
Couvre : login admin, login médecin invalide, OTP, reset password
"""
import pytest

pytestmark = pytest.mark.anyio

ADMIN_PHONE = "+237656616801"


async def test_admin_login_succes(client):
    """L'admin peut se connecter avec ses identifiants corrects."""
    res = await client.post("/api/admin/auth/login", json={
        "email": "adminpneumoia@gmail.com",
        "password": "Admin1234!",
        "phone": ADMIN_PHONE,
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["admin"]["email"] == "adminpneumoia@gmail.com"


async def test_admin_login_mauvais_mdp(client):
    """Un mauvais mot de passe retourne 401."""
    res = await client.post("/api/admin/auth/login", json={
        "email": "adminpneumoia@gmail.com",
        "password": "mauvais_mdp",
        "phone": ADMIN_PHONE,
    })
    assert res.status_code == 401


async def test_admin_login_email_inexistant(client):
    """Un email inconnu retourne 401."""
    res = await client.post("/api/admin/auth/login", json={
        "email": "inconnu@email.com",
        "password": "Admin1234!",
        "phone": ADMIN_PHONE,
    })
    assert res.status_code == 401


async def test_medecin_login_email_invalide(client):
    """Login médecin avec email inexistant → 401."""
    res = await client.post("/api/v1/auth/login", json={
        "email": "faux@email.com",
        "password": "Test1234!"
    })
    assert res.status_code == 401


async def test_forgot_password_email_inexistant(client):
    """Reset password avec email inconnu → 404."""
    res = await client.post("/api/v1/auth/forgot-password", json={
        "email": "inconnu@email.com"
    })
    assert res.status_code == 404


async def test_token_admin_donne_acces_medecins(client, admin_headers):
    """Un token admin valide permet d'accéder à la liste des médecins actifs."""
    res = await client.get("/api/admin/medecins/actifs", headers=admin_headers)
    assert res.status_code == 200


async def test_acces_sans_token_refuse(client):
    """Accéder à une route protégée sans token → 401 ou 403."""
    res = await client.get("/api/admin/medecins/actifs")
    assert res.status_code in (401, 403)


async def test_token_invalide_refuse(client):
    """Un token falsifié est rejeté."""
    res = await client.get("/api/admin/medecins/actifs", headers={
        "Authorization": "Bearer token_faux_12345"
    })
    assert res.status_code in (401, 403)

from app.extensions import db
from app.models import User
from tests.conftest import TEST_PASSWORD


def test_register_success(app, client):
    response = client.post(
        "/register",
        data={"username": "bob", "email": "bob@example.com", "password": TEST_PASSWORD, "confirm": TEST_PASSWORD},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Compte créé" in response.get_data(as_text=True)
    with app.app_context():
        user = db.session.scalar(db.select(User).filter_by(username="bob"))
        assert user is not None
        assert user.role == "USER"
        assert user.password_hash != TEST_PASSWORD


def test_register_rejects_short_password(client):
    response = client.post(
        "/register",
        data={"username": "bob", "email": "bob@example.com", "password": "short", "confirm": "short"},
    )
    assert response.status_code == 200
    assert "au moins 8 caractères" in response.get_data(as_text=True)


def test_register_rejects_duplicate_username(client, create_user):
    create_user("alice")
    response = client.post(
        "/register",
        data={"username": "alice", "email": "other@example.com", "password": TEST_PASSWORD, "confirm": TEST_PASSWORD},
    )
    assert "déjà utilisé" in response.get_data(as_text=True)


def test_login_success(login, create_user):
    create_user("alice")
    response = login("alice")
    assert response.status_code == 200
    assert "Tableau de bord" in response.get_data(as_text=True)


def test_login_wrong_password(login, create_user):
    create_user("alice")
    response = login("alice", "mauvais-mot-de-passe")
    assert "Identifiants invalides" in response.get_data(as_text=True)


def test_login_does_not_redirect_to_external_site(client, create_user):
    create_user("alice")
    response = client.post(
        "/login?next=https://evil.example.com",
        data={"username": "alice", "password": TEST_PASSWORD},
    )
    assert response.status_code == 302
    assert "evil" not in response.headers["Location"]


def test_logout(client, login, create_user):
    create_user("alice")
    login("alice")
    response = client.post("/logout", follow_redirects=True)
    assert "déconnecté" in response.get_data(as_text=True)
    after = client.get("/dashboard")
    assert after.status_code == 302
    assert "/login" in after.headers["Location"]

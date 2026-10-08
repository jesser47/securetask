from app.extensions import db
from app.models import Task


def _titles(app):
    with app.app_context():
        return [t.title for t in db.session.scalars(db.select(Task)).all()]


def test_create_task(app, client, login, create_user):
    create_user("alice")
    login("alice")
    response = client.post(
        "/tasks/new",
        data={"title": "Écrire le rapport", "description": "Version 1", "status": "TODO", "priority": "HIGH"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Écrire le rapport" in response.get_data(as_text=True)
    assert _titles(app) == ["Écrire le rapport"]


def test_create_task_requires_title(app, client, login, create_user):
    create_user("alice")
    login("alice")
    response = client.post("/tasks/new", data={"title": "  ", "status": "TODO", "priority": "LOW"})
    assert response.status_code == 200
    assert "obligatoire" in response.get_data(as_text=True)
    assert _titles(app) == []


def test_edit_task(app, client, login, create_user, create_task):
    uid = create_user("alice")
    task_id = create_task(uid, title="Ancien titre")
    login("alice")
    response = client.post(
        f"/tasks/{task_id}/edit",
        data={"title": "Nouveau titre", "description": "", "status": "DONE", "priority": "LOW"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        task = db.session.get(Task, task_id)
        assert task.title == "Nouveau titre"
        assert task.status == "DONE"
        assert task.priority == "LOW"


def test_delete_task(app, client, login, create_user, create_task):
    uid = create_user("alice")
    task_id = create_task(uid)
    login("alice")
    response = client.post(f"/tasks/{task_id}/delete", follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        assert db.session.get(Task, task_id) is None


def test_search_tasks(client, login, create_user, create_task):
    uid = create_user("alice")
    create_task(uid, title="Alpha déploiement")
    create_task(uid, title="Beta revue")
    login("alice")
    html = client.get("/tasks/?q=alpha").get_data(as_text=True)
    assert "Alpha déploiement" in html
    assert "Beta revue" not in html


def test_filter_by_status(client, login, create_user, create_task):
    uid = create_user("alice")
    create_task(uid, title="Finie", status="DONE")
    create_task(uid, title="Ouverte", status="TODO")
    login("alice")
    html = client.get("/tasks/?status=DONE").get_data(as_text=True)
    assert "Finie" in html
    assert "Ouverte" not in html


def test_tasks_require_authentication(client):
    for url in ("/tasks/", "/tasks/new", "/dashboard"):
        response = client.get(url)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

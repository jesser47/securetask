from app.extensions import db
from app.models import Role, Task


def test_user_cannot_edit_or_delete_other_users_task(app, client, login, create_user, create_task):
    owner_id = create_user("alice")
    create_user("bob")
    task_id = create_task(owner_id, title="Privée")
    login("bob")

    assert client.get(f"/tasks/{task_id}/edit").status_code == 404
    edit = client.post(f"/tasks/{task_id}/edit", data={"title": "Piratée", "status": "TODO", "priority": "LOW"})
    assert edit.status_code == 404
    assert client.post(f"/tasks/{task_id}/delete").status_code == 404

    with app.app_context():
        task = db.session.get(Task, task_id)
        assert task is not None
        assert task.title == "Privée"


def test_user_does_not_see_other_users_tasks(client, login, create_user, create_task):
    create_task(create_user("alice"), title="Secret d'Alice")
    create_user("bob")
    login("bob")
    assert "Secret" not in client.get("/tasks/").get_data(as_text=True)


def test_non_admin_cannot_access_admin_page(client, login, create_user):
    create_user("alice")
    login("alice")
    assert client.get("/admin/users").status_code == 403


def test_admin_can_list_users(client, login, create_user):
    create_user("root", role=Role.ADMIN)
    create_user("alice")
    login("root")
    response = client.get("/admin/users")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "root" in html and "alice" in html


def test_admin_page_requires_authentication(client):
    response = client.get("/admin/users")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

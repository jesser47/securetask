from app.services import task_service


def test_dashboard_stats(app, create_user, create_task):
    uid = create_user("alice")
    other = create_user("bob")
    create_task(uid, status="DONE", priority="HIGH")
    create_task(uid, status="IN_PROGRESS", priority="HIGH")
    create_task(uid, status="TODO", priority="LOW")
    create_task(other, status="TODO", priority="HIGH")
    with app.app_context():
        stats = task_service.dashboard_stats(uid)
    assert stats["total"] == 3
    assert stats["done"] == 1
    assert stats["in_progress"] == 1
    assert stats["todo"] == 1
    assert stats["high_priority"] == 1
    assert len(stats["recent"]) == 3


def test_dashboard_page_and_error_pages(client, login, create_user):
    create_user("alice")
    login("alice")
    assert client.get("/dashboard").status_code == 200
    missing = client.get("/page-inexistante")
    assert missing.status_code == 404
    assert "Page introuvable" in missing.get_data(as_text=True)


def test_health_endpoint(client):
    assert client.get("/health").get_json() == {"status": "ok"}

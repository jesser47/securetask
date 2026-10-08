import pytest

from app import create_app
from app.extensions import db
from app.models import Priority, Role, Status, Task, User
from config import TestConfig

TEST_PASSWORD = "Str0ng-Test-Passw0rd"


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def create_user(app):
    def _create(username="alice", password=TEST_PASSWORD, role=Role.USER):
        with app.app_context():
            user = User(username=username, email=f"{username}@example.com", role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return user.id

    return _create


@pytest.fixture()
def create_task(app):
    def _create(user_id, title="Tâche de test", status=Status.TODO, priority=Priority.MEDIUM, description=""):
        with app.app_context():
            task = Task(user_id=user_id, title=title, status=status, priority=priority, description=description)
            db.session.add(task)
            db.session.commit()
            return task.id

    return _create


@pytest.fixture()
def login(client):
    def _login(username="alice", password=TEST_PASSWORD):
        return client.post("/login", data={"username": username, "password": password}, follow_redirects=True)

    return _login

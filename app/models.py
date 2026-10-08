from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class Role:
    USER = "USER"
    ADMIN = "ADMIN"
    ALL = (USER, ADMIN)


class Status:
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    CHOICES = [(TODO, "À faire"), (IN_PROGRESS, "En cours"), (DONE, "Terminée")]
    ALL = tuple(v for v, _ in CHOICES)


class Priority:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CHOICES = [(LOW, "Basse"), (MEDIUM, "Moyenne"), (HIGH, "Haute")]
    ALL = tuple(v for v, _ in CHOICES)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(10), nullable=False, default=Role.USER)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    tasks = db.relationship(
        "Task", back_populates="owner", cascade="all, delete-orphan", lazy="select"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == Role.ADMIN

    def __repr__(self):
        return f"<User {self.username}>"


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    status = db.Column(db.String(15), nullable=False, default=Status.TODO)
    priority = db.Column(db.String(10), nullable=False, default=Priority.MEDIUM)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=utcnow, onupdate=utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    owner = db.relationship("User", back_populates="tasks")

    def __repr__(self):
        return f"<Task {self.id} {self.title!r}>"

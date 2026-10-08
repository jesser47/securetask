import re

from sqlalchemy import select

from app.extensions import db
from app.models import Role, User

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,64}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8


def validate_registration(username, email, password, confirm):
    errors = []
    username = (username or "").strip()
    email = (email or "").strip().lower()

    if not USERNAME_RE.match(username):
        errors.append("Nom d'utilisateur invalide (3 à 64 caractères : lettres, chiffres, . _ -).")
    if len(email) > 120 or not EMAIL_RE.match(email):
        errors.append("Adresse email invalide.")
    if len(password or "") < MIN_PASSWORD_LENGTH:
        errors.append(f"Le mot de passe doit contenir au moins {MIN_PASSWORD_LENGTH} caractères.")
    if password != confirm:
        errors.append("Les mots de passe ne correspondent pas.")

    if not errors:
        exists = db.session.scalar(
            select(User.id).where((User.username == username) | (User.email == email))
        )
        if exists:
            errors.append("Ce nom d'utilisateur ou cet email est déjà utilisé.")
    return errors


def create_user(username, email, password, role=Role.USER):
    user = User(username=username.strip(), email=email.strip().lower(), role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def authenticate(username, password):
    user = db.session.scalar(select(User).where(User.username == (username or "").strip()))
    if user is None or not user.check_password(password or ""):
        return None
    return user

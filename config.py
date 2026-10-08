"""Configuration de SecureTask (lue depuis les variables d'environnement)."""
import os
import secrets

from dotenv import load_dotenv

load_dotenv()


class Config:
    # Si SECRET_KEY n'est pas définie, une clé aléatoire est générée au démarrage
    # (pratique en dev ; en production, définir SECRET_KEY explicitement).
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///securetask.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
    WTF_CSRF_TIME_LIMIT = 3600


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = secrets.token_hex(32)
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False

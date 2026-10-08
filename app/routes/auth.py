from urllib.parse import urlparse

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.services import user_service

bp = Blueprint("auth", __name__)


def _is_safe_next(target):
    """N'autorise que les redirections relatives internes (anti open-redirect)."""
    if not target or "\\" in target:
        return False
    parsed = urlparse(target)
    return not parsed.scheme and not parsed.netloc and target.startswith("/") and not target.startswith("//")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    values = {}
    if request.method == "POST":
        username = request.form.get("username", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")
        errors = user_service.validate_registration(username, email, password, confirm)
        if not errors:
            try:
                user_service.create_user(username, email, password)
            except IntegrityError:
                db.session.rollback()
                errors.append("Ce nom d'utilisateur ou cet email est déjà utilisé.")
            else:
                flash("Compte créé avec succès. Vous pouvez vous connecter.", "success")
                return redirect(url_for("auth.login"))
        for error in errors:
            flash(error, "danger")
        values = {"username": username, "email": email}
    return render_template("auth/register.html", values=values)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    username = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        user = user_service.authenticate(username, request.form.get("password", ""))
        if user is None:
            flash("Identifiants invalides.", "danger")
        else:
            login_user(user)
            next_url = request.args.get("next")
            return redirect(next_url if _is_safe_next(next_url) else url_for("main.dashboard"))
    return render_template("auth/login.html", username=username)


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for("auth.login"))

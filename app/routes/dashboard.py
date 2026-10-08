from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import func, select

from app.decorators import admin_required
from app.extensions import db
from app.models import Task, User
from app.services import task_service

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))


@bp.route("/health")
def health():
    return {"status": "ok"}


@bp.route("/dashboard")
@login_required
def dashboard():
    stats = task_service.dashboard_stats(current_user.id)
    return render_template("dashboard.html", stats=stats)


@bp.route("/admin/users")
@admin_required
def admin_users():
    rows = db.session.execute(
        select(User, func.count(Task.id))
        .outerjoin(Task, Task.user_id == User.id)
        .group_by(User.id)
        .order_by(User.created_at)
    ).all()
    return render_template("admin/users.html", rows=rows)

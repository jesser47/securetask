from flask import abort
from sqlalchemy import func, or_, select

from app.extensions import db
from app.models import Priority, Status, Task

TITLE_MAX = 120
DESCRIPTION_MAX = 2000


def parse_task_form(form):
    """Valide les données du formulaire. Retourne (données, erreurs)."""
    data = {
        "title": (form.get("title") or "").strip(),
        "description": (form.get("description") or "").strip(),
        "status": form.get("status", Status.TODO),
        "priority": form.get("priority", Priority.MEDIUM),
    }
    errors = []
    if not data["title"]:
        errors.append("Le titre est obligatoire.")
    elif len(data["title"]) > TITLE_MAX:
        errors.append(f"Le titre ne doit pas dépasser {TITLE_MAX} caractères.")
    if len(data["description"]) > DESCRIPTION_MAX:
        errors.append(f"La description ne doit pas dépasser {DESCRIPTION_MAX} caractères.")
    if data["status"] not in Status.ALL:
        errors.append("Statut invalide.")
    if data["priority"] not in Priority.ALL:
        errors.append("Priorité invalide.")
    return data, errors


def _escape_like(value):
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def search_tasks(user_id, query=None, status=None):
    stmt = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc(), Task.id.desc())
    if query:
        pattern = f"%{_escape_like(query)}%"
        stmt = stmt.where(
            or_(Task.title.ilike(pattern, escape="\\"), Task.description.ilike(pattern, escape="\\"))
        )
    if status:
        stmt = stmt.where(Task.status == status)
    return db.session.scalars(stmt).all()


def get_user_task_or_404(user_id, task_id):
    task = db.session.get(Task, task_id)
    if task is None or task.user_id != user_id:
        abort(404)
    return task


def create_task(user_id, data):
    task = Task(user_id=user_id, **data)
    db.session.add(task)
    db.session.commit()
    return task


def update_task(task, data):
    for key, value in data.items():
        setattr(task, key, value)
    db.session.commit()
    return task


def delete_task(task):
    db.session.delete(task)
    db.session.commit()


def dashboard_stats(user_id):
    rows = db.session.execute(
        select(Task.status, func.count(Task.id)).where(Task.user_id == user_id).group_by(Task.status)
    ).all()
    by_status = dict(rows)
    high_priority = db.session.scalar(
        select(func.count(Task.id)).where(
            Task.user_id == user_id, Task.priority == Priority.HIGH, Task.status != Status.DONE
        )
    )
    recent = db.session.scalars(
        select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc(), Task.id.desc()).limit(5)
    ).all()
    return {
        "total": sum(by_status.values()),
        "done": by_status.get(Status.DONE, 0),
        "in_progress": by_status.get(Status.IN_PROGRESS, 0),
        "todo": by_status.get(Status.TODO, 0),
        "high_priority": high_priority or 0,
        "recent": recent,
    }

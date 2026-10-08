from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.models import Priority, Status
from app.services import task_service

bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@bp.route("/")
@login_required
def list_tasks():
    query = request.args.get("q", "").strip()[:100]
    status = request.args.get("status", "")
    if status not in Status.ALL:
        status = ""
    tasks = task_service.search_tasks(current_user.id, query, status or None)
    return render_template("tasks/list.html", tasks=tasks, q=query, status=status)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def create_task():
    values = {"status": Status.TODO, "priority": Priority.MEDIUM}
    if request.method == "POST":
        data, errors = task_service.parse_task_form(request.form)
        if not errors:
            task_service.create_task(current_user.id, data)
            flash("Tâche créée avec succès.", "success")
            return redirect(url_for("tasks.list_tasks"))
        for error in errors:
            flash(error, "danger")
        values = data
    return render_template("tasks/form.html", task=None, values=values)


@bp.route("/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = task_service.get_user_task_or_404(current_user.id, task_id)
    values = {
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
    }
    if request.method == "POST":
        data, errors = task_service.parse_task_form(request.form)
        if not errors:
            task_service.update_task(task, data)
            flash("Tâche modifiée avec succès.", "success")
            return redirect(url_for("tasks.list_tasks"))
        for error in errors:
            flash(error, "danger")
        values = data
    return render_template("tasks/form.html", task=task, values=values)


@bp.route("/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = task_service.get_user_task_or_404(current_user.id, task_id)
    task_service.delete_task(task)
    flash("Tâche supprimée.", "info")
    return redirect(url_for("tasks.list_tasks"))

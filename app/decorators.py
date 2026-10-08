from functools import wraps

from flask import abort, current_app
from flask_login import current_user


def admin_required(view):
    """Exige un utilisateur connecté avec le rôle ADMIN (401->login, 403 sinon)."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped

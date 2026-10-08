"""Application factory de SecureTask."""
import click
from flask import Flask, render_template
from flask_wtf.csrf import CSRFError

from app.extensions import csrf, db, login_manager
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
    login_manager.login_message_category = "warning"

    from app.models import Priority, Role, Status, User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.routes.auth import bp as auth_bp
    from app.routes.dashboard import bp as main_bp
    from app.routes.tasks import bp as tasks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(tasks_bp)

    @app.context_processor
    def inject_choices():
        return {"STATUS_CHOICES": Status.CHOICES, "PRIORITY_CHOICES": Priority.CHOICES}

    app.jinja_env.filters["status_label"] = lambda v: dict(Status.CHOICES).get(v, v)
    app.jinja_env.filters["priority_label"] = lambda v: dict(Priority.CHOICES).get(v, v)

    @app.after_request
    def set_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response

    @app.errorhandler(400)
    @app.errorhandler(CSRFError)
    def bad_request(error):
        return render_template("errors/400.html"), 400

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.cli.command("init-db")
    def init_db_command():
        """Crée les tables de la base de données."""
        db.create_all()
        click.echo("Base de données initialisée.")

    @app.cli.command("create-admin")
    @click.option("--username", prompt=True)
    @click.option("--email", prompt=True)
    @click.password_option()
    def create_admin_command(username, email, password):
        """Crée un compte administrateur."""
        from app.services import user_service

        errors = user_service.validate_registration(username, email, password, password)
        if errors:
            raise click.ClickException(" ".join(errors))
        user_service.create_user(username, email, password, role=Role.ADMIN)
        click.echo(f"Administrateur {username} créé.")

    # Initialisation propre de la base (idempotente)
    with app.app_context():
        db.create_all()

    return app

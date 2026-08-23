import os
import posixpath

import click
from flask import Flask, jsonify, send_from_directory

from .config import config_by_name
from .extensions import bcrypt, db, jwt, migrate

FRONTEND_DIR = os.environ.get("FRONTEND_DIR") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
)


def create_app(config_name: str = "dev") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)

    from .modules.auth.routes import auth_bp
    from .modules.admin.routes import admin_bp
    from .modules.posts.routes import posts_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(posts_bp)

    _register_static_frontend(app)
    _register_jwt_error_handlers()
    _register_cors(app)
    _register_seed_cli(app)

    return app


def _register_static_frontend(app: Flask) -> None:
    @app.route("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/openapi.yaml")
    def openapi_spec():
        return send_from_directory(
            FRONTEND_DIR, "openapi.yaml", mimetype="application/yaml"
        )

    @app.route("/<path:path>")
    def static_files(path):
        if "." not in posixpath.basename(path):
            path = path.rstrip("/") + ".html"
        return send_from_directory(FRONTEND_DIR, path)


def _register_jwt_error_handlers() -> None:
    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return jsonify(message="El token ha expirado."), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return jsonify(message="Token inválido."), 401

    @jwt.unauthorized_loader
    def missing_token(reason):
        return jsonify(message="Se requiere el encabezado Authorization: Bearer <token>."), 401


def _register_cors(app: Flask) -> None:
    @app.after_request
    def add_cors_headers(response):
        response.headers.setdefault("Access-Control-Allow-Origin", "*")
        response.headers.setdefault(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )
        response.headers.setdefault(
            "Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        )
        return response


SEED_FACULTIES = {
    "Ingeniería": ["Ingeniería de Sistemas", "Ingeniería Industrial"],
    "Ciencias Básicas": [],
}


def _register_seed_cli(app: Flask) -> None:
    @app.cli.command("seed-db")
    def seed_db():
        """Seed faculties and programs from the mockups (idempotent)."""
        from .modules.auth.models import Faculty, Program

        created = 0
        for faculty_name, program_names in SEED_FACULTIES.items():
            faculty = Faculty.query.filter_by(name=faculty_name).first()
            if faculty is None:
                faculty = Faculty(name=faculty_name)
                db.session.add(faculty)
                db.session.flush()
                created += 1
            for program_name in program_names:
                exists = Program.query.filter_by(
                    name=program_name, faculty_id=faculty.id
                ).first()
                if exists is None:
                    db.session.add(Program(name=program_name, faculty_id=faculty.id))
                    created += 1
        db.session.commit()
        click.echo(f"Seed completo ({created} registros creados).")

    @app.cli.command("seed-admin")
    def seed_admin():
        """Create the development administrator configured by environment."""
        from .modules.auth.models import ROLE_ADMINISTRATOR, STATUS_ACTIVE, User

        email = os.environ.get("ADMIN_DEMO_EMAIL", "admin.demo@unilibre.edu.co").strip().lower()
        password = os.environ.get("ADMIN_DEMO_PASSWORD")
        name = os.environ.get("ADMIN_DEMO_NAME", "Administrador Demo").strip()
        if not password:
            raise click.ClickException("ADMIN_DEMO_PASSWORD es obligatorio para seed-admin.")
        user = User.query.filter_by(email=email).first()
        if user is None:
            user = User(email=email)
            db.session.add(user)
        user.full_name = name or "Administrador Demo"
        user.role = ROLE_ADMINISTRATOR
        user.status = STATUS_ACTIVE
        user.set_password(password)
        db.session.commit()
        click.echo(f"Administrador demo listo: {email}")

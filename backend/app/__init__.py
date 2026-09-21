import os
import posixpath

import click
from flask import Flask, jsonify, render_template, send_from_directory

from .config import config_by_name
from .extensions import bcrypt, db, jwt, migrate
from .services.seed_service import (
    SEED_USERS_DEFAULT_PASSWORD,
    seed_admin as seed_admin_users,
    seed_db as seed_catalog,
    seed_users as seed_demo_users,
)

# Re-exported for tests
__all__ = ["create_app", "SEED_USERS_DEFAULT_PASSWORD"]


def create_app(config_name: str = "dev") -> Flask:
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)

    from app import models  # noqa: F401 — register metadata for Alembic/create_all
    from app.routes import admin_bp, auth_bp, posts_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(posts_bp)

    _register_pages(app)
    _register_jwt_error_handlers()
    _register_cors(app)
    _register_seed_cli(app)

    return app


def _register_pages(app: Flask) -> None:
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/openapi.yaml")
    def openapi_spec():
        return send_from_directory(
            app.static_folder, "openapi.yaml", mimetype="application/yaml"
        )

    @app.route("/<path:path>")
    def pages(path: str):
        basename = posixpath.basename(path)
        if "." not in basename:
            template = path.rstrip("/") + ".html"
            return render_template(template)
        static_path = os.path.join(app.static_folder, path)
        if os.path.isfile(static_path):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, path)


def _register_jwt_error_handlers() -> None:
    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return jsonify(message="El token ha expirado."), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return jsonify(message="Token inválido."), 401

    @jwt.unauthorized_loader
    def missing_token(reason):
        return jsonify(
            message="Se requiere el encabezado Authorization: Bearer <token>."
        ), 401


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


def _register_seed_cli(app: Flask) -> None:
    @app.cli.command("seed-db")
    def seed_db():
        """Seed faculties and programs from the mockups (idempotent)."""
        created = seed_catalog()
        click.echo(f"Seed completo ({created} registros creados).")

    @app.cli.command("seed-admin")
    def seed_admin():
        """Create the development administrator configured by environment."""
        email = os.environ.get(
            "ADMIN_DEMO_EMAIL", "admin.demo@unilibre.edu.co"
        ).strip().lower()
        password = os.environ.get("ADMIN_DEMO_PASSWORD")
        name = os.environ.get("ADMIN_DEMO_NAME", "Administrador Demo").strip()
        if not password:
            raise click.ClickException(
                "ADMIN_DEMO_PASSWORD es obligatorio para seed-admin."
            )
        ready = seed_admin_users(email, password, name)
        click.echo(f"Administrador demo listo: {ready}")

    @app.cli.command("seed-users")
    def seed_users():
        """Seed demo users (one per role) idempotently for development."""
        created, updated = seed_demo_users()
        click.echo(
            "Usuarios demo listos: "
            f"{created} creados, {updated} actualizados (rol/estado/contraseña normalizados)."
        )

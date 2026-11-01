import os
import posixpath

import click
from flask import Flask, abort, jsonify, render_template, request, send_from_directory
from jinja2 import TemplateNotFound

from .config import config_by_name
from .extensions import bcrypt, db, jwt, migrate
from .services.seed_service import (
    SEED_USERS_DEFAULT_PASSWORD,
    seed_admin as seed_admin_users,
    seed_db as seed_catalog,
    seed_demo as run_seed_demo,
)

# Re-exported for tests
__all__ = ["create_app", "SEED_USERS_DEFAULT_PASSWORD"]


def create_app(config_name: str = "dev") -> Flask:
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )
    config_class = config_by_name[config_name]
    if hasattr(config_class, "validate"):
        config_class.validate()
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)

    from app import models  # noqa: F401 — register metadata for Alembic/create_all
    from app.routes import ALL_BLUEPRINTS

    for blueprint in ALL_BLUEPRINTS:
        app.register_blueprint(blueprint)

    _register_pages(app)
    _register_jwt_error_handlers()
    _register_cors(app)
    _register_seed_cli(app)

    return app


LEGAL_PAGES = {
    "privacidad": {
        "title": "Política de privacidad",
        "body": "RIUL trata los datos personales de la comunidad investigadora de la Universidad Libre únicamente para operar la plataforma, conforme a la Ley 1581 de 2012 de protección de datos.",
    },
    "terminos": {
        "title": "Términos de uso",
        "body": "El acceso a RIUL está reservado a la comunidad académica. Los contenidos publicados son responsabilidad de sus autores y deben respetar la propiedad intelectual y el reglamento institucional.",
    },
    "contacto": {
        "title": "Contacto",
        "body": "Dirección de Investigaciones, Universidad Libre, Barranquilla, Atlántico. Escríbenos a investigaciones@unilibre.edu.co.",
    },
}


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
        if path.startswith("api/"):
            return jsonify(message="Recurso no encontrado."), 404
        if path.rstrip("/") in LEGAL_PAGES:
            return render_template("legal.html", page=LEGAL_PAGES[path.rstrip("/")])
        if path.rstrip("/") == "styleguide" and not (app.debug or app.testing):
            abort(404)
        basename = posixpath.basename(path)
        if "." not in basename:
            template = path.rstrip("/") + ".html"
            try:
                return render_template(template)
            except TemplateNotFound:
                abort(404)
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
    allowed = [o.strip() for o in app.config["CORS_ORIGINS"].split(",") if o.strip()]

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin", "")
        if allowed == ["*"]:
            response.headers.setdefault("Access-Control-Allow-Origin", "*")
        elif origin in allowed:
            response.headers.setdefault("Access-Control-Allow-Origin", origin)
            response.headers.setdefault("Vary", "Origin")
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

    @app.cli.command("seed-demo")
    def seed_demo():
        """Replace users/posts with the complete RIUL demo dataset (idempotent)."""
        counts = run_seed_demo()
        click.echo(
            "Seed demo completo: "
            + ", ".join(f"{k}={v}" for k, v in counts.items())
            + f" ({counts['facultades_nuevas']} facultades nuevas)."
        )


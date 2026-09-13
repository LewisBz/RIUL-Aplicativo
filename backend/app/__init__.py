import os
import posixpath

import click
from flask import Flask, jsonify, send_from_directory

from .config import config_by_name
from .extensions import bcrypt, db, jwt, migrate
from .seed_data import (
    SEED_DEMO_POSTS,
    SEED_DEMO_REACTIONS,
    SEED_DEMO_USERS,
    SEED_FACULTIES,
)

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


SEED_USERS_PASSWORD_ENV = "DEMO_USERS_PASSWORD"
SEED_USERS_DEFAULT_PASSWORD = "RiulDemo2026*"


def _register_seed_cli(app: Flask) -> None:
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

    @app.cli.command("seed-demo")
    def seed_demo():
        """Replace app data with the complete RIUL demo dataset (idempotent).

        Purges existing reactions, attachments, posts and users, then rebuilds
        the full demo dataset defined in app/seed_data.py: faculties, programs,
        15 users (administrators/leaders/researchers + pending/rejected),
        15 posts across all 5 categories and 47 reactions among related users.
        """
        from sqlalchemy import text

        from .modules.auth.models import Faculty, Program, User

        db.session.execute(
            text(
                "TRUNCATE TABLE post_reactions, post_attachments, posts, users "
                "RESTART IDENTITY CASCADE"
            )
        )
        db.session.commit()

        from .modules.posts.models import Post, PostReaction

        created_faculties = 0
        faculty_ids = {}
        program_ids = {}
        for faculty_name, program_names in SEED_FACULTIES.items():
            faculty = Faculty.query.filter_by(name=faculty_name).first()
            if faculty is None:
                faculty = Faculty(name=faculty_name)
                db.session.add(faculty)
                db.session.flush()
                created_faculties += 1
            faculty_ids[faculty_name] = faculty.id
            for program_name in program_names:
                program = Program.query.filter_by(
                    name=program_name, faculty_id=faculty.id
                ).first()
                if program is None:
                    program = Program(name=program_name, faculty_id=faculty.id)
                    db.session.add(program)
                    db.session.flush()
                program_ids[(faculty_name, program_name)] = program.id

        password = os.environ.get(SEED_USERS_PASSWORD_ENV, SEED_USERS_DEFAULT_PASSWORD)

        users_by_email = {}
        for spec in SEED_DEMO_USERS:
            user = User(
                full_name=spec["full_name"],
                email=spec["email"],
                role=spec["role"],
                status=spec["status"],
                motivation=spec["motivation"],
                faculty_id=faculty_ids[spec["faculty"]] if spec["faculty"] else None,
                program_id=(
                    program_ids[(spec["faculty"], spec["program"])]
                    if spec["program"]
                    else None
                ),
            )
            user.set_password(password)
            db.session.add(user)
            users_by_email[spec["email"]] = user
        db.session.flush()

        posts = []
        for spec in SEED_DEMO_POSTS:
            post = Post(
                author_id=users_by_email[spec["author"]].id,
                category=spec["category"],
                content=spec["content"],
                link_url=spec["link_url"],
                created_at=spec["created_at"],
            )
            db.session.add(post)
            posts.append(post)
        db.session.flush()

        reactions = 0
        for post, reactors in zip(posts, SEED_DEMO_REACTIONS):
            for email in reactors:
                db.session.add(
                    PostReaction(post_id=post.id, user_id=users_by_email[email].id)
                )
                reactions += 1

        db.session.commit()

        counts = {
            "facultades": len(SEED_FACULTIES),
            "programas": sum(len(p) for p in SEED_FACULTIES.values()),
            "usuarios": len(SEED_DEMO_USERS),
            "posts": len(SEED_DEMO_POSTS),
            "reacciones": reactions,
        }
        click.echo(
            "Seed demo completo: "
            + ", ".join(f"{k}={v}" for k, v in counts.items())
            + f" ({created_faculties} facultades nuevas)."
        )

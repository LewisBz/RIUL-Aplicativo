from app.routes.admin import admin_bp
from app.routes.auth import auth_bp
from app.routes.posts import posts_bp
from app.routes.semilleros import semilleros_bp
from app.routes.workflow import workflow_bp

__all__ = ["admin_bp", "auth_bp", "posts_bp", "semilleros_bp", "workflow_bp"]

from app.routes.admin import admin_bp
from app.routes.auth import auth_bp
from app.routes.engagement import gamification_bp, notifications_bp
from app.routes.events import events_bp
from app.routes.posts import posts_bp
from app.routes.profile import profile_bp
from app.routes.projects import projects_bp
from app.routes.semilleros import semilleros_bp
from app.routes.support import support_bp

ALL_BLUEPRINTS = (
    support_bp,
    auth_bp,
    profile_bp,
    posts_bp,
    semilleros_bp,
    projects_bp,
    events_bp,
    notifications_bp,
    gamification_bp,
    admin_bp,
)

__all__ = ["ALL_BLUEPRINTS"]

from flask import Blueprint

from app.controllers import posts_controller
from app.utils.errors import ServiceError

posts_bp = Blueprint("posts", __name__, url_prefix="/api")
posts_bp.errorhandler(ServiceError)(posts_controller.handle_service_error)
posts_bp.errorhandler(413)(posts_controller.handle_too_large)

posts_bp.get("/posts")(posts_controller.list_posts)
posts_bp.post("/posts")(posts_controller.create_post)
posts_bp.delete("/posts/<int:post_id>")(posts_controller.delete_post)
posts_bp.post("/posts/<int:post_id>/reactions")(posts_controller.toggle_reaction)
posts_bp.get("/posts/<int:post_id>/comments")(posts_controller.list_comments)
posts_bp.post("/posts/<int:post_id>/comments")(posts_controller.create_comment)
posts_bp.delete("/posts/<int:post_id>/comments/<int:comment_id>")(posts_controller.delete_comment)
posts_bp.post("/posts/<int:post_id>/shares")(posts_controller.toggle_share)
posts_bp.get("/posts/files/<path:name>")(posts_controller.serve_attachment)

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from flask_jwt_extended import get_jwt_identity, jwt_required

from . import services
from .services import ServiceError

posts_bp = Blueprint("posts", __name__, url_prefix="/api")


@posts_bp.errorhandler(ServiceError)
def handle_service_error(error):
    return jsonify(message=error.message), error.status


@posts_bp.errorhandler(413)
def handle_too_large(error):
    limit_mb = current_app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024)
    return jsonify(message=f"El archivo supera el límite de {limit_mb} MB."), 413


@posts_bp.get("/posts")
@jwt_required()
def list_posts():
    viewer_id = int(get_jwt_identity())
    category = request.args.get("category") or None
    page = request.args.get("page", default=1, type=int)
    posts, total = services.list_posts(category=category, page=page)
    return (
        jsonify(
            items=[p.to_dict(viewer_id=viewer_id) for p in posts],
            page=max(1, page),
            per_page=services.DEFAULT_PER_PAGE,
            total=total,
        ),
        200,
    )


@posts_bp.post("/posts")
@jwt_required()
def create_post():
    user_id = int(get_jwt_identity())
    data = {
        "category": request.form.get("category"),
        "content": request.form.get("content"),
        "link_url": request.form.get("link_url"),
    }
    file = request.files.get("file")
    post = services.create_post(user_id, data, file)
    return jsonify(post=post.to_dict(viewer_id=user_id)), 201


@posts_bp.delete("/posts/<int:post_id>")
@jwt_required()
def delete_post(post_id):
    user_id = int(get_jwt_identity())
    services.delete_post(user_id, post_id)
    return "", 204


@posts_bp.post("/posts/<int:post_id>/reactions")
@jwt_required()
def toggle_reaction(post_id):
    user_id = int(get_jwt_identity())
    count, reacted = services.toggle_reaction(user_id, post_id)
    return jsonify(reaction_count=count, reacted_by_me=reacted), 200


@posts_bp.get("/posts/files/<path:name>")
def serve_attachment(name):
    directory = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(directory, f"posts/{name}")

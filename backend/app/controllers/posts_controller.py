from flask import current_app, jsonify, request, send_from_directory
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.controllers.http import json_error, load_schema
from app.schemas import (
    CommentCreateSchema,
    PostCreateSchema,
    PostListQuerySchema,
    serialize_comment,
    serialize_post,
    serialize_posts,
)
from app.models import ROLE_ADMINISTRATOR
from app.repositories import user_repository
from app.services import post_service
from app.utils.errors import ServiceError


@jwt_required()
def list_posts():
    viewer_id = int(get_jwt_identity())
    query = load_schema(
        PostListQuerySchema(),
        {"category": request.args.get("category") or None, "page": request.args.get("page", 1)},
    )
    posts, total = post_service.list_posts(
        category=query.get("category"), page=query.get("page") or 1
    )
    return (
        jsonify(
            items=serialize_posts(posts, viewer_id),
            page=max(1, query.get("page") or 1),
            per_page=post_service.DEFAULT_PER_PAGE,
            total=total,
        ),
        200,
    )


@jwt_required()
def create_post():
    user_id = int(get_jwt_identity())
    data = load_schema(
        PostCreateSchema(),
        {
            "category": request.form.get("category") or "community",
            "content": request.form.get("content") or "",
            "link_url": request.form.get("link_url") or "",
        },
    )
    file = request.files.get("file")
    post = post_service.create_post(user_id, data, file)
    return jsonify(post=serialize_post(post, user_id)), 201


@jwt_required()
def delete_post(post_id: int):
    user_id = int(get_jwt_identity())
    actor = user_repository.get_user_by_id(user_id)
    is_admin = actor is not None and actor.role == ROLE_ADMINISTRATOR
    post_service.delete_post(user_id, post_id, is_admin=is_admin)
    return "", 204


@jwt_required()
def toggle_reaction(post_id: int):
    user_id = int(get_jwt_identity())
    count, reacted = post_service.toggle_reaction(user_id, post_id)
    return jsonify(reaction_count=count, reacted_by_me=reacted), 200


@jwt_required()
def list_comments(post_id: int):
    comments = post_service.list_comments(post_id)
    return jsonify(items=[serialize_comment(c) for c in comments], total=len(comments)), 200


@jwt_required()
def create_comment(post_id: int):
    user_id = int(get_jwt_identity())
    data = load_schema(CommentCreateSchema(), request.get_json(silent=True) or {})
    comment = post_service.add_comment(user_id, post_id, data["body"])
    return jsonify(comment=serialize_comment(comment)), 201


@jwt_required()
def delete_comment(post_id: int, comment_id: int):
    user_id = int(get_jwt_identity())
    actor = user_repository.get_user_by_id(user_id)
    is_admin = actor is not None and actor.role == ROLE_ADMINISTRATOR
    post_service.delete_comment(user_id, post_id, comment_id, is_admin=is_admin)
    return "", 204


@jwt_required()
def toggle_share(post_id: int):
    user_id = int(get_jwt_identity())
    count, shared = post_service.toggle_share(user_id, post_id)
    return jsonify(share_count=count, shared_by_me=shared), 200


@jwt_required(locations=["headers", "query_string"])
def serve_attachment(name: str):
    directory = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(directory, f"posts/{name}")


def handle_too_large(_error):
    limit_mb = current_app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024)
    return json_error(f"El archivo supera el límite de {limit_mb} MB.", 413)


def handle_service_error(error: ServiceError):
    return json_error(error.message, error.status)


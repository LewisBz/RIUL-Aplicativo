import time
from pathlib import Path

from flask import current_app

from app.models import (
    POST_CATEGORIES,
    Comment,
    Post,
    PostAttachment,
    PostReaction,
    PostShare,
)
from app.repositories import post_repository
from app.utils.errors import ServiceError
from app.utils.uploads import save_upload

DEFAULT_PER_PAGE = 10
MAX_COMMENT_LENGTH = 2000


def _clean(value) -> str:
    return (value or "").strip()


def _validate_category(raw) -> str:
    category = _clean(raw) or "community"
    if category not in POST_CATEGORIES:
        raise ServiceError("Categoría inválida.", 400)
    return category


def _validate_link(link_url) -> str | None:
    link = _clean(link_url) or None
    if link is not None and not link.lower().startswith(("http://", "https://")):
        raise ServiceError("El enlace debe iniciar con http:// o https://.", 400)
    return link


def _store_attachment(post: Post, file) -> None:
    post.attachments.append(PostAttachment(**save_upload(file, "posts")))


def create_post(user_id: int, data: dict, file=None) -> Post:
    category = _validate_category(data.get("category"))
    content = _clean(data.get("content")) or None
    link_url = _validate_link(data.get("link_url"))
    has_file = file is not None and getattr(file, "filename", "")

    if content is None and link_url is None and not has_file:
        raise ServiceError(
            "La publicación requiere texto, enlace o archivo adjunto.", 400
        )

    post = Post(author_id=user_id, category=category, content=content, link_url=link_url)
    post_repository.add_post(post)
    post_repository.flush()

    if has_file:
        _store_attachment(post, file)

    post_repository.commit()
    return post


def list_posts(
    category: str | None = None, page: int = 1, per_page: int = DEFAULT_PER_PAGE
) -> tuple[list[Post], int]:
    page = max(1, page)
    per_page = max(1, min(per_page, 50))
    filters = []
    if category is not None:
        if category not in POST_CATEGORIES:
            raise ServiceError("Categoría inválida.", 400)
        filters.append(Post.category == category)
    return post_repository.list_posts(filters, page, per_page)


def get_post_or_404(post_id: int) -> Post:
    post = post_repository.get_post(post_id)
    if post is None:
        raise ServiceError("Publicación no encontrada.", 404)
    return post


def _remove_file(path: Path) -> None:
    for attempt in range(12):
        try:
            path.unlink(missing_ok=True)
            return
        except OSError:
            if attempt == 11:
                return
            time.sleep(0.3)


def delete_post(user_id: int, post_id: int, is_admin: bool = False) -> None:
    post = get_post_or_404(post_id)
    if post.author_id != user_id and not is_admin:
        raise ServiceError("Solo el autor puede eliminar esta publicación.", 403)
    if post_repository.post_has_achievements(post.id):
        raise ServiceError(
            "La publicación respalda un logro y no puede eliminarse.", 409
        )
    storage_names = [a.storage_name for a in post.attachments]
    post_repository.delete_post(post)
    post_repository.commit()
    for name in storage_names:
        _remove_file(Path(current_app.config["UPLOAD_FOLDER"]) / "posts" / name)


def toggle_reaction(user_id: int, post_id: int) -> tuple[int, bool]:
    post = get_post_or_404(post_id)
    existing = post_repository.get_reaction(post_id, user_id)
    if existing is None:
        post_repository.add_reaction(PostReaction(post_id=post.id, user_id=user_id))
        reacted = True
    else:
        post_repository.delete_reaction(existing)
        reacted = False
    post_repository.commit()
    return post_repository.count_reactions(post_id), reacted


# --- Comentarios ---
def list_comments(post_id: int) -> list[Comment]:
    get_post_or_404(post_id)
    return post_repository.list_comments(post_id)


def add_comment(user_id: int, post_id: int, body: str) -> Comment:
    post = get_post_or_404(post_id)
    text = _clean(body)
    if not text:
        raise ServiceError("El comentario no puede estar vacío.", 400)
    if len(text) > MAX_COMMENT_LENGTH:
        raise ServiceError(
            f"El comentario no puede superar {MAX_COMMENT_LENGTH} caracteres.", 400
        )
    comment = post_repository.add_comment(Comment(post_id=post.id, user_id=user_id, body=text))
    post_repository.commit()
    return comment


def delete_comment(user_id: int, post_id: int, comment_id: int, is_admin: bool = False) -> None:
    get_post_or_404(post_id)
    comment = post_repository.get_comment(post_id, comment_id)
    if comment is None:
        raise ServiceError("Comentario no encontrado.", 404)
    if comment.user_id != user_id and not is_admin:
        raise ServiceError("Solo el autor puede eliminar este comentario.", 403)
    post_repository.delete_comment(comment)
    post_repository.commit()


# --- Compartidos ---
def toggle_share(user_id: int, post_id: int) -> tuple[int, bool]:
    post = get_post_or_404(post_id)
    existing = post_repository.get_share(post_id, user_id)
    if existing is None:
        post_repository.add_share(PostShare(post_id=post.id, user_id=user_id))
        shared = True
    else:
        post_repository.delete_share(existing)
        shared = False
    post_repository.commit()
    return post_repository.count_shares(post_id), shared

import time
import uuid
from pathlib import Path

from flask import current_app
from sqlalchemy import func, select
from werkzeug.utils import secure_filename

from app.extensions import db
from app.modules.posts.models import (
    KIND_FILE,
    KIND_IMAGE,
    POST_CATEGORIES,
    Post,
    PostAttachment,
    PostReaction,
)

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB (also enforced by MAX_CONTENT_LENGTH)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
ALLOWED_FILE_EXTENSIONS = {"pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx"}

DEFAULT_PER_PAGE = 10


class ServiceError(Exception):
    def __init__(self, message: str, status: int):
        super().__init__(message)
        self.message = message
        self.status = status


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


def _attachment_kind(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext in ALLOWED_IMAGE_EXTENSIONS:
        return KIND_IMAGE
    if ext in ALLOWED_FILE_EXTENSIONS:
        return KIND_FILE
    raise ServiceError(
        "Tipo de archivo no permitido. Imágenes: png, jpg, jpeg, webp, gif. "
        "Documentos: pdf, doc, docx, ppt, pptx, xls, xlsx.",
        400,
    )


def _uploads_dir() -> Path:
    directory = Path(current_app.config["UPLOAD_FOLDER"]) / "posts"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _store_attachment(post: Post, file) -> None:
    original = secure_filename(file.filename or "")
    if not original or "." not in original:
        raise ServiceError("Adjunto inválido o sin extensión.", 400)
    kind = _attachment_kind(original)
    ext = original.rsplit(".", 1)[-1].lower()
    storage_name = f"{uuid.uuid4().hex}.{ext}"
    target = _uploads_dir() / storage_name
    file.save(target)
    attachment = PostAttachment(
        post_id=post.id,
        kind=kind,
        file_name=original,
        storage_name=storage_name,
        mime_type=getattr(file, "mimetype", None),
        file_size=target.stat().st_size,
    )
    db.session.add(attachment)


def create_post(user_id: int, data: dict, file=None) -> Post:
    category = _validate_category(data.get("category"))
    content = _clean(data.get("content")) or None
    link_url = _validate_link(data.get("link_url"))

    if content is None and link_url is None and file is None:
        raise ServiceError(
            "La publicación requiere texto, enlace o archivo adjunto.", 400
        )

    post = Post(author_id=user_id, category=category, content=content, link_url=link_url)
    db.session.add(post)
    db.session.flush()

    if file is not None and getattr(file, "filename", ""):
        _store_attachment(post, file)

    db.session.commit()
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

    total = db.session.scalar(
        select(func.count()).select_from(Post).where(*filters)
    )
    stmt = (
        select(Post)
        .where(*filters)
        .order_by(Post.created_at.desc(), Post.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    posts = list(db.session.scalars(stmt).all())
    return posts, int(total or 0)


def get_post_or_404(post_id: int) -> Post:
    post = db.session.get(Post, post_id)
    if post is None:
        raise ServiceError("Publicación no encontrada.", 404)
    return post


def _remove_file(path: Path) -> None:
    # Windows puede mantener locks transitorios (antivirus/indexer): reintentar.
    for attempt in range(12):
        try:
            path.unlink(missing_ok=True)
            return
        except OSError:
            if attempt == 11:
                return
            time.sleep(0.3)


def delete_post(user_id: int, post_id: int) -> None:
    post = get_post_or_404(post_id)
    if post.author_id != user_id:
        raise ServiceError("Solo el autor puede eliminar esta publicación.", 403)
    storage_names = [a.storage_name for a in post.attachments]
    db.session.delete(post)
    db.session.commit()
    for name in storage_names:
        _remove_file(Path(current_app.config["UPLOAD_FOLDER"]) / "posts" / name)


def toggle_reaction(user_id: int, post_id: int) -> tuple[int, bool]:
    post = get_post_or_404(post_id)
    existing = db.session.scalar(
        select(PostReaction).where(
            PostReaction.post_id == post_id, PostReaction.user_id == user_id
        )
    )
    if existing is None:
        db.session.add(PostReaction(post_id=post.id, user_id=user_id))
        reacted = True
    else:
        db.session.delete(existing)
        reacted = False
    db.session.commit()
    count = db.session.scalar(
        select(func.count()).select_from(PostReaction).where(PostReaction.post_id == post_id)
    )
    return int(count or 0), reacted

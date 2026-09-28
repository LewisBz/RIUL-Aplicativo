import time
import uuid
from pathlib import Path

from flask import current_app
from werkzeug.utils import secure_filename

from app.models import KIND_FILE, KIND_IMAGE, POST_CATEGORIES, Post, PostAttachment, PostReaction
from app.repositories import post_repository
from app.utils.errors import ServiceError

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
ALLOWED_FILE_EXTENSIONS = {"pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx"}
DEFAULT_PER_PAGE = 10


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
    post.attachments.append(
        PostAttachment(
            kind=kind,
            file_name=original,
            storage_name=storage_name,
            mime_type=getattr(file, "mimetype", None),
            file_size=target.stat().st_size,
        )
    )


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


def delete_post(user_id: int, post_id: int) -> None:
    post = get_post_or_404(post_id)
    if post.author_id != user_id:
        raise ServiceError("Solo el autor puede eliminar esta publicación.", 403)
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

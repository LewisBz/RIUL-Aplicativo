import uuid
from pathlib import Path

from flask import current_app
from werkzeug.utils import secure_filename

from app.utils.errors import ServiceError

KIND_IMAGE = "image"
KIND_FILE = "file"

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
ALLOWED_FILE_EXTENSIONS = {"pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx"}


def uploads_dir(subdir: str) -> Path:
    directory = Path(current_app.config["UPLOAD_FOLDER"]) / subdir
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def attachment_kind(filename: str) -> str:
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


def save_upload(file, subdir: str) -> dict:
    """Guarda un archivo subido y devuelve sus metadatos para persistirlos."""
    original = secure_filename(file.filename or "")
    if not original or "." not in original:
        raise ServiceError("Adjunto inválido o sin extensión.", 400)
    kind = attachment_kind(original)
    ext = original.rsplit(".", 1)[-1].lower()
    storage_name = f"{uuid.uuid4().hex}.{ext}"
    target = uploads_dir(subdir) / storage_name
    file.save(target)
    return {
        "kind": kind,
        "file_name": original,
        "storage_name": storage_name,
        "mime_type": getattr(file, "mimetype", None),
        "file_size": target.stat().st_size,
    }

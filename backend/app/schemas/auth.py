from marshmallow import Schema, fields, validate

from app.models import POST_CATEGORIES


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    full_name = fields.Str(allow_none=True)
    email = fields.Email(required=True)
    role = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    faculty_id = fields.Int(allow_none=True)
    program_id = fields.Int(allow_none=True)


class RegisterSchema(Schema):
    email = fields.Email(required=True, error_messages={"required": "Correo electrónico inválido.", "invalid": "Correo electrónico inválido."})
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8, error="La contraseña debe tener al menos 8 caracteres."),
    )
    full_name = fields.Str(load_default="")
    faculty_id = fields.Int(load_default=None, allow_none=True)
    program_id = fields.Int(load_default=None, allow_none=True)


class LoginSchema(Schema):
    email = fields.Email(required=True, error_messages={"required": "Correo electrónico inválido.", "invalid": "Correo electrónico inválido."})
    password = fields.Str(required=True)


class RequestAccountSchema(Schema):
    email = fields.Email(required=True, error_messages={"required": "Correo electrónico inválido.", "invalid": "Correo electrónico inválido."})
    full_name = fields.Str(required=True)
    motivation = fields.Str(required=True)
    faculty_id = fields.Int(required=True)
    program_id = fields.Int(required=True)


class ProgramSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    faculty_id = fields.Int()


class FacultyCatalogSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    programs = fields.Nested(ProgramSchema, many=True)


class TokenUserSchema(Schema):
    access_token = fields.Str()
    user = fields.Nested(UserSchema)


class AuthorSchema(Schema):
    id = fields.Int()
    full_name = fields.Str(allow_none=True)


class AttachmentSchema(Schema):
    id = fields.Int()
    kind = fields.Str()
    file_name = fields.Str()
    mime_type = fields.Str(allow_none=True)
    file_size = fields.Int(allow_none=True)
    url = fields.Method("dump_url")

    def dump_url(self, obj):
        return f"/api/posts/files/{obj.storage_name}"


class PostSchema(Schema):
    id = fields.Int()
    category = fields.Str()
    content = fields.Str(allow_none=True)
    link_url = fields.Str(allow_none=True)
    created_at = fields.Method("dump_created_at")
    author = fields.Nested(AuthorSchema)
    attachments = fields.Nested(AttachmentSchema, many=True)
    reaction_count = fields.Method("dump_reaction_count")
    reacted_by_me = fields.Bool(dump_only=True, dump_default=False)
    comment_count = fields.Method("dump_comment_count")
    share_count = fields.Method("dump_share_count")
    shared_by_me = fields.Bool(dump_only=True, dump_default=False)

    def dump_created_at(self, obj):
        return obj.created_at.isoformat() if obj.created_at else None

    def dump_reaction_count(self, obj):
        return len(obj.reactions)

    def dump_comment_count(self, obj):
        return len(obj.comments)

    def dump_share_count(self, obj):
        return len(obj.shares)


def serialize_post(post, viewer_id: int | None = None) -> dict:
    payload = PostSchema().dump(post)
    payload["reacted_by_me"] = viewer_id is not None and any(
        r.user_id == viewer_id for r in post.reactions
    )
    payload["shared_by_me"] = viewer_id is not None and any(
        s.user_id == viewer_id for s in post.shares
    )
    return payload


class CommentCreateSchema(Schema):
    body = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=2000, error="El comentario debe tener entre 1 y 2000 caracteres."),
        error_messages={"required": "El comentario no puede estar vacío."},
    )


def serialize_comment(comment) -> dict:
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "body": comment.body,
        "created_at": comment.created_at.isoformat() if comment.created_at else None,
        "author": {"id": comment.user.id, "full_name": comment.user.full_name},
    }


def serialize_posts(posts, viewer_id: int | None = None) -> list[dict]:
    return [serialize_post(post, viewer_id) for post in posts]


class PostCreateSchema(Schema):
    category = fields.Str(
        load_default="community",
        validate=validate.OneOf(POST_CATEGORIES, error="Categoría inválida."),
    )
    content = fields.Str(load_default="")
    link_url = fields.Str(load_default="")


class PostListQuerySchema(Schema):
    category = fields.Str(load_default=None, allow_none=True)
    page = fields.Int(load_default=1)


class UserStatusSchema(Schema):
    status = fields.Str(required=True)


class AdminUsersQuerySchema(Schema):
    status = fields.Str(load_default=None, allow_none=True)
    role = fields.Str(load_default=None, allow_none=True)
    q = fields.Str(load_default=None, allow_none=True)

from marshmallow import Schema, fields, validate

from app.models import PROJECT_STATUSES, PUBLICATION_STATUSES


def iso(value):
    return value.isoformat() if value else None


class ProjectCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=3, max=200, error="El título debe tener entre 3 y 200 caracteres."))
    type = fields.Str(load_default="")
    status = fields.Str(load_default="planned", validate=validate.OneOf(PROJECT_STATUSES, error="Estado de proyecto inválido."))
    description = fields.Str(load_default="")
    line = fields.Str(load_default="")
    role_required = fields.Str(load_default="")
    semillero = fields.Str(load_default=None, allow_none=True)
    start_date = fields.Date(load_default=None, allow_none=True)
    end_date = fields.Date(load_default=None, allow_none=True)
    milestones = fields.List(fields.Str(validate=validate.Length(min=1, max=200)), load_default=list)


class ProjectUpdateSchema(Schema):
    status = fields.Str(validate=validate.OneOf(PROJECT_STATUSES, error="Estado de proyecto inválido."))
    progress = fields.Int(validate=validate.Range(min=0, max=100, error="El avance debe estar entre 0 y 100."))
    description = fields.Str()
    line = fields.Str()
    end_date = fields.Date(allow_none=True)


class ProjectListQuerySchema(Schema):
    q = fields.Str(load_default=None, allow_none=True)
    status = fields.Str(load_default=None, allow_none=True)
    semillero = fields.Str(load_default=None, allow_none=True)
    mine = fields.Bool(load_default=False)


class ProjectProductSchema(Schema):
    type = fields.Str(required=True)
    name = fields.Str(required=True)


class MilestoneUpdateSchema(Schema):
    done = fields.Bool(required=True)


class PublicationCreateSchema(Schema):
    title = fields.Str(required=True)
    venue = fields.Str(load_default="")
    published_on = fields.Date(load_default=None, allow_none=True)
    status = fields.Str(load_default="in_review", validate=validate.OneOf(PUBLICATION_STATUSES, error="Estado de publicación inválido."))
    semillero = fields.Str(load_default=None, allow_none=True)


def serialize_publication(p) -> dict:
    return {
        "id": p.id,
        "title": p.title,
        "venue": p.venue,
        "published_on": iso(p.published_on),
        "status": p.status,
        "semillero": p.semillero.slug if p.semillero else None,
    }


def serialize_product(product) -> dict:
    return {"id": product.id, "type": product.type, "name": product.name, "status": product.status}


def serialize_project_summary(project, viewer_role: str | None = None) -> dict:
    semillero = project.semillero
    return {
        "id": project.id,
        "slug": project.slug,
        "title": project.title,
        "type": project.type,
        "status": project.status,
        "description": project.description,
        "progress": project.progress,
        "line": project.line,
        "role_required": project.role_required,
        "start_date": iso(project.start_date),
        "end_date": iso(project.end_date),
        "faculty": semillero.faculty.name if semillero and semillero.faculty else None,
        "semillero": {"slug": semillero.slug, "name": semillero.name} if semillero else None,
        "leader": {"id": project.leader.id, "full_name": project.leader.full_name},
        "my_role": viewer_role,
    }


def serialize_project_detail(project, viewer_role: str | None = None) -> dict:
    payload = serialize_project_summary(project, viewer_role)
    payload["members"] = [
        {"id": m.user.id, "full_name": m.user.full_name} for m in project.members
    ]
    payload["products"] = [serialize_product(p) for p in project.products]
    payload["milestones"] = [
        {"id": m.id, "text": m.text, "done": m.done} for m in project.milestones
    ]
    return payload

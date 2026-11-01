from marshmallow import Schema, fields, validate

from app.schemas.projects import (
    iso,
    serialize_project_summary,
    serialize_publication,
)


class ResearchLineInputSchema(Schema):
    name = fields.Str(required=True)
    icon = fields.Str(load_default="science")
    coordinator = fields.Str(load_default=None, allow_none=True)


class SemilleroCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3, max=160, error="El nombre debe tener entre 3 y 160 caracteres."))
    area = fields.Str(load_default="")
    description = fields.Str(load_default="")
    icon = fields.Str(load_default="science")
    faculty_id = fields.Int(load_default=None, allow_none=True)
    program_id = fields.Int(load_default=None, allow_none=True)
    about = fields.Str(load_default="")
    mission = fields.Str(load_default="")
    vision = fields.Str(load_default="")
    interest_areas = fields.List(fields.Str(), load_default=list)
    lines = fields.List(fields.Nested(ResearchLineInputSchema), load_default=list)


class SemilleroActivitySchema(Schema):
    title = fields.Str(required=True)
    place = fields.Str(load_default="")
    occurred_on = fields.Date(required=True)


class SemilleroListQuerySchema(Schema):
    q = fields.Str(load_default=None, allow_none=True)
    faculty_id = fields.Int(load_default=None, allow_none=True)
    area = fields.Str(load_default=None, allow_none=True)


def _initials(name: str | None) -> str:
    parts = (name or "?").split()
    return "".join(p[0] for p in parts[:2]).upper() or "?"


def serialize_semillero_summary(s, my_role: str | None = None) -> dict:
    return {
        "id": s.id,
        "slug": s.slug,
        "name": s.name,
        "area": s.area,
        "description": s.description,
        "icon": s.icon,
        "top_badge": s.top_badge,
        "faculty": {"id": s.faculty.id, "name": s.faculty.name} if s.faculty else None,
        "program": {"id": s.program.id, "name": s.program.name} if s.program else None,
        "leader": {"id": s.leader_id, "full_name": s.leader_name},
        "member_count": len(s.members) + (1 if s.leader_id else 0),
        "my_role": my_role,
    }


def serialize_semillero_detail(s, my_role, projects, publications) -> dict:
    payload = serialize_semillero_summary(s, my_role)
    payload["leader"]["title"] = s.leader_title
    payload.update(
        affiliation=s.affiliation,
        about=s.about,
        mission=s.mission,
        vision=s.vision,
        interest_areas=s.interest_areas or [],
        members=[
            {
                "id": m.user.id,
                "full_name": m.user.full_name,
                "initials": _initials(m.user.full_name),
                "role": m.role,
            }
            for m in s.members
        ],
        lines=[
            {"id": line.id, "name": line.name, "icon": line.icon, "coordinator": line.coordinator}
            for line in s.lines
        ],
        projects=[serialize_project_summary(p) for p in projects],
        publications=[serialize_publication(p) for p in publications],
        activities=[
            {"id": a.id, "title": a.title, "place": a.place, "occurred_on": iso(a.occurred_on)}
            for a in s.activities
        ],
    )
    return payload

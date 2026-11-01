from marshmallow import Schema, fields, validate

from app.models import (
    MEMBERSHIP_ACTIVE,
    MEMBERSHIP_REJECTED,
    SEMILLERO_ROLE_CO_LEADER,
    SEMILLERO_ROLE_LEADER,
    SEMILLERO_ROLE_MEMBER,
)
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


class MemberReviewSchema(Schema):
    """Resolución de una solicitud de vinculación por el líder."""

    status = fields.Str(
        required=True,
        validate=validate.OneOf(
            [MEMBERSHIP_ACTIVE, MEMBERSHIP_REJECTED], error="Estado de vinculación inválido."
        ),
    )
    role = fields.Str(
        load_default=None,
        allow_none=True,
        validate=validate.OneOf(
            [SEMILLERO_ROLE_MEMBER, SEMILLERO_ROLE_CO_LEADER], error="Rol de vinculación inválido."
        ),
    )


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
        "leader": {"id": s.leader_id, "full_name": s.leader.full_name if s.leader else None},
        "member_count": len(s.active_members),
        "my_role": my_role,
    }


def serialize_semillero_detail(
    s,
    membership: dict,
    projects,
    publications,
    *,
    can_manage: bool = False,
    following: bool = False,
    follower_count: int = 0,
) -> dict:
    payload = serialize_semillero_summary(s, membership["role"])
    payload["leader"]["title"] = s.leader_title
    progress = s.progress
    payload.update(
        my_status=membership["status"],
        following=following,
        follower_count=follower_count,
        progress={
            "xp": progress.xp if progress else 0,
            "level": progress.level.level_number if progress else 1,
        },
        affiliation=s.affiliation,
        about=s.about,
        mission=s.mission,
        vision=s.vision,
        interest_areas=s.interest_areas or [],
        # El líder se muestra aparte; aquí van los demás integrantes activos.
        members=[
            {
                "id": m.user.id,
                "full_name": m.user.full_name,
                "initials": _initials(m.user.full_name),
                "role": m.role,
            }
            for m in s.active_members
            if m.role != SEMILLERO_ROLE_LEADER
        ],
        pending_members=(
            [
                {
                    "id": m.user.id,
                    "full_name": m.user.full_name,
                    "initials": _initials(m.user.full_name),
                    "requested_at": iso(m.joined_at),
                }
                for m in s.pending_members
            ]
            if can_manage
            else []
        ),
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

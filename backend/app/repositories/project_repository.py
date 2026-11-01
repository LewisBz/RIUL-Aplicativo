from sqlalchemy import func, or_, select

from app.extensions import db
from app.models import (
    Project,
    ProjectMember,
    ProjectMilestone,
    ProjectProduct,
    Publication,
    Semillero,
)


def slug_exists(slug: str) -> bool:
    return db.session.scalar(select(Project.id).where(Project.slug == slug)) is not None


def get_by_slug(slug: str) -> Project | None:
    return db.session.scalar(select(Project).where(Project.slug == slug))


def list_projects(
    q: str | None = None,
    status: str | None = None,
    semillero_id: int | None = None,
    member_id: int | None = None,
) -> list[Project]:
    stmt = select(Project).order_by(Project.created_at.desc(), Project.id.desc())
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(Project.title.like(like), Project.description.like(like), Project.line.like(like))
        )
    if status:
        stmt = stmt.where(Project.status == status)
    if semillero_id:
        stmt = stmt.where(Project.semillero_id == semillero_id)
    if member_id:
        stmt = stmt.where(
            Project.id.in_(
                select(ProjectMember.project_id).where(ProjectMember.user_id == member_id)
            )
        )
    return list(db.session.scalars(stmt).all())


def add(project: Project) -> Project:
    db.session.add(project)
    return project


def add_product(product: ProjectProduct) -> ProjectProduct:
    db.session.add(product)
    return product


def get_milestone(project_id: int, milestone_id: int) -> ProjectMilestone | None:
    return db.session.scalar(
        select(ProjectMilestone).where(
            ProjectMilestone.project_id == project_id,
            ProjectMilestone.id == milestone_id,
        )
    )


def get_member(project_id: int, user_id: int) -> ProjectMember | None:
    return db.session.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
        )
    )


def count_projects() -> int:
    return int(db.session.scalar(select(func.count()).select_from(Project)) or 0)


def add_publication(publication: Publication) -> Publication:
    db.session.add(publication)
    return publication


def list_publications(author_id: int, limit: int | None = None) -> list[Publication]:
    stmt = (
        select(Publication)
        .where(Publication.author_id == author_id)
        .order_by(Publication.published_on.desc(), Publication.id.desc())
    )
    if limit:
        stmt = stmt.limit(limit)
    return list(db.session.scalars(stmt).all())


def get_semillero(semillero_id: int) -> Semillero | None:
    return db.session.get(Semillero, semillero_id)


def commit() -> None:
    db.session.commit()


def flush() -> None:
    db.session.flush()


def list_semillero_publications(semillero_id: int) -> list[Publication]:
    stmt = (
        select(Publication)
        .where(Publication.semillero_id == semillero_id)
        .order_by(Publication.published_on.desc(), Publication.id.desc())
    )
    return list(db.session.scalars(stmt).all())

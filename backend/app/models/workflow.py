from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class SemilleroFollow(db.Model):
    __tablename__ = "semillero_follows"
    __table_args__ = (UniqueConstraint("semillero_id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    semillero_id: Mapped[int] = mapped_column(ForeignKey("semilleros.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Comment(db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    author: Mapped["User"] = relationship()


class Project(db.Model):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(80), nullable=False, default="Investigación")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="En curso")
    description: Mapped[str | None] = mapped_column(Text)
    faculty: Mapped[str | None] = mapped_column(String(120))
    seedbed: Mapped[str | None] = mapped_column(String(160))
    leader_name: Mapped[str | None] = mapped_column(String(160))
    leader_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    progress: Mapped[int] = mapped_column(nullable=False, default=0)
    line: Mapped[str | None] = mapped_column(String(120))
    start_date: Mapped[str | None] = mapped_column(String(20))
    end_date: Mapped[str | None] = mapped_column(String(20))

    members: Mapped[list["ProjectMember"]] = relationship(cascade="all, delete-orphan")
    milestones: Mapped[list["ProjectMilestone"]] = relationship(cascade="all, delete-orphan")


class ProjectMember(db.Model):
    __tablename__ = "project_members"
    __table_args__ = (UniqueConstraint("project_id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(160), nullable=False)


class ProjectMilestone(db.Model):
    __tablename__ = "project_milestones"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    text: Mapped[str] = mapped_column(String(255), nullable=False)
    done: Mapped[bool] = mapped_column(nullable=False, default=False)


class Event(db.Model):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(40), nullable=False, default="Evento")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Abierto")
    location: Mapped[str | None] = mapped_column(String(160))
    capacity: Mapped[int | None] = mapped_column()
    organizer: Mapped[str | None] = mapped_column(String(160))
    starts_at: Mapped[datetime] = mapped_column(nullable=False)
    ends_at: Mapped[datetime | None] = mapped_column()
    semillero_id: Mapped[int | None] = mapped_column(ForeignKey("semilleros.id"))

    participations: Mapped[list["EventParticipation"]] = relationship(
        cascade="all, delete-orphan"
    )


class EventParticipation(db.Model):
    __tablename__ = "event_participations"
    __table_args__ = (UniqueConstraint("event_id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="registered")


class Call(db.Model):
    __tablename__ = "calls"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Abierta")
    location: Mapped[str | None] = mapped_column(String(160))
    organizer: Mapped[str | None] = mapped_column(String(160))
    starts_at: Mapped[datetime] = mapped_column(nullable=False)
    ends_at: Mapped[datetime | None] = mapped_column()
    published_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    applications: Mapped[list["CallApplication"]] = relationship(
        cascade="all, delete-orphan"
    )


class CallApplication(db.Model):
    __tablename__ = "call_applications"
    __table_args__ = (UniqueConstraint("call_id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    call_id: Mapped[int] = mapped_column(ForeignKey("calls.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")


class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    bio: Mapped[str | None] = mapped_column(Text)
    photo_url: Mapped[str | None] = mapped_column(String(500))


class Badge(db.Model):
    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    icon: Mapped[str] = mapped_column(String(40), nullable=False, default="military_tech")


class Achievement(db.Model):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    kind: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    xp_amount: Mapped[int] = mapped_column(nullable=False, default=20)
    evidence: Mapped[str | None] = mapped_column(String(500))
    source_kind: Mapped[str | None] = mapped_column(String(30))
    source_id: Mapped[int | None] = mapped_column()
    validated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship(foreign_keys=[user_id])


class UserProgress(db.Model):
    __tablename__ = "user_progress"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    xp: Mapped[int] = mapped_column(nullable=False, default=0)
    level: Mapped[int] = mapped_column(nullable=False, default=1)
    stars: Mapped[int] = mapped_column(nullable=False, default=1)


class UserBadge(db.Model):
    __tablename__ = "user_badges"
    __table_args__ = (UniqueConstraint("user_id", "badge_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    badge_id: Mapped[int] = mapped_column(ForeignKey("badges.id"), nullable=False)
    achievement_id: Mapped[int | None] = mapped_column(ForeignKey("achievements.id"))
    granted_at: Mapped[datetime] = mapped_column(server_default=func.now())

    badge: Mapped["Badge"] = relationship()


class Notification(db.Model):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    href: Mapped[str | None] = mapped_column(String(200))
    read_at: Mapped[datetime | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


from app.models.user import User  # noqa: E402

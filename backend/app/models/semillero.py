from datetime import date, datetime

from sqlalchemy import JSON, Date, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.user import User

SEMILLERO_ROLE_LEADER = "leader"
SEMILLERO_ROLE_CO_LEADER = "co_leader"
SEMILLERO_ROLE_MEMBER = "member"
SEMILLERO_ROLES = (SEMILLERO_ROLE_LEADER, SEMILLERO_ROLE_CO_LEADER, SEMILLERO_ROLE_MEMBER)

MEMBERSHIP_PENDING = "pending"
MEMBERSHIP_ACTIVE = "active"
MEMBERSHIP_REJECTED = "rejected"
MEMBERSHIP_STATUSES = (MEMBERSHIP_PENDING, MEMBERSHIP_ACTIVE, MEMBERSHIP_REJECTED)


class Semillero(db.Model):
    __tablename__ = "semilleros"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    area: Mapped[str | None] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text)
    icon: Mapped[str] = mapped_column(String(40), default="science", server_default="science")
    top_badge: Mapped[str | None] = mapped_column(String(40))
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculties.id"), nullable=False)
    program_id: Mapped[int | None] = mapped_column(ForeignKey("programs.id"))
    leader_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    leader_title: Mapped[str | None] = mapped_column(String(160))
    affiliation: Mapped[str | None] = mapped_column(String(255))
    about: Mapped[str | None] = mapped_column(Text)
    mission: Mapped[str | None] = mapped_column(Text)
    vision: Mapped[str | None] = mapped_column(Text)
    interest_areas: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    faculty = relationship("Faculty")
    program = relationship("Program")
    leader: Mapped["User"] = relationship()
    members: Mapped[list["SemilleroMember"]] = relationship(
        back_populates="semillero",
        cascade="all, delete-orphan",
        order_by="SemilleroMember.id",
    )
    lines: Mapped[list["ResearchLine"]] = relationship(
        back_populates="semillero", cascade="all, delete-orphan"
    )
    activities: Mapped[list["SemilleroActivity"]] = relationship(
        back_populates="semillero",
        cascade="all, delete-orphan",
        order_by="SemilleroActivity.occurred_on.desc()",
    )
    follows: Mapped[list["SemilleroFollow"]] = relationship(
        back_populates="semillero", cascade="all, delete-orphan"
    )
    progress: Mapped["SemilleroProgress | None"] = relationship(
        back_populates="semillero", cascade="all, delete-orphan", uselist=False
    )

    @property
    def active_members(self) -> list["SemilleroMember"]:
        return [m for m in self.members if m.status == MEMBERSHIP_ACTIVE]

    @property
    def pending_members(self) -> list["SemilleroMember"]:
        return [m for m in self.members if m.status == MEMBERSHIP_PENDING]


class SemilleroMember(db.Model):
    """Vínculo usuario-semillero. El líder figura con rol `leader`."""

    __tablename__ = "semillero_members"
    __table_args__ = (
        UniqueConstraint("semillero_id", "user_id"),
        db.CheckConstraint(
            "role IN ('leader','co_leader','member')", name="ck_semillero_members_role"
        ),
        db.CheckConstraint(
            "status IN ('pending','active','rejected')", name="ck_semillero_members_status"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    semillero_id: Mapped[int] = mapped_column(ForeignKey("semilleros.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default=SEMILLERO_ROLE_MEMBER, server_default=SEMILLERO_ROLE_MEMBER
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=MEMBERSHIP_PENDING, server_default=MEMBERSHIP_PENDING
    )
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    joined_at: Mapped[datetime] = mapped_column(server_default=func.now())

    semillero: Mapped["Semillero"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    approver: Mapped["User | None"] = relationship(foreign_keys=[approved_by])


class ResearchLine(db.Model):
    __tablename__ = "semillero_research_lines"

    id: Mapped[int] = mapped_column(primary_key=True)
    semillero_id: Mapped[int] = mapped_column(ForeignKey("semilleros.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    icon: Mapped[str] = mapped_column(String(40), default="science", server_default="science")
    coordinator: Mapped[str | None] = mapped_column(String(160))

    semillero: Mapped["Semillero"] = relationship(back_populates="lines")


class SemilleroFollow(db.Model):
    """Seguimiento de un semillero por un usuario (único por par)."""

    __tablename__ = "semillero_follows"
    __table_args__ = (UniqueConstraint("semillero_id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    semillero_id: Mapped[int] = mapped_column(ForeignKey("semilleros.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    semillero: Mapped["Semillero"] = relationship(back_populates="follows")
    user: Mapped["User"] = relationship()


class SemilleroProgress(db.Model):
    """XP acumulado del semillero (logros aprobados) y su nivel vigente."""

    __tablename__ = "semillero_progress"

    id: Mapped[int] = mapped_column(primary_key=True)
    semillero_id: Mapped[int] = mapped_column(
        ForeignKey("semilleros.id"), nullable=False, unique=True
    )
    level_id: Mapped[int] = mapped_column(ForeignKey("levels.id"), nullable=False)
    xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    semillero: Mapped["Semillero"] = relationship(back_populates="progress")
    level = relationship("Level")


class SemilleroActivity(db.Model):
    __tablename__ = "semillero_activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    semillero_id: Mapped[int] = mapped_column(ForeignKey("semilleros.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    place: Mapped[str | None] = mapped_column(String(200))
    occurred_on: Mapped[date] = mapped_column(Date, nullable=False)

    semillero: Mapped["Semillero"] = relationship(back_populates="activities")

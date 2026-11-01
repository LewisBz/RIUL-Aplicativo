from datetime import date, datetime

from sqlalchemy import JSON, Date, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.user import User

SEMILLERO_ROLE_MEMBER = "member"
SEMILLERO_ROLE_CO_LEADER = "co_leader"
SEMILLERO_ROLES = (SEMILLERO_ROLE_MEMBER, SEMILLERO_ROLE_CO_LEADER)


class Semillero(db.Model):
    __tablename__ = "semilleros"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    area: Mapped[str | None] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text)
    icon: Mapped[str] = mapped_column(String(40), default="science", server_default="science")
    top_badge: Mapped[str | None] = mapped_column(String(40))
    faculty_id: Mapped[int | None] = mapped_column(ForeignKey("faculties.id"))
    program_id: Mapped[int | None] = mapped_column(ForeignKey("programs.id"))
    leader_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    leader_name: Mapped[str | None] = mapped_column(String(160))
    leader_title: Mapped[str | None] = mapped_column(String(160))
    affiliation: Mapped[str | None] = mapped_column(String(255))
    about: Mapped[str | None] = mapped_column(Text)
    mission: Mapped[str | None] = mapped_column(Text)
    vision: Mapped[str | None] = mapped_column(Text)
    interest_areas: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    faculty = relationship("Faculty")
    program = relationship("Program")
    leader: Mapped["User | None"] = relationship()
    members: Mapped[list["SemilleroMember"]] = relationship(
        back_populates="semillero", cascade="all, delete-orphan"
    )
    lines: Mapped[list["ResearchLine"]] = relationship(
        back_populates="semillero", cascade="all, delete-orphan"
    )
    activities: Mapped[list["SemilleroActivity"]] = relationship(
        back_populates="semillero",
        cascade="all, delete-orphan",
        order_by="SemilleroActivity.occurred_on.desc()",
    )


class SemilleroMember(db.Model):
    __tablename__ = "semillero_members"
    __table_args__ = (UniqueConstraint("semillero_id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    semillero_id: Mapped[int] = mapped_column(ForeignKey("semilleros.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), default=SEMILLERO_ROLE_MEMBER, server_default=SEMILLERO_ROLE_MEMBER
    )
    joined_at: Mapped[datetime] = mapped_column(server_default=func.now())

    semillero: Mapped["Semillero"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship()


class ResearchLine(db.Model):
    __tablename__ = "research_lines"

    id: Mapped[int] = mapped_column(primary_key=True)
    semillero_id: Mapped[int] = mapped_column(ForeignKey("semilleros.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    icon: Mapped[str] = mapped_column(String(40), default="science", server_default="science")
    coordinator: Mapped[str | None] = mapped_column(String(160))

    semillero: Mapped["Semillero"] = relationship(back_populates="lines")


class SemilleroActivity(db.Model):
    __tablename__ = "semillero_activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    semillero_id: Mapped[int] = mapped_column(ForeignKey("semilleros.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    place: Mapped[str | None] = mapped_column(String(200))
    occurred_on: Mapped[date] = mapped_column(Date, nullable=False)

    semillero: Mapped["Semillero"] = relationship(back_populates="activities")

from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.user import Faculty, Program, User


class Semillero(db.Model):
    __tablename__ = "semilleros"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    area: Mapped[str | None] = mapped_column(String(100))
    mission: Mapped[str | None] = mapped_column(Text)
    vision: Mapped[str | None] = mapped_column(Text)
    faculty_id: Mapped[int | None] = mapped_column(
        ForeignKey("faculties.id", ondelete="SET NULL")
    )
    program_id: Mapped[int | None] = mapped_column(
        ForeignKey("programs.id", ondelete="SET NULL")
    )
    leader_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    faculty: Mapped["Faculty | None"] = relationship()
    program: Mapped["Program | None"] = relationship()
    leader: Mapped["User | None"] = relationship()
    members: Mapped[list["SemilleroMember"]] = relationship(
        back_populates="semillero", cascade="all, delete-orphan"
    )


class SemilleroMember(db.Model):
    __tablename__ = "semillero_members"
    __table_args__ = (UniqueConstraint("semillero_id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    semillero_id: Mapped[int] = mapped_column(
        ForeignKey("semilleros.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role_in_semillero: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Estudiante Investigador",
        server_default="Estudiante Investigador",
    )
    joined_at: Mapped[datetime] = mapped_column(server_default=func.now())

    semillero: Mapped["Semillero"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship()

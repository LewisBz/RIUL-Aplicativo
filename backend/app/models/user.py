from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import bcrypt, db

ROLE_RESEARCHER = "researcher"
ROLE_LEADER = "leader"
ROLE_ADMINISTRATOR = "administrator"

STATUS_ACTIVE = "active"
STATUS_PENDING = "pending"
STATUS_REJECTED = "rejected"


class Faculty(db.Model):
    __tablename__ = "faculties"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)

    programs: Mapped[list["Program"]] = relationship(back_populates="faculty")


class Program(db.Model):
    __tablename__ = "programs"
    __table_args__ = (db.UniqueConstraint("name", "faculty_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculties.id"))

    faculty: Mapped["Faculty"] = relationship(back_populates="programs")


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str | None] = mapped_column(String(160))
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ROLE_RESEARCHER,
        server_default=ROLE_RESEARCHER,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=STATUS_ACTIVE,
        server_default=STATUS_ACTIVE,
    )
    motivation: Mapped[str | None] = mapped_column(String(500))
    faculty_id: Mapped[int | None] = mapped_column(ForeignKey("faculties.id"))
    program_id: Mapped[int | None] = mapped_column(ForeignKey("programs.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    faculty: Mapped["Faculty | None"] = relationship()
    program: Mapped["Program | None"] = relationship()
    profile: Mapped["UserProfile | None"] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False
    )

    def set_password(self, raw: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(raw).decode("utf-8")

    def check_password(self, raw: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, raw)

    def ensure_profile(self) -> "UserProfile":
        """Devuelve el perfil extendido, creándolo si todavía no existe."""
        if self.profile is None:
            self.profile = UserProfile()
        return self.profile


class UserProfile(db.Model):
    """Datos públicos opcionales del investigador (1:1 con `users`)."""

    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    bio: Mapped[str | None] = mapped_column(Text)
    photo: Mapped[str | None] = mapped_column(String(255))
    orcid: Mapped[str | None] = mapped_column(String(19))

    user: Mapped["User"] = relationship(back_populates="profile")

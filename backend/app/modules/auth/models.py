from datetime import datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import bcrypt, db

ROLE_RESEARCHER = "researcher"
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

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "faculty_id": self.faculty_id}


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str | None] = mapped_column(String(160))
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ROLE_RESEARCHER, server_default=ROLE_RESEARCHER
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=STATUS_ACTIVE, server_default=STATUS_ACTIVE
    )
    motivation: Mapped[str | None] = mapped_column(String(500))
    faculty_id: Mapped[int | None] = mapped_column(ForeignKey("faculties.id"))
    program_id: Mapped[int | None] = mapped_column(ForeignKey("programs.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    faculty: Mapped["Faculty | None"] = relationship()
    program: Mapped["Program | None"] = relationship()

    def set_password(self, raw: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(raw).decode("utf-8")

    def check_password(self, raw: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, raw)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "status": self.status,
            "faculty_id": self.faculty_id,
            "program_id": self.program_id,
        }

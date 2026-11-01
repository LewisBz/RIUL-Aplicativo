from datetime import date, datetime

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.semillero import Semillero
from app.models.user import User

PROJECT_PLANNED = "planned"
PROJECT_IN_PROGRESS = "in_progress"
PROJECT_REVIEW = "review"
PROJECT_COMPLETED = "completed"
PROJECT_STATUSES = (PROJECT_PLANNED, PROJECT_IN_PROGRESS, PROJECT_REVIEW, PROJECT_COMPLETED)

PRODUCT_IN_REVIEW = "in_review"
PRODUCT_APPROVED = "approved"
PRODUCT_STATUSES = (PRODUCT_IN_REVIEW, PRODUCT_APPROVED)



class Project(db.Model):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str | None] = mapped_column(String(60))
    status: Mapped[str] = mapped_column(
        String(20), default=PROJECT_PLANNED, server_default=PROJECT_PLANNED
    )
    description: Mapped[str | None] = mapped_column(Text)
    progress: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    line: Mapped[str | None] = mapped_column(String(120))
    role_required: Mapped[str | None] = mapped_column(String(160))
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    semillero_id: Mapped[int | None] = mapped_column(ForeignKey("semilleros.id"))
    leader_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    semillero: Mapped["Semillero | None"] = relationship()
    leader: Mapped["User"] = relationship()
    members: Mapped[list["ProjectMember"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    products: Mapped[list["ProjectProduct"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    milestones: Mapped[list["ProjectMilestone"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProjectMilestone.position",
    )


class ProjectMember(db.Model):
    __tablename__ = "project_members"
    __table_args__ = (UniqueConstraint("project_id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    project: Mapped["Project"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship()


class ProjectProduct(db.Model):
    __tablename__ = "project_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(60), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=PRODUCT_IN_REVIEW, server_default=PRODUCT_IN_REVIEW
    )

    project: Mapped["Project"] = relationship(back_populates="products")


class ProjectMilestone(db.Model):
    __tablename__ = "project_milestones"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    text: Mapped[str] = mapped_column(String(200), nullable=False)
    done: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    position: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    project: Mapped["Project"] = relationship(back_populates="milestones")


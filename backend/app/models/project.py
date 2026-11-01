from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.semillero import Semillero
from app.models.user import User

PROJECT_PLANNED = "planned"
PROJECT_IN_PROGRESS = "in_progress"
PROJECT_REVIEW = "review"
PROJECT_CLOSED = "closed"
PROJECT_STATUSES = (PROJECT_PLANNED, PROJECT_IN_PROGRESS, PROJECT_REVIEW, PROJECT_CLOSED)

MEMBER_PRINCIPAL = "principal"
MEMBER_MEMBER = "member"
PROJECT_MEMBER_ROLES = (MEMBER_PRINCIPAL, MEMBER_MEMBER)

PRODUCT_ARTICLE = "article"
PRODUCT_PRESENTATION = "presentation"
PRODUCT_PATENT = "patent"
PRODUCT_REPORT = "report"
PRODUCT_TYPES = (PRODUCT_ARTICLE, PRODUCT_PRESENTATION, PRODUCT_PATENT, PRODUCT_REPORT)

PRODUCT_IN_REVIEW = "in_review"
PRODUCT_APPROVED = "approved"
PRODUCT_STATUSES = (PRODUCT_IN_REVIEW, PRODUCT_APPROVED)

# Etiquetas en español aceptadas al registrar un producto.
PRODUCT_TYPE_ALIASES = {
    "articulo": PRODUCT_ARTICLE,
    "artículo": PRODUCT_ARTICLE,
    "ponencia": PRODUCT_PRESENTATION,
    "presentacion": PRODUCT_PRESENTATION,
    "presentación": PRODUCT_PRESENTATION,
    "patente": PRODUCT_PATENT,
    "informe": PRODUCT_REPORT,
    "reporte": PRODUCT_REPORT,
}


def normalize_product_type(raw: str | None) -> str | None:
    value = (raw or "").strip().lower()
    if value in PRODUCT_TYPES:
        return value
    return PRODUCT_TYPE_ALIASES.get(value)


class Project(db.Model):
    __tablename__ = "projects"
    __table_args__ = (
        db.CheckConstraint(
            "status IN ('planned','in_progress','review','closed')", name="ck_projects_status"
        ),
        db.CheckConstraint("progress BETWEEN 0 AND 100", name="ck_projects_progress"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str | None] = mapped_column(String(60))
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=PROJECT_PLANNED, server_default=PROJECT_PLANNED
    )
    description: Mapped[str | None] = mapped_column(Text)
    progress: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    line: Mapped[str | None] = mapped_column(String(120))
    role_required: Mapped[str | None] = mapped_column(String(160))
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    semillero_id: Mapped[int | None] = mapped_column(ForeignKey("semilleros.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    semillero: Mapped["Semillero | None"] = relationship()
    members: Mapped[list["ProjectMember"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProjectMember.id",
    )
    products: Mapped[list["Product"]] = relationship(back_populates="project")
    milestones: Mapped[list["ProjectMilestone"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProjectMilestone.position",
    )

    @property
    def principal(self) -> "ProjectMember | None":
        return next((m for m in self.members if m.role == MEMBER_PRINCIPAL), None)

    @property
    def leader(self) -> "User | None":
        principal = self.principal
        return principal.user if principal else None

    @property
    def leader_id(self) -> int | None:
        principal = self.principal
        return principal.user_id if principal else None


class ProjectMember(db.Model):
    __tablename__ = "project_members"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id"),
        db.CheckConstraint(
            "role IN ('principal','member')", name="ck_project_members_role"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default=MEMBER_MEMBER, server_default=MEMBER_MEMBER
    )

    project: Mapped["Project"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship()


class Product(db.Model):
    """Producto de investigación (artículo, ponencia, patente o informe).

    Unifica los antiguos `project_products` y `publications`: pertenece a un
    investigador (`user_id`) y, opcionalmente, a un proyecto.
    """

    __tablename__ = "products"
    __table_args__ = (
        db.CheckConstraint(
            "type IN ('article','presentation','patent','report')", name="ck_products_type"
        ),
        db.CheckConstraint(
            "status IN ('in_review','approved')", name="ck_products_status"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), index=True)
    semillero_id: Mapped[int | None] = mapped_column(ForeignKey("semilleros.id"))
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    venue: Mapped[str | None] = mapped_column(String(160))
    published_on: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=PRODUCT_IN_REVIEW, server_default=PRODUCT_IN_REVIEW
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    owner: Mapped["User"] = relationship()
    project: Mapped["Project | None"] = relationship(back_populates="products")
    semillero: Mapped["Semillero | None"] = relationship()

    @property
    def name(self) -> str:
        return self.title


class ProjectMilestone(db.Model):
    __tablename__ = "project_milestones"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    # Columna `title` en la base; el atributo conserva el nombre `text`.
    text: Mapped[str] = mapped_column("title", String(200), nullable=False)
    done: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    position: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    project: Mapped["Project"] = relationship(back_populates="milestones")

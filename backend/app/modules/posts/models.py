from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.modules.auth.models import User

CATEGORY_ARTICLE = "article"
CATEGORY_PROJECT_ADVANCE = "project_advance"
CATEGORY_PRESENTATION = "presentation"
CATEGORY_EVENT = "event"
CATEGORY_COMMUNITY = "community"
POST_CATEGORIES = (
    CATEGORY_ARTICLE,
    CATEGORY_PROJECT_ADVANCE,
    CATEGORY_PRESENTATION,
    CATEGORY_EVENT,
    CATEGORY_COMMUNITY,
)

KIND_IMAGE = "image"
KIND_FILE = "file"


class Post(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    category: Mapped[str] = mapped_column(
        String(30), nullable=False, default=CATEGORY_COMMUNITY, server_default=CATEGORY_COMMUNITY
    )
    content: Mapped[str | None] = mapped_column(Text)
    link_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    author: Mapped["User"] = relationship()
    attachments: Mapped[list["PostAttachment"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )
    reactions: Mapped[list["PostReaction"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )

    def to_dict(self, viewer_id: int | None = None) -> dict:
        return {
            "id": self.id,
            "category": self.category,
            "content": self.content,
            "link_url": self.link_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "author": {
                "id": self.author.id,
                "full_name": self.author.full_name,
            },
            "attachments": [a.to_dict() for a in self.attachments],
            "reaction_count": len(self.reactions),
            "reacted_by_me": viewer_id is not None
            and any(r.user_id == viewer_id for r in self.reactions),
        }


class PostAttachment(db.Model):
    __tablename__ = "post_attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    kind: Mapped[str] = mapped_column(String(10), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    mime_type: Mapped[str | None] = mapped_column(String(100))
    file_size: Mapped[int | None] = mapped_column()

    post: Mapped["Post"] = relationship(back_populates="attachments")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "kind": self.kind,
            "file_name": self.file_name,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
            "url": f"/api/posts/files/{self.storage_name}",
        }


class PostReaction(db.Model):
    __tablename__ = "post_reactions"
    __table_args__ = (UniqueConstraint("post_id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    post: Mapped["Post"] = relationship(back_populates="reactions")

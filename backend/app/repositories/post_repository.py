from sqlalchemy import func, select

from app.extensions import db
from app.models import Post, PostAttachment, PostReaction


def add_post(post: Post) -> Post:
    db.session.add(post)
    return post


def add_attachment(attachment: PostAttachment) -> PostAttachment:
    db.session.add(attachment)
    return attachment


def get_post(post_id: int) -> Post | None:
    return db.session.get(Post, post_id)


def count_posts(*conditions) -> int:
    return int(
        db.session.scalar(select(func.count()).select_from(Post).where(*conditions))
        or 0
    )


def list_posts(
    filters: list, page: int, per_page: int
) -> tuple[list[Post], int]:
    total = count_posts(*filters)
    stmt = (
        select(Post)
        .where(*filters)
        .order_by(Post.created_at.desc(), Post.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return list(db.session.scalars(stmt).all()), total


def delete_post(post: Post) -> None:
    db.session.delete(post)


def get_reaction(post_id: int, user_id: int) -> PostReaction | None:
    return db.session.scalar(
        select(PostReaction).where(
            PostReaction.post_id == post_id, PostReaction.user_id == user_id
        )
    )


def add_reaction(reaction: PostReaction) -> PostReaction:
    db.session.add(reaction)
    return reaction


def delete_reaction(reaction: PostReaction) -> None:
    db.session.delete(reaction)


def count_reactions(post_id: int) -> int:
    return int(
        db.session.scalar(
            select(func.count())
            .select_from(PostReaction)
            .where(PostReaction.post_id == post_id)
        )
        or 0
    )


def commit() -> None:
    db.session.commit()


def flush() -> None:
    db.session.flush()

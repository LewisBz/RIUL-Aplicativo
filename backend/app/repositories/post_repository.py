from sqlalchemy import func, select

from app.extensions import db
from app.models import Achievement, Comment, Post, PostAttachment, PostReaction, PostShare


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


def post_has_achievements(post_id: int) -> bool:
    return (
        db.session.scalar(select(Achievement.id).where(Achievement.post_id == post_id).limit(1))
        is not None
    )


# --- Reacciones ---
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


# --- Comentarios ---
def add_comment(comment: Comment) -> Comment:
    db.session.add(comment)
    return comment


def get_comment(post_id: int, comment_id: int) -> Comment | None:
    return db.session.scalar(
        select(Comment).where(Comment.post_id == post_id, Comment.id == comment_id)
    )


def list_comments(post_id: int) -> list[Comment]:
    stmt = (
        select(Comment)
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at, Comment.id)
    )
    return list(db.session.scalars(stmt).all())


def count_comments(post_id: int) -> int:
    return int(
        db.session.scalar(
            select(func.count()).select_from(Comment).where(Comment.post_id == post_id)
        )
        or 0
    )


def delete_comment(comment: Comment) -> None:
    db.session.delete(comment)


# --- Compartidos ---
def get_share(post_id: int, user_id: int) -> PostShare | None:
    return db.session.scalar(
        select(PostShare).where(PostShare.post_id == post_id, PostShare.user_id == user_id)
    )


def add_share(share: PostShare) -> PostShare:
    db.session.add(share)
    return share


def delete_share(share: PostShare) -> None:
    db.session.delete(share)


def count_shares(post_id: int) -> int:
    return int(
        db.session.scalar(
            select(func.count()).select_from(PostShare).where(PostShare.post_id == post_id)
        )
        or 0
    )


def commit() -> None:
    db.session.commit()


def flush() -> None:
    db.session.flush()

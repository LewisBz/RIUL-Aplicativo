from sqlalchemy import text

from app.extensions import db


def purge_tables(tables: tuple[str, ...]) -> None:
    db.session.expunge_all()
    db.session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    for table in tables:
        db.session.execute(text(f"TRUNCATE TABLE `{table}`"))
    db.session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    db.session.commit()
    db.session.expunge_all()

from datetime import date, timedelta

from app.extensions import db
from app.models import (
    ACHIEVEMENT_VALIDATED,
    Achievement,
    Faculty,
    Project,
    Publication,
    ROLE_ADMINISTRATOR,
    ROLE_RESEARCHER,
    Semillero,
    SemilleroMember,
)


def test_analytics_requires_admin(client, make_role_user):
    assert client.get("/api/admin/analytics").status_code == 401
    _, headers = make_role_user(ROLE_RESEARCHER)
    assert client.get("/api/admin/analytics", headers=headers).status_code == 403


def test_analytics_empty_state(client, make_role_user):
    _, headers = make_role_user(ROLE_ADMINISTRATOR)
    body = client.get("/api/admin/analytics", headers=headers).get_json()
    assert body["totals"]["publications"] == 0
    assert len(body["production"]) == 12
    assert body["top_semilleros"] == []
    assert body["account_status"]["active"] == 1
    assert body["account_status"]["total"] == 1


def test_analytics_aggregates_real_data(client, make_role_user):
    user, _ = make_role_user(ROLE_RESEARCHER)
    _, headers = make_role_user(ROLE_ADMINISTRATOR)
    faculty = Faculty.query.first()
    semillero = Semillero(slug="sem-a", name="Semillero A", faculty_id=faculty.id)
    db.session.add(semillero)
    db.session.flush()
    db.session.add(SemilleroMember(semillero_id=semillero.id, user_id=user.id))
    db.session.add(Publication(author_id=user.id, title="Paper"))
    db.session.add(Project(slug="p-1", title="Proyecto", leader_id=user.id, status="in_progress"))
    db.session.add(Project(slug="p-2", title="Cerrado", leader_id=user.id, status="completed"))
    db.session.add(
        Achievement(
            user_id=user.id,
            title="Logro",
            status=ACHIEVEMENT_VALIDATED,
            xp=120,
            achieved_on=date.today(),
        )
    )
    db.session.commit()

    body = client.get("/api/admin/analytics", headers=headers).get_json()
    assert body["totals"] == {
        "publications": 1,
        "active_projects": 1,
        "semilleros": 1,
        "validated_xp": 120,
    }
    assert body["top_semilleros"][0]["name"] == "Semillero A"
    assert body["top_semilleros"][0]["xp"] == 120
    assert body["semilleros_by_faculty"][0]["count"] == 1
    assert sum(m["publications"] for m in body["production"]) == 1
    assert sum(m["projects"] for m in body["production"]) == 2


def test_production_uses_business_dates_not_registration_dates(client, make_role_user):
    user, _ = make_role_user(ROLE_RESEARCHER)
    _, headers = make_role_user(ROLE_ADMINISTRATOR)
    three_months_ago = date.today().replace(day=1) - timedelta(days=75)
    long_ago = date.today() - timedelta(days=900)
    db.session.add(
        Project(slug="p-old", title="Antiguo", leader_id=user.id, start_date=three_months_ago)
    )
    db.session.add(
        Publication(author_id=user.id, title="Dentro", published_on=three_months_ago)
    )
    db.session.add(Publication(author_id=user.id, title="Fuera", published_on=long_ago))
    db.session.commit()

    body = client.get("/api/admin/analytics", headers=headers).get_json()
    month = three_months_ago.strftime("%Y-%m")
    entry = next(m for m in body["production"] if m["month"] == month)
    assert entry["projects"] == 1
    assert entry["publications"] == 1
    assert sum(m["publications"] for m in body["production"]) == 1
    assert body["totals"]["publications"] == 2

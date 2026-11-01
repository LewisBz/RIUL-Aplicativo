from datetime import date, timedelta

from app.extensions import db
from app.models import (
    ACHIEVEMENT_APPROVED,
    MEMBER_PRINCIPAL,
    MEMBERSHIP_ACTIVE,
    PRODUCT_ARTICLE,
    ROLE_ADMINISTRATOR,
    ROLE_RESEARCHER,
    TYPE_SEMILLERO,
    Achievement,
    AchievementType,
    Faculty,
    Product,
    Project,
    ProjectMember,
    Semillero,
    SemilleroMember,
)
from app.services import gamification_service


def _project(slug: str, title: str, leader, **fields) -> Project:
    project = Project(slug=slug, title=title, **fields)
    project.members.append(ProjectMember(user_id=leader.id, role=MEMBER_PRINCIPAL))
    db.session.add(project)
    return project


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
    semillero = Semillero(
        slug="sem-a", name="Semillero A", faculty_id=faculty.id, leader_id=user.id
    )
    semillero.members.append(
        SemilleroMember(user_id=user.id, role="leader", status=MEMBERSHIP_ACTIVE)
    )
    db.session.add(semillero)
    db.session.flush()
    gamification_service.ensure_semillero_progress(semillero.id)
    db.session.add(Product(user_id=user.id, type=PRODUCT_ARTICLE, title="Paper"))
    _project("p-1", "Proyecto", user, status="in_progress")
    _project("p-2", "Cerrado", user, status="closed")
    achievement = Achievement(
        user_id=user.id,
        type_id=AchievementType.query.filter_by(code=TYPE_SEMILLERO).one().id,
        semillero_id=semillero.id,
        status=ACHIEVEMENT_APPROVED,
        achieved_on=date.today(),
    )
    db.session.add(achievement)
    db.session.flush()
    gamification_service.apply_approval(achievement, 120)
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
    _project("p-old", "Antiguo", user, start_date=three_months_ago)
    db.session.add(
        Product(
            user_id=user.id, type=PRODUCT_ARTICLE, title="Dentro", published_on=three_months_ago
        )
    )
    db.session.add(
        Product(user_id=user.id, type=PRODUCT_ARTICLE, title="Fuera", published_on=long_ago)
    )
    db.session.commit()

    body = client.get("/api/admin/analytics", headers=headers).get_json()
    month = three_months_ago.strftime("%Y-%m")
    entry = next(m for m in body["production"] if m["month"] == month)
    assert entry["projects"] == 1
    assert entry["publications"] == 1
    assert sum(m["publications"] for m in body["production"]) == 1
    assert body["totals"]["publications"] == 2

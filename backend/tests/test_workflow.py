from app.extensions import db
from app.models import ROLE_LEADER, Post, Semillero, User, UserProgress
from tests.test_admin import admin_token


def test_comment_project_and_achievement_flow(client, make_user, make_headers):
    _, registered = make_user(full_name="Camila de Prueba")
    headers = make_headers(registered["access_token"])
    created = client.post(
        "/api/posts",
        data={"content": "Avance del semillero", "category": "community"},
        headers=headers,
    )
    assert created.status_code == 201, created.get_json()
    post_id = created.get_json()["post"]["id"]

    comment = client.post(
        f"/api/posts/{post_id}/comments",
        json={"body": "Buen avance"},
        headers=headers,
    )
    assert comment.status_code == 201, comment.get_json()
    listed = client.get(f"/api/posts/{post_id}/comments", headers=headers)
    assert listed.get_json()["items"][0]["body"] == "Buen avance"

    project = client.post(
        "/api/projects",
        json={"title": "Proyecto de prueba", "description": "Modelo"},
        headers=headers,
    )
    assert project.status_code == 201, project.get_json()
    assert client.get("/api/projects", headers=headers).status_code == 200

    logro = client.post(
        "/api/achievements",
        json={"title": "Ponencia de prueba", "kind": "presentation", "evidence": "https://ejemplo.test"},
        headers=headers,
    )
    assert logro.status_code == 201, logro.get_json()
    achievement_id = logro.get_json()["id"]

    admin = admin_token(email="admin.workflow@unilibre.edu.co")
    approved = client.patch(
        f"/api/admin/achievements/{achievement_id}",
        json={"status": "approved"},
        headers={"Authorization": f"Bearer {admin}"},
    )
    assert approved.status_code == 200, approved.get_json()

    user = UserProgress.query.filter(UserProgress.xp > 0).first()
    assert user is not None
    assert user.stars >= 1
    reports = client.get(
        "/api/admin/reports",
        headers={"Authorization": f"Bearer {admin}"},
    )
    assert reports.status_code == 200
    assert reports.get_json()["pending_achievements"] >= 0
    assert db.session.get(Post, post_id) is not None


def test_semillero_join(client, make_user, make_headers):
    leader = make_user(email="lider.workflow@unilibre.edu.co", full_name="Líder Workflow")[1]
    from app.models import ROLE_LEADER

    leader_user_id = client.get(
        "/api/auth/me", headers=make_headers(leader["access_token"])
    ).get_json()["user"]["id"]
    person = db.session.get(User, leader_user_id)
    person.role = ROLE_LEADER
    semillero = Semillero(slug="semillero-workflow", name="Semillero Workflow", leader_id=person.id)
    db.session.add(semillero)
    db.session.commit()

    _, student = make_user()
    joined = client.post(
        "/api/semilleros/semillero-workflow/join",
        json={"motivation": "Quiero investigar"},
        headers=make_headers(student["access_token"]),
    )
    assert joined.status_code == 201, joined.get_json()
    pending = client.get(
        "/api/semilleros/semillero-workflow/pending",
        headers=make_headers(leader["access_token"]),
    )
    assert pending.status_code == 200
    assert pending.get_json()["items"]

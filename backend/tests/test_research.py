from datetime import datetime, timedelta

import pytest


def _iso(delta_days: int) -> str:
    return (datetime.now() + timedelta(days=delta_days)).replace(microsecond=0).isoformat()


@pytest.fixture()
def researcher(make_role_user):
    return make_role_user("researcher", "Investigadora Uno")


@pytest.fixture()
def leader(make_role_user):
    return make_role_user("leader", "Docente Líder")


@pytest.fixture()
def admin(make_role_user):
    return make_role_user("administrator", "Admin Demo")


@pytest.fixture()
def semillero(client, leader):
    response = client.post(
        "/api/semilleros",
        json={"name": "Semillero de Pruebas", "area": "IA", "interest_areas": ["IA"],
              "lines": [{"name": "Línea 1"}]},
        headers=leader[1],
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["semillero"]


class TestAuthRequired:
    @pytest.mark.parametrize(
        "path",
        ["/api/semilleros", "/api/projects", "/api/events", "/api/notifications",
         "/api/gamification/me", "/api/gamification/ranking", "/api/dashboard", "/api/profile"],
    )
    def test_endpoints_require_token(self, client, path):
        assert client.get(path).status_code == 401

    def test_unknown_api_route_is_json_404(self, client):
        response = client.get("/api/no-existe")
        assert response.status_code == 404
        assert "message" in response.get_json()

    def test_unknown_page_is_404(self, client):
        assert client.get("/pagina-inexistente").status_code == 404


class TestSemilleros:
    def test_only_leader_or_admin_creates(self, client, researcher):
        response = client.post("/api/semilleros", json={"name": "Nuevo"}, headers=researcher[1])
        assert response.status_code == 403

    def test_create_and_slug_unique(self, client, leader, semillero):
        assert semillero["slug"] == "semillero-de-pruebas"
        again = client.post("/api/semilleros", json={"name": "Semillero de Pruebas"}, headers=leader[1])
        assert again.get_json()["semillero"]["slug"] == "semillero-de-pruebas-2"

    def test_list_filter_and_detail(self, client, researcher, semillero):
        listing = client.get("/api/semilleros?q=Pruebas", headers=researcher[1]).get_json()
        assert listing["total"] == 1 and "IA" in listing["areas"]
        detail = client.get(f"/api/semilleros/{semillero['slug']}", headers=researcher[1]).get_json()
        assert detail["semillero"]["lines"][0]["name"] == "Línea 1"
        assert client.get("/api/semilleros/nope", headers=researcher[1]).status_code == 404

    def test_join_leave_flow_notifies_leader(self, client, researcher, leader, semillero):
        slug = semillero["slug"]
        joined = client.post(f"/api/semilleros/{slug}/members", headers=researcher[1])
        assert joined.status_code == 201
        assert joined.get_json()["semillero"]["my_role"] == "member"
        assert client.post(f"/api/semilleros/{slug}/members", headers=researcher[1]).status_code == 409
        notes = client.get("/api/notifications", headers=leader[1]).get_json()
        assert notes["unread_count"] == 1
        left = client.delete(f"/api/semilleros/{slug}/members/me", headers=researcher[1])
        assert left.status_code == 200 and left.get_json()["semillero"]["my_role"] is None
        assert client.delete(f"/api/semilleros/{slug}/members/me", headers=researcher[1]).status_code == 404

    def test_activity_only_for_leader(self, client, researcher, leader, semillero):
        url = f"/api/semilleros/{semillero['slug']}/activities"
        body = {"title": "Reunión", "occurred_on": "2026-10-01"}
        assert client.post(url, json=body, headers=researcher[1]).status_code == 403
        response = client.post(url, json=body, headers=leader[1])
        assert response.status_code == 201
        assert response.get_json()["semillero"]["activities"][0]["title"] == "Reunión"


class TestProjects:
    def test_create_update_flow(self, client, researcher, semillero):
        slug = semillero["slug"]
        client.post(f"/api/semilleros/{slug}/members", headers=researcher[1])
        created = client.post(
            "/api/projects",
            json={"title": "Proyecto Uno", "semillero": slug, "milestones": ["A", "B"]},
            headers=researcher[1],
        )
        assert created.status_code == 201, created.get_json()
        project = created.get_json()["project"]
        assert project["my_role"] == "leader" and len(project["milestones"]) == 2

        milestone = project["milestones"][0]["id"]
        done = client.patch(f"/api/projects/{project['slug']}/milestones/{milestone}",
                            json={"done": True}, headers=researcher[1])
        assert done.get_json()["project"]["progress"] == 50

        patched = client.patch(f"/api/projects/{project['slug']}",
                               json={"status": "in_progress"}, headers=researcher[1])
        assert patched.get_json()["project"]["status"] == "in_progress"
        product = client.post(f"/api/projects/{project['slug']}/products",
                              json={"type": "Artículo", "name": "Paper"}, headers=researcher[1])
        assert product.status_code == 201

        mine = client.get("/api/projects?mine=1", headers=researcher[1]).get_json()
        assert mine["total"] == 1

    def test_validation_and_permissions(self, client, researcher, make_role_user, semillero):
        assert client.post("/api/projects", json={"title": "x"}, headers=researcher[1]).status_code == 400
        outsider = client.post("/api/projects",
                               json={"title": "Proyecto Ajeno", "semillero": semillero["slug"]},
                               headers=researcher[1])
        assert outsider.status_code == 403
        own = client.post("/api/projects", json={"title": "Proyecto Libre"}, headers=researcher[1])
        slug = own.get_json()["project"]["slug"]
        _, other = make_role_user("researcher")
        assert client.patch(f"/api/projects/{slug}", json={"progress": 10}, headers=other).status_code == 403
        assert client.patch(f"/api/projects/{slug}", json={"progress": 500}, headers=researcher[1]).status_code == 400
        assert client.get("/api/projects?status=invalid", headers=researcher[1]).status_code == 400
        assert client.get("/api/projects/nope", headers=researcher[1]).status_code == 404


class TestEvents:
    def _create(self, client, headers, **overrides):
        body = {"title": "Simposio de Prueba", "starts_at": _iso(5), "ends_at": _iso(6),
                "capacity": 1, "requirements": ["Registro"]}
        body.update(overrides)
        return client.post("/api/events", json=body, headers=headers)

    def test_only_leader_or_admin_creates(self, client, researcher, leader):
        assert self._create(client, researcher[1]).status_code == 403
        assert self._create(client, leader[1]).status_code == 201

    def test_invalid_dates(self, client, leader):
        response = self._create(client, leader[1], starts_at=_iso(6), ends_at=_iso(5))
        assert response.status_code == 400

    def test_registration_capacity_and_achievement(self, client, researcher, make_role_user, leader):
        slug = self._create(client, leader[1]).get_json()["event"]["slug"]
        reg = client.post(f"/api/events/{slug}/registrations", headers=researcher[1])
        assert reg.status_code == 201
        assert reg.get_json()["event"]["participation"] == "registered"
        assert client.post(f"/api/events/{slug}/registrations", headers=researcher[1]).status_code == 409
        _, other = make_role_user("researcher")
        assert client.post(f"/api/events/{slug}/registrations", headers=other).status_code == 409  # sin cupo
        assert client.get(f"/api/events/{slug}", headers=other).get_json()["event"]["participation"] == "full"

        gamification = client.get("/api/gamification/me", headers=researcher[1]).get_json()["gamification"]
        assert gamification["achievements"][0]["status"] == "in_review"
        unreg = client.delete(f"/api/events/{slug}/registrations/me", headers=researcher[1])
        assert unreg.get_json()["event"]["participation"] == "available"

    def test_closed_event_rejects_registration(self, client, researcher, leader):
        slug = self._create(client, leader[1], starts_at=_iso(-3), ends_at=_iso(-2)).get_json()["event"]["slug"]
        assert client.post(f"/api/events/{slug}/registrations", headers=researcher[1]).status_code == 409
        listing = client.get("/api/events?status=closed", headers=researcher[1]).get_json()
        assert listing["items"][0]["participation"] == "closed"


class TestGamificationAndNotifications:
    def test_achievement_review_flow(self, client, researcher, admin):
        created = client.post("/api/gamification/achievements",
                              json={"title": "Ponencia nacional"}, headers=researcher[1])
        assert created.status_code == 201
        achievement_id = created.get_json()["achievement"]["id"]

        assert client.get("/api/admin/achievements", headers=researcher[1]).status_code == 403
        pending = client.get("/api/admin/achievements?status=in_review", headers=admin[1]).get_json()
        assert pending["total"] == 1

        review = client.patch(f"/api/admin/achievements/{achievement_id}",
                              json={"status": "validated", "xp": 250}, headers=admin[1])
        assert review.status_code == 200
        assert client.patch(f"/api/admin/achievements/{achievement_id}",
                            json={"status": "in_review"}, headers=admin[1]).status_code == 400

        summary = client.get("/api/gamification/me", headers=researcher[1]).get_json()["gamification"]
        assert summary["total_xp"] == 250 and summary["level"] == 2 and summary["xp"] == 50

        ranking = client.get("/api/gamification/ranking", headers=researcher[1]).get_json()
        assert ranking["items"][0]["is_current_user"] is True

        notes = client.get("/api/notifications?unread=1", headers=researcher[1]).get_json()
        assert notes["unread_count"] == 1 and notes["items"][0]["type"] == "achievement"
        note_id = notes["items"][0]["id"]
        read = client.patch(f"/api/notifications/{note_id}", json={"read": True}, headers=researcher[1])
        assert read.get_json()["notification"]["read"] is True
        assert client.patch("/api/notifications/9999", json={"read": True}, headers=researcher[1]).status_code == 404

    def test_read_all(self, client, researcher, admin):
        for index in range(2):
            achievement = client.post("/api/gamification/achievements",
                                      json={"title": f"Logro {index}"}, headers=researcher[1])
            client.patch(f"/api/admin/achievements/{achievement.get_json()['achievement']['id']}",
                         json={"status": "rejected"}, headers=admin[1])
        assert client.get("/api/notifications", headers=researcher[1]).get_json()["unread_count"] == 2
        assert client.post("/api/notifications/read-all", headers=researcher[1]).get_json()["unread_count"] == 0

    def test_approving_user_notifies(self, client, make_role_user, admin):
        from app.extensions import db
        from app.models import STATUS_PENDING, User

        pending, headers = make_role_user("researcher")
        pending.status = STATUS_PENDING
        db.session.commit()
        client.patch(f"/api/admin/users/{pending.id}", json={"status": "active"}, headers=admin[1])
        notes = client.get("/api/notifications", headers=headers).get_json()
        assert notes["items"][0]["type"] == "account"


class TestProfileAndDashboard:
    def test_profile_update_and_password(self, client, researcher, ids):
        body = {"full_name": "Nombre Nuevo", "faculty_id": ids["facultad_ingenieria"],
                "program_id": ids["programa_sistemas"]}
        updated = client.patch("/api/profile", json=body, headers=researcher[1]).get_json()["profile"]
        assert updated["user"]["full_name"] == "Nombre Nuevo"
        assert updated["program"]["name"] == "Ingeniería de Sistemas"
        assert client.patch("/api/profile", json={"full_name": " "}, headers=researcher[1]).status_code == 400

        wrong = client.post("/api/profile/password",
                            json={"current_password": "mal", "new_password": "nueva12345"},
                            headers=researcher[1])
        assert wrong.status_code == 400
        ok = client.post("/api/profile/password",
                         json={"current_password": "secreto123", "new_password": "nueva12345"},
                         headers=researcher[1])
        assert ok.status_code == 204
        login = client.post("/api/auth/login",
                            json={"email": researcher[0].email, "password": "nueva12345"})
        assert login.status_code == 200

    def test_publication_and_dashboard(self, client, researcher):
        pub = client.post("/api/publications",
                          json={"title": "Mi artículo", "venue": "IEEE", "published_on": "2026-01-10"},
                          headers=researcher[1])
        assert pub.status_code == 201
        profile = client.get("/api/profile", headers=researcher[1]).get_json()["profile"]
        assert profile["publications"][0]["title"] == "Mi artículo"
        dashboard = client.get("/api/dashboard", headers=researcher[1]).get_json()["dashboard"]
        assert dashboard["publications"][0]["venue"] == "IEEE"
        assert dashboard["gamification"]["level"] == 1
        assert dashboard["semillero"] is None

    def test_admin_delete_any_post(self, client, researcher, admin):
        created = client.post("/api/posts", data={"content": "Hola"}, headers=researcher[1],
                              content_type="multipart/form-data")
        post_id = created.get_json()["post"]["id"]
        assert client.delete(f"/api/posts/{post_id}", headers=admin[1]).status_code == 204


class TestAdminUsers:
    def test_search_users(self, client, admin, researcher):
        found = client.get("/api/admin/users?q=Investigadora", headers=admin[1]).get_json()
        assert found["total"] == 1

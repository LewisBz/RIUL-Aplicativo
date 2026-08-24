from app.extensions import db
from app.modules.auth.models import (
    ROLE_ADMINISTRATOR,
    ROLE_LEADER,
    STATUS_ACTIVE,
    User,
)
from app.modules.auth.services import create_access_token_for


def admin_token(name="Administrador Demo", email="admin.demo@unilibre.edu.co"):
    user = User(
        full_name=name,
        email=email,
        role=ROLE_ADMINISTRATOR,
        status=STATUS_ACTIVE,
    )
    user.set_password("secreto123")
    db.session.add(user)
    db.session.commit()
    return create_access_token_for(user)


def make_leader(email="docente.demo@unilibre.edu.co"):
    user = User(
        full_name="Docente Demo",
        email=email,
        role=ROLE_LEADER,
        status=STATUS_ACTIVE,
    )
    user.set_password("secreto123")
    db.session.add(user)
    db.session.commit()
    return user


class TestAdminOverview:
    def test_requires_authentication(self, client):
        response = client.get("/api/admin/overview")

        assert response.status_code == 401

    def test_rejects_researcher(self, client, make_user):
        _, body = make_user()

        response = client.get(
            "/api/admin/overview",
            headers={"Authorization": f"Bearer {body['access_token']}"},
        )

        assert response.status_code == 403

    def test_returns_real_counts_for_admin(self, client, make_user):
        make_user()
        token = admin_token()

        response = client.get(
            "/api/admin/overview",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        body = response.get_json()
        assert body["users"]["total"] == 2
        assert body["users"]["active"] == 2
        assert body["faculties"] == 2
        assert "semilleros" in body["unavailable"]

    def test_rechecks_user_status_after_token_creation(self, client):
        token = admin_token()
        user = User.query.filter_by(email="admin.demo@unilibre.edu.co").one()
        user.status = "suspended"
        db.session.commit()

        response = client.get(
            "/api/admin/overview",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401

    def test_lists_users_for_admin(self, client, make_user):
        make_user()
        token = admin_token()

        response = client.get(
            "/api/admin/users?status=active",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.get_json()["total"] == 2

    def test_rejects_invalid_user_filter(self, client):
        token = admin_token()

        response = client.get(
            "/api/admin/users?status=unknown",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400

    def test_rejects_invalid_role_filter(self, client):
        token = admin_token()

        response = client.get(
            "/api/admin/users?role=unknown",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400

    def test_filters_users_by_leader_role(self, client, make_user):
        make_user()
        make_leader()
        token = admin_token()

        response = client.get(
            "/api/admin/users?role=leader",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        body = response.get_json()
        assert body["total"] == 1
        assert body["items"][0]["role"] == "leader"
        assert body["items"][0]["email"] == "docente.demo@unilibre.edu.co"

    def test_admin_can_update_researcher_status(self, client, make_user):
        _, body = make_user()
        token = admin_token()

        response = client.patch(
            f"/api/admin/users/{body['user']['id']}",
            json={"status": "rejected"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.get_json()["user"]["status"] == "rejected"

    def test_admin_cannot_deactivate_self(self, client):
        token = admin_token()
        user = User.query.filter_by(email="admin.demo@unilibre.edu.co").one()

        response = client.patch(
            f"/api/admin/users/{user.id}",
            json={"status": "rejected"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
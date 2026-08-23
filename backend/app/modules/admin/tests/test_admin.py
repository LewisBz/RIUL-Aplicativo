from app.extensions import db
from app.modules.auth.models import ROLE_ADMINISTRATOR, STATUS_ACTIVE, User
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
from app.modules.auth.tests.conftest import unique_email


class TestInstitutionalRegistration:
    def test_register_returns_201_with_active_user_and_token(self, client, ids):
        email = unique_email()
        response = client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "secreto123",
                "full_name": "Ana María Torres",
                "faculty_id": ids["facultad_ingenieria"],
                "program_id": ids["programa_sistemas"],
            },
        )
        assert response.status_code == 201
        body = response.get_json()
        assert body["access_token"]
        assert body["user"]["email"] == email
        assert body["user"]["status"] == "active"
        assert body["user"]["role"] == "researcher"

    def test_register_rejects_non_institutional_domain(self, client):
        response = client.post(
            "/api/auth/register",
            json={"email": unique_email("gmail.com"), "password": "secreto123"},
        )
        assert response.status_code == 400
        assert "unilibre.edu.co" in response.get_json()["message"]

    def test_register_rejects_duplicate_email(self, client, make_user):
        payload, _ = make_user()
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 409

    def test_register_rejects_short_password(self, client):
        response = client.post(
            "/api/auth/register",
            json={"email": unique_email(), "password": "corta"},
        )
        assert response.status_code == 400


class TestExternalAccountRequest:
    def test_request_account_creates_pending_without_token(self, client, ids):
        email = unique_email("gmail.com")
        response = client.post(
            "/api/auth/request-account",
            json={
                "email": email,
                "full_name": "Investigador Externo",
                "motivation": "Colaborar en proyectos de investigación.",
                "faculty_id": ids["facultad_ingenieria"],
                "program_id": ids["programa_industrial"],
            },
        )
        assert response.status_code == 202
        body = response.get_json()
        assert "access_token" not in body
        assert "pendiente de aprobación" in body["message"]

    def test_request_account_rejects_institutional_email(self, client):
        response = client.post(
            "/api/auth/request-account",
            json={
                "email": unique_email(),
                "full_name": "Alguien",
                "motivation": "Motivo",
                "faculty_id": 1,
                "program_id": 1,
            },
        )
        assert response.status_code == 400

    def test_pending_account_cannot_login(self, client, ids):
        email = unique_email("gmail.com")
        client.post(
            "/api/auth/request-account",
            json={
                "email": email,
                "full_name": "Pendiente User",
                "motivation": "Quiero participar.",
                "faculty_id": ids["facultad_ingenieria"],
                "program_id": ids["programa_sistemas"],
            },
        )
        response = client.post(
            "/api/auth/login", json={"email": email, "password": "lo-que-sea-123"}
        )
        assert response.status_code == 403
        assert (
            "Solicitud pendiente de aprobación" in response.get_json()["message"]
        )


class TestLogin:
    def test_login_success_returns_token(self, client, make_user):
        payload, registered = make_user()
        response = client.post(
            "/api/auth/login",
            json={"email": payload["email"], "password": payload["password"]},
        )
        assert response.status_code == 200
        body = response.get_json()
        assert body["access_token"]
        assert body["user"]["id"] == registered["user"]["id"]

    def test_login_wrong_password_401(self, client, make_user):
        payload, _ = make_user()
        response = client.post(
            "/api/auth/login",
            json={"email": payload["email"], "password": "incorrecta99"},
        )
        assert response.status_code == 401

    def test_login_unknown_email_401(self, client):
        response = client.post(
            "/api/auth/login",
            json={"email": "nadie@unilibre.edu.co", "password": "secreto123"},
        )
        assert response.status_code == 401


class TestProtectedMe:
    def test_me_requires_bearer_token(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_me_returns_identity_from_valid_token(self, client, make_user):
        _, registered = make_user()
        token = registered["access_token"]
        response = client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.get_json()["user"]["id"] == registered["user"]["id"]

    def test_me_rejects_garbage_token(self, client):
        response = client.get(
            "/api/auth/me", headers={"Authorization": "Bearer no-es-un-jwt"}
        )
        assert response.status_code == 401


class TestCatalog:
    def test_catalog_lists_faculties_with_programs(self, client, ids):
        response = client.get("/api/auth/catalog")
        assert response.status_code == 200
        faculties = response.get_json()["faculties"]
        ing = next(f for f in faculties if f["name"] == "Ingeniería")
        program_names = [p["name"] for p in ing["programs"]]
        assert "Ingeniería de Sistemas" in program_names

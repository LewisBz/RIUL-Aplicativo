import os

from app import SEED_USERS_DEFAULT_PASSWORD
from app.modules.auth.models import Faculty, Program, User

DEMO_EMAILS = {
    "estudiante.demo@unilibre.edu.co": "researcher",
    "docente.demo@unilibre.edu.co": "leader",
    "admin.demo@unilibre.edu.co": "administrator",
}


def _run_seed(app):
    runner = app.test_cli_runner()
    result = runner.invoke(args=["seed-users"])
    assert result.exit_code == 0, result.output
    return result


class TestSeedUsersCommand:
    def test_creates_one_user_per_role(self, app):
        _run_seed(app)

        users = {user.email: user for user in User.query.all()}
        for email, role in DEMO_EMAILS.items():
            assert email in users
            assert users[email].role == role
            assert users[email].status == "active"
            assert users[email].check_password(
                os.environ.get("DEMO_USERS_PASSWORD", SEED_USERS_DEFAULT_PASSWORD)
            )

    def test_assigns_faculty_and_program_to_non_admins(self, app):
        _run_seed(app)

        faculty = Faculty.query.filter_by(name="Ingeniería").first()
        program = Program.query.filter_by(name="Ingeniería de Sistemas").first()
        student = User.query.filter_by(
            email="estudiante.demo@unilibre.edu.co"
        ).one()
        leader = User.query.filter_by(email="docente.demo@unilibre.edu.co").one()
        admin = User.query.filter_by(email="admin.demo@unilibre.edu.co").one()

        assert student.faculty_id == faculty.id
        assert student.program_id == program.id
        assert leader.faculty_id == faculty.id
        assert leader.program_id == program.id
        assert admin.faculty_id is None

    def test_is_idempotent(self, app):
        _run_seed(app)
        result = _run_seed(app)

        assert "0 creados, 3 actualizados" in result.output
        count = User.query.filter(User.email.in_(DEMO_EMAILS.keys())).count()
        assert count == 3

    def test_seeded_accounts_can_login(self, app, client):
        _run_seed(app)

        for email in DEMO_EMAILS:
            response = client.post(
                "/api/auth/login",
                json={
                    "email": email,
                    "password": os.environ.get(
                        "DEMO_USERS_PASSWORD", SEED_USERS_DEFAULT_PASSWORD
                    ),
                },
            )
            assert response.status_code == 200, response.get_json()
            assert response.get_json()["user"]["role"] == DEMO_EMAILS[email]

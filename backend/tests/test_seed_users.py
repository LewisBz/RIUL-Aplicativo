import os

from app import SEED_USERS_DEFAULT_PASSWORD
from app.models import Faculty, Post, PostReaction, Program, User

EXPECTED_USERS = 15
EXPECTED_POSTS = 15
EXPECTED_REACTIONS = 47

EXPECTED_ROLES = {"administrator": 2, "leader": 4, "researcher": 9}
EXPECTED_STATUSES = {"active": 13, "pending": 1, "rejected": 1}

FACULTY_PROGRAMS = {"Ingeniería": 2, "Ciencias Básicas": 1}

TEAMS = {
    "laura.mendoza@unilibre.edu.co": {
        "camila.rojas@unilibre.edu.co",
        "andres.perez@unilibre.edu.co",
    },
    "maria.antonieta.perez@unilibre.edu.co": {
        "luis.grandett@unilibre.edu.co",
        "carolina.martinez@unilibre.edu.co",
    },
    "mateo.silva@unilibre.edu.co": {
        "diego.gutierrez@unilibre.edu.co",
        "paula.fernandez@unilibre.edu.co",
    },
    "javier.torres@unilibre.edu.co": {"sofia.diaz@unilibre.edu.co"},
}


def _run_seed(app):
    runner = app.test_cli_runner()
    result = runner.invoke(args=["seed-demo"])
    assert result.exit_code == 0, result.output
    return result


class TestSeedDemoCommand:
    def test_creates_full_dataset(self, app):
        _run_seed(app)

        assert User.query.count() == EXPECTED_USERS
        assert Post.query.count() == EXPECTED_POSTS
        assert PostReaction.query.count() == EXPECTED_REACTIONS

    def test_roles_and_statuses(self, app):
        _run_seed(app)

        for role, expected in EXPECTED_ROLES.items():
            assert User.query.filter(User.role == role).count() == expected
        for status, expected in EXPECTED_STATUSES.items():
            assert User.query.filter(User.status == status).count() == expected

    def test_faculties_and_programs(self, app):
        _run_seed(app)

        for name, expected_programs in FACULTY_PROGRAMS.items():
            faculty = Faculty.query.filter_by(name=name).one()
            assert (
                Program.query.filter_by(faculty_id=faculty.id).count()
                == expected_programs
            )

    def test_researchers_share_program_with_their_leader(self, app):
        _run_seed(app)

        for leader_email, members in TEAMS.items():
            leader = User.query.filter_by(email=leader_email).one()
            assert leader.role == "leader"
            for member_email in members:
                member = User.query.filter_by(email=member_email).one()
                assert member.role == "researcher"
                assert member.faculty_id == leader.faculty_id
                assert member.program_id == leader.program_id

    def test_admins_have_no_faculty(self, app):
        _run_seed(app)

        for admin in User.query.filter(User.role == "administrator").all():
            assert admin.faculty_id is None
            assert admin.program_id is None

    def test_all_categories_are_present(self, app):
        _run_seed(app)

        categories = {post.category for post in Post.query.all()}
        assert categories == {
            "event",
            "project_advance",
            "article",
            "presentation",
            "community",
        }

    def test_no_duplicate_reactions(self, app):
        _run_seed(app)

        for post in Post.query.all():
            seen = {r.user_id for r in post.reactions}
            assert len(seen) == len(post.reactions)

    def test_active_accounts_login_and_pending_rejected_are_blocked(self, app, client):
        _run_seed(app)
        password = os.environ.get("DEMO_USERS_PASSWORD", SEED_USERS_DEFAULT_PASSWORD)

        for email in [
            "laura.mendoza@unilibre.edu.co",
            "camila.rojas@unilibre.edu.co",
        ]:
            response = client.post(
                "/api/auth/login", json={"email": email, "password": password}
            )
            assert response.status_code == 200, response.get_json()

        for email in ["isabela.blanco@gmail.com", "tomas.restrepo@hotmail.com"]:
            response = client.post(
                "/api/auth/login", json={"email": email, "password": password}
            )
            assert response.status_code == 403, response.get_json()

    def test_all_users_share_the_demo_password(self, app):
        _run_seed(app)

        password = os.environ.get("DEMO_USERS_PASSWORD", SEED_USERS_DEFAULT_PASSWORD)
        for user in User.query.all():
            assert user.check_password(password)

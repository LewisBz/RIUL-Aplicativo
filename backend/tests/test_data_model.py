"""Contrato del modelo de datos: tablas, restricciones y flujos de los dominios nuevos."""
import io
from datetime import date, datetime, timedelta

import pytest
from sqlalchemy.exc import DBAPIError

from app.extensions import db
from app.models import (
    Achievement,
    AchievementType,
    CallApplication,
    Event,
    Project,
    SemilleroProgress,
    UserBadge,
    UserProgress,
    XpLedger,
)

EXPECTED_TABLES = {
    # Usuarios y organización
    "users", "user_profiles", "faculties", "programs",
    # Comunidad
    "posts", "post_attachments", "post_reactions", "comments", "post_shares",
    # Semilleros
    "semilleros", "semillero_members", "semillero_research_lines",
    "semillero_follows", "semillero_progress", "semillero_activities",
    # Proyectos y productos
    "projects", "project_members", "project_milestones", "products",
    # Eventos y convocatorias
    "events", "event_participations", "calls", "call_applications",
    # Gamificación
    "levels", "badges", "achievement_types", "achievements", "evidences",
    "user_badges", "xp_ledger", "user_progress",
    # Soporte y analítica
    "notifications", "report_snapshots", "support_tickets",
}
LEGACY_TABLES = {"publications", "project_products", "event_registrations"}


def _iso(days: int) -> str:
    return (datetime.now() + timedelta(days=days)).replace(microsecond=0).isoformat()


@pytest.fixture()
def researcher(make_role_user):
    return make_role_user("researcher", "Investigadora Uno")


@pytest.fixture()
def other(make_role_user):
    return make_role_user("researcher", "Investigador Dos")


@pytest.fixture()
def leader(make_role_user):
    return make_role_user("leader", "Docente Líder")


@pytest.fixture()
def admin(make_role_user):
    return make_role_user("administrator", "Admin Demo")


@pytest.fixture()
def semillero(client, leader, ids):
    response = client.post(
        "/api/semilleros",
        json={"name": "Semillero Modelo", "faculty_id": ids["facultad_ingenieria"]},
        headers=leader[1],
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["semillero"]


def _join(client, semillero, leader, who):
    slug = semillero["slug"]
    client.post(f"/api/semilleros/{slug}/members", headers=who[1])
    approved = client.patch(
        f"/api/semilleros/{slug}/members/{who[0].id}",
        json={"status": "active"},
        headers=leader[1],
    )
    assert approved.status_code == 200, approved.get_json()


# --- Esquema -----------------------------------------------------------------
class TestSchemaContract:
    def test_all_domain_tables_exist_and_legacy_ones_do_not(self, app):
        tables = set(db.inspect(db.engine).get_table_names())
        assert EXPECTED_TABLES <= tables
        assert not (LEGACY_TABLES & tables)

    def test_reference_catalogs_are_seeded(self, app):
        from app.models import Badge, Level

        assert Level.query.count() == 20
        assert Badge.query.count() == 7
        assert {t.code for t in AchievementType.query.all()} == {
            "event", "post", "project", "article", "presentation", "patent", "semillero",
        }

    def test_achievement_requires_exactly_one_origin(self, app, researcher):
        achievement_type = AchievementType.query.filter_by(code="event").one()
        event = Event(
            slug="e", title="E", starts_at=datetime.now(), ends_at=datetime.now() + timedelta(hours=1),
            created_by=researcher[0].id,
        )
        project = Project(slug="p", title="P")
        db.session.add_all([event, project])
        db.session.flush()
        base = dict(user_id=researcher[0].id, type_id=achievement_type.id, achieved_on=date.today())

        for origins in ({}, {"event_id": event.id, "project_id": project.id}):
            db.session.add(Achievement(**base, **origins))
            with pytest.raises(DBAPIError):
                db.session.flush()
            db.session.rollback()

    def test_event_cannot_end_before_it_starts(self, app, researcher):
        db.session.add(
            Event(
                slug="e2", title="E2", starts_at=datetime.now(),
                ends_at=datetime.now() - timedelta(days=1), created_by=researcher[0].id,
            )
        )
        with pytest.raises(DBAPIError):
            db.session.flush()
        db.session.rollback()

    def test_application_needs_user_xor_semillero(self, app, admin):
        from app.models import Call

        call = Call(
            slug="c", title="C", starts_at=datetime.now(),
            ends_at=datetime.now() + timedelta(days=1), published_by=admin[0].id,
        )
        db.session.add(call)
        db.session.flush()
        db.session.add(CallApplication(call_id=call.id))
        with pytest.raises(DBAPIError):
            db.session.flush()
        db.session.rollback()

    def test_project_progress_is_bounded(self, app):
        db.session.add(Project(slug="p3", title="P3", progress=150))
        with pytest.raises(DBAPIError):
            db.session.flush()
        db.session.rollback()


# --- Feed: comentarios y compartidos -------------------------------------------
class TestCommentsAndShares:
    def _post(self, client, headers):
        response = client.post(
            "/api/posts", data={"content": "Hola comunidad"}, headers=headers,
            content_type="multipart/form-data",
        )
        return response.get_json()["post"]["id"]

    def test_comment_lifecycle(self, client, researcher, other, admin):
        post_id = self._post(client, researcher[1])
        url = f"/api/posts/{post_id}/comments"
        assert client.post(url, json={"body": "  "}, headers=other[1]).status_code == 400
        created = client.post(url, json={"body": "Gran aporte"}, headers=other[1])
        assert created.status_code == 201
        comment = created.get_json()["comment"]
        assert comment["author"]["full_name"] == "Investigador Dos"

        listing = client.get(url, headers=researcher[1]).get_json()
        assert listing["total"] == 1
        feed = client.get("/api/posts", headers=researcher[1]).get_json()["items"][0]
        assert feed["comment_count"] == 1

        delete = f"{url}/{comment['id']}"
        assert client.delete(delete, headers=researcher[1]).status_code == 403
        assert client.delete(delete, headers=admin[1]).status_code == 204
        assert client.get(url, headers=researcher[1]).get_json()["total"] == 0
        assert client.post("/api/posts/9999/comments", json={"body": "x"}, headers=other[1]).status_code == 404

    def test_share_toggles_and_counts(self, client, researcher, other):
        post_id = self._post(client, researcher[1])
        url = f"/api/posts/{post_id}/shares"
        first = client.post(url, headers=other[1]).get_json()
        assert first == {"share_count": 1, "shared_by_me": True}
        feed = client.get("/api/posts", headers=other[1]).get_json()["items"][0]
        assert feed["share_count"] == 1 and feed["shared_by_me"] is True
        assert client.post(url, headers=other[1]).get_json() == {"share_count": 0, "shared_by_me": False}

    def test_deleting_post_removes_comments_and_shares(self, client, researcher, other):
        post_id = self._post(client, researcher[1])
        client.post(f"/api/posts/{post_id}/comments", json={"body": "ok"}, headers=other[1])
        client.post(f"/api/posts/{post_id}/shares", headers=other[1])
        assert client.delete(f"/api/posts/{post_id}", headers=researcher[1]).status_code == 204
        assert db.session.execute(db.text("SELECT COUNT(*) FROM comments")).scalar() == 0
        assert db.session.execute(db.text("SELECT COUNT(*) FROM post_shares")).scalar() == 0


# --- Convocatorias -----------------------------------------------------------
class TestCalls:
    def _call(self, client, headers):
        return client.post(
            "/api/events",
            json={"title": "Convocatoria Semilleros", "kind": "call",
                  "starts_at": _iso(1), "ends_at": _iso(20)},
            headers=headers,
        )

    def test_only_admin_publishes_calls(self, client, leader, admin):
        assert self._call(client, leader[1]).status_code == 403
        created = self._call(client, admin[1])
        assert created.status_code == 201
        assert created.get_json()["event"]["kind"] == "call"

    def test_application_and_review(self, client, admin, researcher, other):
        slug = self._call(client, admin[1]).get_json()["event"]["slug"]
        applied = client.post(f"/api/events/{slug}/registrations", headers=researcher[1])
        assert applied.status_code == 201
        assert applied.get_json()["event"]["participation"] == "registered"
        assert client.post(f"/api/events/{slug}/registrations", headers=researcher[1]).status_code == 409

        url = f"/api/events/{slug}/applications"
        assert client.get(url, headers=researcher[1]).status_code == 403
        items = client.get(url, headers=admin[1]).get_json()["items"]
        assert len(items) == 1 and items[0]["status"] == "pending"
        assert items[0]["applicant"]["name"] == "Investigadora Uno"

        review = client.patch(f"{url}/{items[0]['id']}", json={"status": "accepted"}, headers=admin[1])
        assert review.status_code == 200 and review.get_json()["application"]["status"] == "accepted"
        assert client.patch(f"{url}/{items[0]['id']}", json={"status": "pending"}, headers=admin[1]).status_code == 400
        # Una postulación resuelta ya no se puede retirar.
        withdraw = client.delete(f"/api/events/{slug}/registrations/me", headers=researcher[1])
        assert withdraw.status_code == 409
        # Otro usuario puede postularse y retirar mientras esté pendiente.
        client.post(f"/api/events/{slug}/registrations", headers=other[1])
        assert client.delete(f"/api/events/{slug}/registrations/me", headers=other[1]).status_code == 200

    def test_semillero_application_requires_its_leader(self, client, admin, leader, researcher, semillero):
        slug = self._call(client, admin[1]).get_json()["event"]["slug"]
        body = {"semillero": semillero["slug"]}
        denied = client.post(f"/api/events/{slug}/registrations", json=body, headers=researcher[1])
        assert denied.status_code == 403
        ok = client.post(f"/api/events/{slug}/registrations", json=body, headers=leader[1])
        assert ok.status_code == 201
        again = client.post(f"/api/events/{slug}/registrations", json=body, headers=leader[1])
        assert again.status_code == 409
        items = client.get(f"/api/events/{slug}/applications", headers=admin[1]).get_json()["items"]
        assert items[0]["applicant"]["kind"] == "semillero"

    def test_calls_are_listed_by_kind(self, client, admin, leader, researcher):
        self._call(client, admin[1])
        client.post(
            "/api/events",
            json={"title": "Simposio", "starts_at": _iso(2), "ends_at": _iso(3)},
            headers=leader[1],
        )
        calls = client.get("/api/events?kind=call", headers=researcher[1]).get_json()
        assert [e["kind"] for e in calls["items"]] == ["call"]
        assert client.get("/api/events", headers=researcher[1]).get_json()["total"] == 2


# --- Logros con origen único, XP y progreso -------------------------------------
class TestAchievementsPipeline:
    def _project_with_article(self, client, semillero, leader, researcher):
        _join(client, semillero, leader, researcher)
        project = client.post(
            "/api/projects",
            json={"title": "Proyecto XP", "semillero": semillero["slug"]},
            headers=researcher[1],
        ).get_json()["project"]
        product = client.post(
            f"/api/projects/{project['slug']}/products",
            json={"type": "Artículo", "name": "Paper XP"},
            headers=researcher[1],
        ).get_json()["product"]
        return project, product

    def test_requires_single_valid_origin(self, client, researcher):
        post = lambda body: client.post("/api/gamification/achievements", json=body, headers=researcher[1])
        assert post({"title": "Sin origen"}).status_code == 400
        assert post({"event": "a", "project": "b"}).status_code == 400
        assert post({"project": "no-existe"}).status_code == 404
        assert post({"event": "no-existe"}).status_code == 404

    def test_ownership_checks(self, client, semillero, leader, researcher, other):
        project, product = self._project_with_article(client, semillero, leader, researcher)
        post = lambda body, who: client.post("/api/gamification/achievements", json=body, headers=who[1])
        assert post({"project": project["slug"]}, other).status_code == 403
        assert post({"product": product["id"]}, other).status_code == 403
        assert post({"semillero": semillero["slug"]}, other).status_code == 403

    def test_type_is_derived_from_origin_and_not_duplicated(self, client, semillero, leader, researcher):
        project, product = self._project_with_article(client, semillero, leader, researcher)
        body = {"product": product["id"]}
        created = client.post("/api/gamification/achievements", json=body, headers=researcher[1])
        assert created.status_code == 201
        data = created.get_json()["achievement"]
        assert data["type"] == "article" and data["status"] == "pending"
        assert data["origin"]["kind"] == "product" and data["xp"] == 150
        assert client.post("/api/gamification/achievements", json=body, headers=researcher[1]).status_code == 409
        wrong = client.post(
            "/api/gamification/achievements",
            json={"project": project["slug"], "type": "patent"},
            headers=researcher[1],
        )
        assert wrong.status_code == 400

    def test_approval_feeds_ledger_progress_badges_and_semillero(
        self, client, semillero, leader, researcher, admin
    ):
        _, product = self._project_with_article(client, semillero, leader, researcher)
        created = client.post(
            "/api/gamification/achievements", json={"product": product["id"]}, headers=researcher[1]
        ).get_json()["achievement"]
        approved = client.patch(
            f"/api/admin/achievements/{created['id']}", json={"status": "approved"}, headers=admin[1]
        )
        assert approved.status_code == 200

        achievement = db.session.get(Achievement, created["id"])
        assert achievement.validated_by == admin[0].id and achievement.validated_at is not None
        assert achievement.xp_semillero_id is not None  # acreditado al semillero del proyecto
        assert XpLedger.query.filter_by(achievement_id=achievement.id).one().amount == 150
        progress = UserProgress.query.filter_by(user_id=researcher[0].id).one()
        assert progress.xp == 150 and progress.level.level_number == 1 and progress.stars == 1
        assert UserBadge.query.filter_by(user_id=researcher[0].id).count() == 1
        semillero_progress = SemilleroProgress.query.filter_by(
            semillero_id=achievement.xp_semillero_id
        ).one()
        assert semillero_progress.xp == 150

    def test_rejection_gives_no_xp(self, client, semillero, leader, researcher, admin):
        _, product = self._project_with_article(client, semillero, leader, researcher)
        created = client.post(
            "/api/gamification/achievements", json={"product": product["id"]}, headers=researcher[1]
        ).get_json()["achievement"]
        client.patch(
            f"/api/admin/achievements/{created['id']}", json={"status": "rejected"}, headers=admin[1]
        )
        assert XpLedger.query.count() == 0
        assert UserProgress.query.count() == 0
        summary = client.get("/api/gamification/me", headers=researcher[1]).get_json()["gamification"]
        assert summary["total_xp"] == 0

    def test_catalog_lists_types(self, client, researcher):
        items = client.get("/api/gamification/types", headers=researcher[1]).get_json()["items"]
        assert {t["code"] for t in items} >= {"event", "article", "patent"}
        assert all(t["xp_value"] > 0 for t in items)

    def test_evidence_upload_and_privacy(self, client, semillero, leader, researcher, other, admin):
        _, product = self._project_with_article(client, semillero, leader, researcher)
        achievement = client.post(
            "/api/gamification/achievements", json={"product": product["id"]}, headers=researcher[1]
        ).get_json()["achievement"]
        url = f"/api/gamification/achievements/{achievement['id']}/evidences"

        no_file = client.post(url, headers=researcher[1], content_type="multipart/form-data")
        assert no_file.status_code == 400
        bad = client.post(
            url, data={"file": (io.BytesIO(b"x"), "virus.exe")}, headers=researcher[1],
            content_type="multipart/form-data",
        )
        assert bad.status_code == 400
        foreign = client.post(
            url, data={"file": (io.BytesIO(b"%PDF-1.4"), "ev.pdf")}, headers=other[1],
            content_type="multipart/form-data",
        )
        assert foreign.status_code == 403

        uploaded = client.post(
            url, data={"file": (io.BytesIO(b"%PDF-1.4 contenido"), "ev.pdf")}, headers=researcher[1],
            content_type="multipart/form-data",
        )
        assert uploaded.status_code == 201
        evidence = uploaded.get_json()["evidence"]
        assert evidence["file_name"] == "ev.pdf"
        assert client.get(evidence["url"], headers=researcher[1]).status_code == 200
        assert client.get(evidence["url"], headers=admin[1]).status_code == 200
        assert client.get(evidence["url"], headers=other[1]).status_code == 403
        summary = client.get("/api/gamification/me", headers=researcher[1]).get_json()["gamification"]
        assert summary["achievements"][0]["evidence_count"] == 1


# --- Reportes --------------------------------------------------------------------
class TestReports:
    BODY = {"kind": "report", "period_start": "2026-01-01", "period_end": "2026-03-31"}

    def test_generate_publish_and_public_visibility(self, client, admin, researcher):
        assert client.post("/api/admin/reports", json=self.BODY, headers=researcher[1]).status_code == 403
        created = client.post("/api/admin/reports", json=self.BODY, headers=admin[1])
        assert created.status_code == 201
        report = created.get_json()["report"]
        assert report["published"] is False and "period" in report["metrics"]

        assert client.get("/api/reports", headers=researcher[1]).get_json()["total"] == 0
        assert client.get(f"/api/reports/{report['id']}", headers=researcher[1]).status_code == 404

        url = f"/api/admin/reports/{report['id']}/publication"
        assert client.post(url, headers=admin[1]).status_code == 200
        assert client.post(url, headers=admin[1]).status_code == 409
        public = client.get("/api/reports", headers=researcher[1]).get_json()
        assert public["total"] == 1 and "metrics" not in public["items"][0]
        assert client.get(f"/api/reports/{report['id']}", headers=researcher[1]).status_code == 200

    def test_ranking_snapshot_and_validation(self, client, admin):
        ranking = client.post(
            "/api/admin/reports", json={**self.BODY, "kind": "ranking"}, headers=admin[1]
        ).get_json()["report"]
        assert set(ranking["metrics"]) == {"users", "semilleros"}
        bad_period = {**self.BODY, "period_start": "2026-05-01"}
        assert client.post("/api/admin/reports", json=bad_period, headers=admin[1]).status_code == 400
        bad_kind = {**self.BODY, "kind": "otro"}
        assert client.post("/api/admin/reports", json=bad_kind, headers=admin[1]).status_code == 400
        listing = client.get("/api/admin/reports?kind=ranking", headers=admin[1]).get_json()
        assert listing["total"] == 1


# --- Perfil -----------------------------------------------------------------------
class TestProfileDetails:
    def test_bio_photo_and_orcid(self, client, researcher):
        body = {"bio": "Investigo IA.", "orcid": "0000-0002-1825-009x",
                "photo": "https://example.com/yo.png"}
        profile = client.patch("/api/profile", json=body, headers=researcher[1]).get_json()["profile"]
        assert profile["bio"] == "Investigo IA."
        assert profile["orcid"] == "0000-0002-1825-009X"
        assert profile["photo"] == "https://example.com/yo.png"
        again = client.get("/api/profile", headers=researcher[1]).get_json()["profile"]
        assert again["orcid"] == "0000-0002-1825-009X"

    @pytest.mark.parametrize(
        "body",
        [{"orcid": "123"}, {"photo": "javascript:alert(1)"}, {"bio": "x" * 2001}],
    )
    def test_rejects_invalid_values(self, client, researcher, body):
        assert client.patch("/api/profile", json=body, headers=researcher[1]).status_code == 400

    def test_clearing_fields(self, client, researcher):
        client.patch("/api/profile", json={"bio": "Algo"}, headers=researcher[1])
        cleared = client.patch("/api/profile", json={"bio": ""}, headers=researcher[1]).get_json()["profile"]
        assert cleared["bio"] is None


# --- Seed demo coherente con el modelo -------------------------------------------
class TestSeedConsistency:
    @pytest.fixture(autouse=True)
    def _seed(self, app):
        result = app.test_cli_runner().invoke(args=["seed-demo"])
        assert result.exit_code == 0, result.output

    def _scalar(self, sql: str):
        return db.session.execute(db.text(sql)).scalar()

    def test_user_progress_matches_ledger(self):
        mismatches = self._scalar(
            """
            SELECT COUNT(*) FROM user_progress p
            WHERE p.xp <> (SELECT COALESCE(SUM(amount), 0) FROM xp_ledger WHERE user_id = p.user_id)
            """
        )
        assert mismatches == 0
        assert self._scalar("SELECT COUNT(*) FROM xp_ledger") == self._scalar(
            "SELECT COUNT(*) FROM achievements WHERE status = 'approved'"
        )

    def test_semillero_progress_matches_credited_ledger(self):
        mismatches = self._scalar(
            """
            SELECT COUNT(*) FROM semillero_progress sp
            WHERE sp.xp <> (
                SELECT COALESCE(SUM(l.amount), 0) FROM xp_ledger l
                JOIN achievements a ON a.id = l.achievement_id
                WHERE a.xp_semillero_id = sp.semillero_id
            )
            """
        )
        assert mismatches == 0
        assert self._scalar("SELECT COUNT(*) FROM semillero_progress") == self._scalar(
            "SELECT COUNT(*) FROM semilleros"
        )

    def test_every_semillero_has_its_leader_as_active_member(self):
        orphans = self._scalar(
            """
            SELECT COUNT(*) FROM semilleros s WHERE NOT EXISTS (
                SELECT 1 FROM semillero_members m
                WHERE m.semillero_id = s.id AND m.user_id = s.leader_id
                  AND m.role = 'leader' AND m.status = 'active'
            )
            """
        )
        assert orphans == 0

    def test_every_project_has_one_principal(self):
        bad = self._scalar(
            """
            SELECT COUNT(*) FROM projects p
            WHERE (SELECT COUNT(*) FROM project_members m
                   WHERE m.project_id = p.id AND m.role = 'principal') <> 1
            """
        )
        assert bad == 0

    def test_new_domains_are_populated(self):
        assert self._scalar("SELECT COUNT(*) FROM comments") > 0
        assert self._scalar("SELECT COUNT(*) FROM post_shares") > 0
        assert self._scalar("SELECT COUNT(*) FROM semillero_follows") > 0
        assert self._scalar("SELECT COUNT(*) FROM user_profiles") > 0
        assert self._scalar("SELECT COUNT(*) FROM semillero_members WHERE status = 'pending'") > 0
        assert self._scalar("SELECT COUNT(*) FROM calls") > 0
        assert self._scalar("SELECT COUNT(*) FROM call_applications") > 0
        assert self._scalar("SELECT COUNT(*) FROM achievements WHERE status = 'pending'") > 0
        assert self._scalar("SELECT COUNT(*) FROM report_snapshots WHERE published_at IS NOT NULL") == 1

    def test_seed_is_repeatable(self, app):
        before = self._scalar("SELECT COUNT(*) FROM achievements")
        result = app.test_cli_runner().invoke(args=["seed-demo"])
        assert result.exit_code == 0, result.output
        assert self._scalar("SELECT COUNT(*) FROM achievements") == before
        assert self._scalar("SELECT COUNT(*) FROM levels") == 20

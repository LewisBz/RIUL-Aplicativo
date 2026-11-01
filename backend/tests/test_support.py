from app.models import Notification, ROLE_ADMINISTRATOR, ROLE_RESEARCHER

VALID = {
    "category": "technical_bug",
    "subject": "Error al subir archivo",
    "message": "Al adjuntar un PDF el feed devuelve un error inesperado.",
}


def test_create_ticket_requires_auth(client):
    assert client.post("/api/support/tickets", json=VALID).status_code == 401


def test_create_and_list_my_tickets(client, make_role_user):
    _, headers = make_role_user(ROLE_RESEARCHER)
    created = client.post("/api/support/tickets", json=VALID, headers=headers)
    assert created.status_code == 201
    assert created.get_json()["ticket"]["status"] == "open"
    listed = client.get("/api/support/tickets", headers=headers)
    assert listed.status_code == 200
    assert listed.get_json()["total"] == 1


def test_users_only_see_their_tickets(client, make_role_user):
    _, first = make_role_user(ROLE_RESEARCHER)
    _, second = make_role_user(ROLE_RESEARCHER)
    client.post("/api/support/tickets", json=VALID, headers=first)
    assert client.get("/api/support/tickets", headers=second).get_json()["total"] == 0


def test_rejects_invalid_ticket(client, make_role_user):
    _, headers = make_role_user(ROLE_RESEARCHER)
    bad_category = client.post(
        "/api/support/tickets", json={**VALID, "category": "x"}, headers=headers
    )
    short_message = client.post(
        "/api/support/tickets", json={**VALID, "message": "corto"}, headers=headers
    )
    assert bad_category.status_code == 400
    assert short_message.status_code == 400


def test_admin_endpoints_reject_researcher(client, make_role_user):
    _, headers = make_role_user(ROLE_RESEARCHER)
    assert client.get("/api/admin/support/tickets", headers=headers).status_code == 403
    assert (
        client.patch(
            "/api/admin/support/tickets/1", json={"status": "resolved"}, headers=headers
        ).status_code
        == 403
    )


def test_admin_lists_and_replies(client, make_role_user, app):
    user, user_headers = make_role_user(ROLE_RESEARCHER)
    _, admin_headers = make_role_user(ROLE_ADMINISTRATOR)
    ticket_id = client.post(
        "/api/support/tickets", json=VALID, headers=user_headers
    ).get_json()["ticket"]["id"]

    listed = client.get("/api/admin/support/tickets?status=open", headers=admin_headers)
    assert listed.status_code == 200
    assert listed.get_json()["items"][0]["user"]["email"] == user.email

    replied = client.patch(
        f"/api/admin/support/tickets/{ticket_id}",
        json={"reply": "Estamos revisando el problema."},
        headers=admin_headers,
    )
    assert replied.status_code == 200
    body = replied.get_json()["ticket"]
    assert body["status"] == "in_progress"
    assert body["admin_reply"] == "Estamos revisando el problema."
    assert Notification.query.filter_by(user_id=user.id).count() == 1

    resolved = client.patch(
        f"/api/admin/support/tickets/{ticket_id}",
        json={"status": "resolved"},
        headers=admin_headers,
    )
    assert resolved.get_json()["ticket"]["status"] == "resolved"


def test_admin_reply_validation_and_not_found(client, make_role_user):
    _, admin_headers = make_role_user(ROLE_ADMINISTRATOR)
    assert (
        client.patch("/api/admin/support/tickets/999", json={"reply": "hola"}, headers=admin_headers).status_code
        == 404
    )
    assert (
        client.patch("/api/admin/support/tickets/999", json={}, headers=admin_headers).status_code
        in (400, 404)
    )
    assert (
        client.get("/api/admin/support/tickets?status=bad", headers=admin_headers).status_code
        == 400
    )

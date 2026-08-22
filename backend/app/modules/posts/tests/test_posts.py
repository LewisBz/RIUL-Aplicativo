import io


def _png():
    return io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"0" * 32)


def _pdf():
    return io.BytesIO(b"%PDF-1.4\n%fake-test-pdf\n")


class TestCreatePost:
    def test_create_text_post_returns_201(self, client, make_user, make_headers):
        _, auth = make_user()
        response = client.post(
            "/api/posts",
            data={"category": "article", "content": "Primer avance del semillero."},
            headers=make_headers(auth["access_token"]),
            content_type="multipart/form-data",
        )
        assert response.status_code == 201
        post = response.get_json()["post"]
        assert post["category"] == "article"
        assert post["content"] == "Primer avance del semillero."
        assert post["author"]["full_name"] == "Investigador de Prueba"
        assert post["attachments"] == []
        assert post["reaction_count"] == 0

    def test_create_requires_auth(self, client):
        response = client.post(
            "/api/posts",
            data={"content": "anónimo"},
            content_type="multipart/form-data",
        )
        assert response.status_code == 401

    def test_create_defaults_to_community_category(self, client, make_user, make_headers):
        _, auth = make_user()
        response = client.post(
            "/api/posts",
            data={"content": "Hola comunidad"},
            headers=make_headers(auth["access_token"]),
            content_type="multipart/form-data",
        )
        assert response.status_code == 201
        assert response.get_json()["post"]["category"] == "community"

    def test_create_rejects_invalid_category(self, client, make_user, make_headers):
        _, auth = make_user()
        response = client.post(
            "/api/posts",
            data={"category": "chisme", "content": "texto"},
            headers=make_headers(auth["access_token"]),
            content_type="multipart/form-data",
        )
        assert response.status_code == 400

    def test_create_requires_content_link_or_file(self, client, make_user, make_headers):
        _, auth = make_user()
        response = client.post(
            "/api/posts",
            data={"category": "event"},
            headers=make_headers(auth["access_token"]),
            content_type="multipart/form-data",
        )
        assert response.status_code == 400
        assert "requiere" in response.get_json()["message"]

    def test_create_with_image_upload(self, client, make_user, make_headers):
        _, auth = make_user()
        response = client.post(
            "/api/posts",
            data={
                "content": "Resultados con gráfica",
                "file": (_png(), "captura.png", "image/png"),
            },
            headers=make_headers(auth["access_token"]),
            content_type="multipart/form-data",
        )
        assert response.status_code == 201
        attachment = response.get_json()["post"]["attachments"][0]
        assert attachment["kind"] == "image"
        assert attachment["file_name"] == "captura.png"
        assert attachment["url"].startswith("/api/posts/files/")

        served = client.get(attachment["url"])
        assert served.status_code == 200
        assert served.data == _png().getvalue()

    def test_create_with_document_upload(self, client, make_user, make_headers):
        _, auth = make_user()
        response = client.post(
            "/api/posts",
            data={"content": "Acta", "file": (_pdf(), "Acta_Reunion.pdf", "application/pdf")},
            headers=make_headers(auth["access_token"]),
            content_type="multipart/form-data",
        )
        assert response.status_code == 201
        attachment = response.get_json()["post"]["attachments"][0]
        assert attachment["kind"] == "file"

    def test_create_rejects_disallowed_extension(self, client, make_user, make_headers):
        _, auth = make_user()
        response = client.post(
            "/api/posts",
            data={"content": "maligno", "file": (io.BytesIO(b"MZ"), "virus.exe", "application/x-msdownload")},
            headers=make_headers(auth["access_token"]),
            content_type="multipart/form-data",
        )
        assert response.status_code == 400

    def test_link_only_post_is_valid(self, client, make_user, make_headers):
        _, auth = make_user()
        ok = client.post(
            "/api/posts",
            data={"link_url": "https://revistas.org/articulo-1"},
            headers=make_headers(auth["access_token"]),
            content_type="multipart/form-data",
        )
        assert ok.status_code == 201
        bad = client.post(
            "/api/posts",
            data={"link_url": "javascript:alert(1)"},
            headers=make_headers(auth["access_token"]),
            content_type="multipart/form-data",
        )
        assert bad.status_code == 400


class TestListPosts:
    def test_feed_requires_auth(self, client):
        assert client.get("/api/posts").status_code == 401

    def test_list_ordered_newest_first(self, client, make_user, make_headers):
        _, auth = make_user()
        headers = make_headers(auth["access_token"])
        created_ids = []
        for index in range(3):
            response = client.post(
                "/api/posts",
                data={"content": f"publicación {index}"},
                headers=headers,
                content_type="multipart/form-data",
            )
            created_ids.append(response.get_json()["post"]["id"])
        feed = client.get("/api/posts", headers=headers).get_json()
        assert feed["total"] == 3
        assert [item["id"] for item in feed["items"]] == sorted(created_ids, reverse=True)

    def test_category_filter(self, client, make_user, make_headers):
        _, auth = make_user()
        headers = make_headers(auth["access_token"])
        for category in ("article", "community"):
            client.post(
                "/api/posts",
                data={"category": category, "content": f"sobre {category}"},
                headers=headers,
                content_type="multipart/form-data",
            )
        feed = client.get("/api/posts?category=community", headers=headers).get_json()
        assert feed["total"] == 1
        assert feed["items"][0]["category"] == "community"

    def test_filter_rejects_invalid_category(self, client, make_user, make_headers):
        _, auth = make_user()
        response = client.get(
            "/api/posts?category=inexistente",
            headers=make_headers(auth["access_token"]),
        )
        assert response.status_code == 400


class TestReactions:
    def test_toggle_add_and_remove(self, client, make_user, make_headers):
        _, auth = make_user()
        headers = make_headers(auth["access_token"])
        post_id = client.post(
            "/api/posts",
            data={"content": "con reacciones"},
            headers=headers,
            content_type="multipart/form-data",
        ).get_json()["post"]["id"]

        first = client.post(f"/api/posts/{post_id}/reactions", headers=headers)
        assert first.status_code == 200
        assert first.get_json() == {"reaction_count": 1, "reacted_by_me": True}

        second = client.post(f"/api/posts/{post_id}/reactions", headers=headers)
        assert second.get_json() == {"reaction_count": 0, "reacted_by_me": False}

    def test_reactions_count_across_users(self, client, make_user, make_headers):
        _, author_auth = make_user()
        _, other_auth = make_user()
        author_headers = make_headers(author_auth["access_token"])
        other_headers = make_headers(other_auth["access_token"])
        post_id = client.post(
            "/api/posts",
            data={"content": "popular"},
            headers=author_headers,
            content_type="multipart/form-data",
        ).get_json()["post"]["id"]

        client.post(f"/api/posts/{post_id}/reactions", headers=author_headers)
        client.post(f"/api/posts/{post_id}/reactions", headers=other_headers)
        detail = client.get("/api/posts", headers=other_headers).get_json()["items"][0]
        assert detail["reaction_count"] == 2
        assert detail["reacted_by_me"] is True

        feed_for_author = client.get("/api/posts", headers=author_headers).get_json()["items"][0]
        assert feed_for_author["reacted_by_me"] is True

    def test_reaction_on_missing_post_returns_404(self, client, make_user, make_headers):
        _, auth = make_user()
        response = client.post("/api/posts/999/reactions", headers=make_headers(auth["access_token"]))
        assert response.status_code == 404


class TestDeletePost:
    def test_author_can_delete_and_file_removed(self, client, make_user, make_headers, uploads_root):
        _, auth = make_user()
        headers = make_headers(auth["access_token"])
        created = client.post(
            "/api/posts",
            data={"content": "borrable", "file": (_png(), "foto.png", "image/png")},
            headers=headers,
            content_type="multipart/form-data",
        ).get_json()["post"]

        response = client.delete(f"/api/posts/{created['id']}", headers=headers)
        assert response.status_code == 204

        feed = client.get("/api/posts", headers=headers).get_json()
        assert feed["total"] == 0
        import os

        assert os.listdir(os.path.join(uploads_root, "posts")) == []

    def test_non_author_cannot_delete(self, client, make_user, make_headers):
        _, author_auth = make_user()
        _, other_auth = make_user()
        post_id = client.post(
            "/api/posts",
            data={"content": "ajeno"},
            headers=make_headers(author_auth["access_token"]),
            content_type="multipart/form-data",
        ).get_json()["post"]["id"]
        response = client.delete(
            f"/api/posts/{post_id}",
            headers=make_headers(other_auth["access_token"]),
        )
        assert response.status_code == 403

    def test_delete_missing_post_returns_404(self, client, make_user, make_headers):
        _, auth = make_user()
        response = client.delete("/api/posts/999", headers=make_headers(auth["access_token"]))
        assert response.status_code == 404

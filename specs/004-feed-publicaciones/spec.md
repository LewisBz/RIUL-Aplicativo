# Feature 004: Feed de Publicaciones (Comunidad)

**Branch**: `004-feed-publicaciones` | **Base**: `develop`
**Constitution**: v1.1.0 | **Priority**: P1 (first authenticated social module)
**Mockup**: `mockup/stitch_riul_design_system_strategy/riul_feed_de_publicaciones/`

## Purpose

First module of the authenticated app area. Reproduces the "RIUL - Comunidad"
mockup: app shell (TopNav + SideBar with researcher profile card and
"Comunidad" active item), create-post box, category filter chips, and a two-
column feed grid of post cards (author, relative time, category badge, text,
link, attachment, Reacciones/Comentarios/Compartir actions).

Scope decisions (agreed 2026-08-22):

- Real file uploads (multipart) stored in a container volume; no URL-pasting.
- Comments deferred to a later feature; the "Comentarios" button renders inert.
- Frontend page name: `frontend/feed.html`.
- The per-card `more_horiz` menu only appears on your own posts → delete.

## API Contract (defined before implementation — Principle II)

All endpoints require `Authorization: Bearer <token>` except file serving.

| Method | Endpoint | Body / Query | Success | Errors |
|---|---|---|---|---|
| GET | `/api/posts` | `?category=&page=` | `200` `{items, page, per_page, total}` ordered by `created_at DESC` | `400` invalid category · `401` |
| POST | `/api/posts` | multipart/form-data: `category`, `content`, `link_url?`, `file?` | `201` `{post}` | `400` validation · `401` · `413` >10 MB |
| DELETE | `/api/posts/<id>` | Bearer (author only) | `204` | `403` not author · `404` |
| POST | `/api/posts/<id>/reactions` | Bearer (toggle) | `200` `{reaction_count, reacted_by_me}` | `404` |
| GET | `/api/posts/files/<name>` | public | `200` file stream | `404` |

Categories (`category`): `article`, `project_advance`, `presentation`,
`event`, `community`. New posts default to `community` when created from the
feed UI (the mockup's create box has no category picker).

Post rule: at least one of `content`, `link_url`, `file` is required.

Attachment kinds derived from extension:
- `image`: png, jpg, jpeg, webp, gif
- `file`: pdf, doc, docx, ppt, pptx, xls, xlsx

Files are stored as `<uuid>.<ext>` under `UPLOAD_FOLDER/posts` and served via
the unauthenticated files endpoint (unguessable names; `<img src>` cannot send
Authorization headers). `MAX_CONTENT_LENGTH` = 10 MB.

## User Stories

### US1: Create a post with optional image/document (P0)
As an active member I want to share text with an optional link or file so the
community can follow my research activity.

- Valid category required; content/link/file at least one present
- Image or document uploaded via multipart, validated by extension and size
- Response returns the serialized post including author, attachment URL,
  reaction count

### US2: Browse the feed with category filters (P0)
As a member I want to open `feed.html` and see recent posts in a responsive
grid, filtering by category chips like in the mockup.

- Pagination `page` (10 per page), newest first
- Category filter validated server-side; empty feed shows a friendly state
- All user-generated strings are HTML-escaped client-side (XSS)

### US3: React to posts (P1)
As a member I want to toggle a reaction on any post.

- One reaction per user per post (unique constraint); toggling removes it
- Response returns authoritative count + `reacted_by_me`

### US4: Delete own posts (P2)
As the author I want to delete my post via the card menu; other users must not
see the menu nor be able to delete.

- Author check server-side (Principle VII); physical attachment file removed

## Data Model

- `posts`: id PK, author_id FK→users NOT NULL, category String(30) NOT NULL
  default `community`, content Text nullable, link_url String(500) nullable,
  created_at server_default now()
- `post_attachments`: id PK, post_id FK→posts NOT NULL, kind String(10) NOT
  NULL (`image`|`file`), file_name String(255) NOT NULL (original),
  storage_name String(120) NOT NULL unique, mime_type String(100) nullable,
  file_size Integer nullable. Max one attachment per post (service-level).
- `post_reactions`: id PK, post_id FK→posts NOT NULL, user_id FK→users NOT
  NULL, created_at; UNIQUE(post_id, user_id). Cascading deletes from posts.

## Non-Functional Requirements

- NFR1: Module follows the established layout
  `app/modules/posts/{models,services,routes,tests}` with `ServiceError`
  handling and blueprint registration in `create_app` (Principle I)
- NFR2: Alembic migration `0002_posts_module_tables` chained after 0001;
  tests run against real PostgreSQL `riul_test` (NFR auth parity)
- NFR3: Uploads volume persisted via compose (`uploads_data:/app/uploads`);
  `UPLOAD_FOLDER` configurable by env var
- NFR4: `feed.html` uses ONLY `css/design-system.css` (new section 16 "Feed
  Components") + vanilla ES module `js/feed.js`; token from
  `localStorage('riul_token')`; no Tailwind (Principle III)
- NFR5: Post-login redirect target becomes `feed.html`

## Edge Cases

- POST without any of content/link/file → `400`
- Unknown category on filter or create → `400`
- Oversized upload → Flask `MAX_CONTENT_LENGTH` → `413` handled as JSON
- Delete by non-author → `403`; nonexistent post → `404`
- Expired token on any endpoint → `401` JSON (global JWT handlers)

## Out of Scope

Comments (deferred feature), post editing, avatar uploads (initials fallback),
gamification hooks, notifications, infinite scroll (page param only),
moderation/admin actions, rich text formatting.

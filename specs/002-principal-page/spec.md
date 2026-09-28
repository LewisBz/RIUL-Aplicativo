# Feature Specification: Public Landing Page from Principal Mockup

**Feature Branch**: `002-principal-page`

**Created**: 2026-08-22

**Status**: Draft

**Input**: User description: "Generar el primer módulo, es decir página principal, con base al mockup riul_p_gina_principal y usando el CSS centralizado ubicado en frontend/."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Landing page faithful to mockup with centralized CSS (Priority: P1)

A visitor opens `frontend/index.html` and sees the public RIUL landing page
reproducing `mockup/stitch_riul_design_system_strategy/riul_p_gina_principal/code.html`
section by section: sticky top navigation (brand + Semilleros/Proyectos/Eventos +
Iniciar sesión/Registrarse actions), hero with abstract background at 20% opacity,
bento grid (featured seedbeds span-8 + recent projects span-4), upcoming-events
carousel, "Descubrir Más" section, and institutional footer — styled exclusively by
`frontend/css/design-system.css` with zero Tailwind usage.

**Why this priority**: It is the first real module of the application and the public
entry point that routes visitors to `/login` and `/register`.

**Independent Test**: Can be fully tested by opening `index.html` standalone in a
browser and visually comparing each section against the mockup screenshot.

**Acceptance Scenarios**:

1. **Given** `index.html` opened standalone (file:// or static server), **When**
   compared against the mockup, **Then** every section's layout, colors, typography
   scale, spacing rhythm, and component states match.
2. **Given** the page source, **When** inspected, **Then** there are no Tailwind CDN
   scripts, no inline `tailwind.config`, and no framework references; only the single
   stylesheet link and Google Fonts loaded by it.
3. **Given** a viewport narrower than 768px, **When** the page renders, **Then** the
   bento grid stacks to one column and margins reduce per the design system.

---

### User Story 2 - Standalone basic interactions (Priority: P2)

The mobile hamburger toggles a simple navigation menu, and the carousel chevron
buttons scroll the events track left/right, using a small vanilla ES module
(`frontend/js/main.js`) with no libraries.

**Why this priority**: The mockup renders these affordances as inert decorations; the
real page must respond, but they are enhancements on top of US1.

**Independent Test**: Can be tested by clicking the hamburger below 768px width and
the chevron buttons at any width, observing menu visibility toggle and horizontal
scroll movement.

**Acceptance Scenarios**:

1. **Given** a viewport < 768px, **When** the hamburger button is clicked, **Then**
   the nav links become visible/collapsed.
2. **Given** more event cards than fit the viewport, **When** either chevron is
   clicked, **Then** the track scrolls smoothly by one card width in that direction.

---

## Requirements

- Section order, copy text, sample data (Semillero 1/2, Proyectos 1–3 with states
  "Fase de desarrollo"/"Publicado"/"En revisión", Eventos 15 Oct & 22 Nov 2026),
  and image URLs are taken verbatim from the mockup.
- Remote Stitch placeholder image URLs are used as-is (accepted tradeoff: require
  internet); they are replaced later when real media exists.
- Links point to canonical routes `/login` and `/register`; other nav/footer anchors
  stay `#` until their modules exist (they will 404 or stay inert meanwhile).
- New landing styles MUST be added to `design-system.css` (single source of truth)
  as token-only classes: `.topnav-brand`, `.nav-link`, `.btn-outline`, `.hero`,
  `.hero-bg`, `.hero-content`, `.card-hover`, `.line-clamp-3`, `.section-header`,
  `.list-row`, `.carousel-track`, `.carousel-card`, `.carousel-arrow`,
  `.hide-scrollbar`, `.progress-mini`, `.check-list`, `.media-overlay`.
- Data is hardcoded HTML for now; wiring to REST endpoints happens in the backend
  modules feature (API-first principle II).

## Edge Cases

- What happens offline? → Fonts/icons degrade to system fallbacks; layout intact;
  remote images show empty containers (acceptable until local assets exist).
- What happens with no JS? → Menu stays hidden on mobile (links remain reachable via
  footer/topnav desktop layout); carousel remains natively swipe-scrollable.
- What happens on ultra-wide screens? → Content constrained to 1280px container.

## Constraints

- Zero build step; vanilla HTML/CSS/JS served as authored (constitution III).
- One JS file maximum for this module (~25 lines).

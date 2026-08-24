# Feature Specification: Centralized Design System from RIUL Mockups

**Feature Branch**: `001-design-system`

**Created**: 2026-08-22

**Status**: Draft

**Input**: User description: "Generar un único archivo que centralice el style de la aplicación (CSS) a partir de los mockups de la carpeta mockup/, ubicado en una carpeta frontend/, junto con una página styleguide.html de demostración."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Single stylesheet with all tokens and components (Priority: P1)

A developer building any RIUL view links one stylesheet
(`frontend/css/design-system.css`) from an HTML page and, without any build step,
obtains: the complete color/typography/spacing/radius/shadow token set as CSS custom
properties, base reset styles, semantic typography utility classes, and reusable
component classes matching the recurring visual patterns of the 19 Stitch mockups.

**Why this priority**: Every future screen depends on this foundation; without it each
view would re-invent styles (the exact problem the mockups have today — Tailwind CDN +
duplicated inline config in all 19 files).

**Independent Test**: Can be fully tested by opening any HTML page that links only
`design-system.css` and confirming tokens/components render correctly. Delivers value
immediately: new views stop depending on Tailwind CDN.

**Acceptance Scenarios**:

1. **Given** an HTML page that links `../frontend/css/design-system.css` via relative
   path, **When** it renders offline (no Tailwind), **Then** colors, typography,
   spacing, radii, shadows and component classes resolve from CSS custom properties.
2. **Given** two different views use `.glass-card` or `.btn-primary`, **When** compared
   side by side, **Then** they look pixel-identical (single source of truth).
3. **Given** the stylesheet, **When** inspected, **Then** it contains zero references to
   frameworks, bundlers, or preprocessors and works served exactly as authored.

---

### User Story 2 - Styleguide demo page for visual validation (Priority: P2)

A designer or developer opens `frontend/styleguide.html` in a browser and sees every
design token (color swatches, type scale, spacing scale) and every component (buttons,
inputs, state pills, cards, XP bar, tables, timeline, shell) rendered live, so the page
can be validated visually against the Stitch mockups before building real views.

**Why this priority**: It is the acceptance instrument for US1 and becomes the living
reference the whole team checks against mockups.

**Independent Test**: Can be fully tested by opening `styleguide.html` standalone in a
browser (file:// or static server) with no other assets than the single CSS file.

**Acceptance Scenarios**:

1. **Given** `styleguide.html` opened in any modern browser, **When** scrolled, **Then**
   every token group and every component defined in the stylesheet is visible and
   labelled.
2. **Given** the styleguide is compared against `mockup/stitch_riul_design_system_strategy/riul_academic_evolution/DESIGN.md`,
   **When** checking primary color, fonts, and spacing rhythm, **Then** they match the
   documented design system.

---

## Requirements

### Canonical decisions (resolving mockup inconsistencies)

- Accent gold is canonized as `#ffb800` (`--accent-gold`). Variants found in mockups
  (`#FFC107`, `#fbbc04`) are NOT used.
- Borders use official DESIGN.md tokens (`--outline-variant #e0bfbf`,
  `--outline #8c7071`); the stray `#e0e0e0` seen in some mockups is dropped.
- Light theme only (mockups configure dark mode but never use it; YAGNI per
  constitution). Token naming keeps Material 3 conventions so dark values can be added
  later without renaming.

### Token requirements

- All ~40 Material 3 color tokens from `DESIGN.md` frontmatter exposed as custom
  properties (`--primary`, `--primary-container`, `--tertiary`, `--surface-*`,
  `--error`, etc.), including `--accent-gold`.
- Typography: Montserrat (600/700) for display/headline + `numeric-xp`; Inter
  (400/600/700) for body/title/label; loaded via Google Fonts with system fallbacks;
  scale classes: display-lg, headline-lg/md, title-lg, body-lg/md, label-caps,
  numeric-xp.
- Spacing on 4px rhythm: unit-1(4px)…unit-12(48px), gutter 24px, container max 1280px,
  margin-mobile 16px.
- Radii: sm 4px, md 8px (controls), lg 16px (large containers), pill.
- Shadows: ambient `0 4px 20px rgba(0,0,0,.05)`; gamified `rgba(255,184,0,.1)` tint;
  XP bar inner glow.

### Component class requirements (extracted from the 19 mockups)

Buttons (primary crimson / secondary graphite outline / gold reward with black text /
teal tertiary), inputs & selects (8px radius, 2px crimson focus ring), `.glass-card`
(blur + translucency), research card vs achievement card (left amber border),
state pills (Activo teal / Cerrado grey / En evaluación error / Publicado green /
Pendiente amber), filter chips, tabs, zebra data table, vertical timeline, dropzone,
XP progress bar with glow, app shell (topnav h-64px + sidebar w-256px sticky +
scrollable main), institutional footer, custom scrollbar.

### Layout requirements

12-column grid helper, centered container (max 1280px, gutter 24px), responsive stack
at ≤768px to 1 column with 16px margins.

### Compliance

- Zero build step: plain CSS, ES-servable as-is (constitution principle III).
- External dependencies limited to Google Fonts + Material Symbols (CDN `<link>`, no JS).

## Edge Cases

- What happens when Google Fonts/Material Symbols fail to load? → System font stacks
  (`sans-serif` fallbacks) keep layout legible; icons degrade gracefully (ligature text
  hidden via `font-display: block` behavior).
- What happens if a view forgets to link the stylesheet? → Unstyled content; not a
  stylesheet defect but styleguide documents the single required `<link>`.
- How does the system handle very long unbroken strings in pills/badges? →
  `overflow-wrap` + `max-width` guards on chip/pill classes.

## Constraints

- Must not introduce npm packages, bundlers, preprocessors, or runtime JS.
- Class names in English (standard practice); comments minimal.
- File must remain ONE css file (user requirement).

---
name: RIUL Academic Evolution
colors:
  surface: '#f9f9f9'
  surface-dim: '#dadada'
  surface-bright: '#f9f9f9'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3f3'
  surface-container: '#eeeeee'
  surface-container-high: '#e8e8e8'
  surface-container-highest: '#e2e2e2'
  on-surface: '#1a1c1c'
  on-surface-variant: '#594141'
  inverse-surface: '#2f3131'
  inverse-on-surface: '#f1f1f1'
  outline: '#8c7071'
  outline-variant: '#e0bfbf'
  surface-tint: '#b02a3e'
  primary: '#7b001f'
  on-primary: '#ffffff'
  primary-container: '#9e1b32'
  on-primary-container: '#ffb0b3'
  inverse-primary: '#ffb3b5'
  secondary: '#5f5e5e'
  on-secondary: '#ffffff'
  secondary-container: '#e4e2e1'
  on-secondary-container: '#656464'
  tertiary: '#00423c'
  on-tertiary: '#ffffff'
  tertiary-container: '#005c53'
  on-tertiary-container: '#8ad2c6'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdada'
  primary-fixed-dim: '#ffb3b5'
  on-primary-fixed: '#40000c'
  on-primary-fixed-variant: '#8f0c28'
  secondary-fixed: '#e4e2e1'
  secondary-fixed-dim: '#c8c6c6'
  on-secondary-fixed: '#1b1c1c'
  on-secondary-fixed-variant: '#474747'
  tertiary-fixed: '#a7f0e4'
  tertiary-fixed-dim: '#8cd4c8'
  on-tertiary-fixed: '#00201c'
  on-tertiary-fixed-variant: '#005048'
  background: '#f9f9f9'
  on-background: '#1a1c1c'
  surface-variant: '#e2e2e2'
typography:
  display-lg:
    fontFamily: Montserrat
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Montserrat
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: Montserrat
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  headline-md:
    fontFamily: Montserrat
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  title-lg:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
  numeric-xp:
    fontFamily: Montserrat
    fontSize: 14px
    fontWeight: '700'
    lineHeight: 20px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  unit-1: 4px
  unit-2: 8px
  unit-4: 16px
  unit-6: 24px
  unit-8: 32px
  unit-12: 48px
  container-max: 1280px
  gutter: 24px
  margin-mobile: 16px
---

## Brand & Style

The design system is built to bridge the gap between traditional academic prestige and modern student engagement. It targets university researchers, faculty, and students involved in "Semilleros" (research seeds). 

The design style is **Corporate / Modern** with a **Tactile** twist for gamified elements. It prioritizes structure, clarity, and authority through high-quality typography and a disciplined grid, while introducing "reward-tier" micro-interactions. The interface should feel like an elite academic portal that has been enhanced with a sophisticated progression system—encouraging research output through subtle visual cues rather than loud, toy-like gamification.

## Colors

This design system utilizes a high-contrast palette to maintain institutional authority while highlighting achievements.

- **Primary (Institutional Crimson):** Used for headers, primary actions, and branding. It must maintain a minimum 4.5:1 contrast ratio against white.
- **Secondary (Graphite):** Used for navigation backgrounds, sidebars, and high-level structural components.
- **Accent (Golden Amber):** Reserved exclusively for gamification elements: XP bars, achievement badges, and ranking highlights. 
- **Neutrals:** A balanced scale of cool greys is used to differentiate between "Surface" (F5F5F5), "Border" (E0E0E0), and "Text Secondary" (757575).

## Typography

The typographic hierarchy distinguishes between *static information* and *dynamic achievement*.

- **Headlines:** Montserrat provides a bold, geometric presence that feels architectural and established. Use heavy weights (600-700) for section titles.
- **Body:** Inter is used for all functional text. Its high x-height ensures legibility in dense research abstracts and data tables.
- **Gamified Elements:** For XP counts and level indicators, use Montserrat with `label-caps` or `numeric-xp` styling to make progression feel distinct from standard metadata.

## Layout & Spacing

The design system employs a **Fixed Grid** model for desktop and a **Fluid Fluid** model for mobile devices. 

- **Grid:** Use a 12-column grid for desktop (1280px max-width) with 24px gutters. 
- **Rhythm:** All spacing must be a multiple of 4px. Use 16px (unit-4) for standard padding within cards and 24px (unit-6) for vertical spacing between logical sections.
- **Mobile Adaption:** At the 768px breakpoint, the layout shifts to a 1-column stack. Margins reduce to 16px to maximize screen real estate for reading academic content.

## Elevation & Depth

Hierarchy is established through **Tonal Layers** and **Ambient Shadows**.

- **Surface Levels:** The background is the lowest level (`neutral_color_hex`). Cards and containers sit on top using white (#FFFFFF).
- **Shadows:** Use extremely soft, blurred shadows for cards: `0px 4px 20px rgba(0, 0, 0, 0.05)`. This creates a sense of "paper" layers without appearing too heavy or dated.
- **Gamified Elevation:** Active achievement cards or "Level Up" notifications should use a slightly higher elevation with a hint of the accent color in the shadow (e.g., `rgba(255, 184, 0, 0.1)`) to draw immediate eye focus.

## Shapes

This design system uses a **Rounded** (Level 2) language. 

- **Standard Elements:** Buttons, input fields, and small cards use a 0.5rem (8px) radius.
- **Large Containers:** Modals and main content cards use a 1rem (16px) radius to soften the academic density.
- **Gamification Icons:** Badges and XP progress bars use "Pill" shapes (full radius) to contrast against the more rectangular institutional elements, signaling their interactive and "fun" nature.

## Components

### Buttons
- **Primary:** Crimson background, white text, 8px radius. Use for "Submit Research" or "Start Project."
- **Secondary:** Graphite outline or light grey fill.
- **XP/Reward Action:** Golden Amber background with black text. Use only for "Claim Reward" or "View Ranking."

### Progress Bars (XP)
- Track background: `neutral_color_hex`.
- Fill: `accent_color_hex`.
- Add a subtle 1px inner glow to the fill to make the "XP" feel like a physical liquid or energy bar.

### Cards
- **Research Card:** White background, 1px border (#E0E0E0), 8px radius. Title in Crimson.
- **Achievement Card:** Same as Research Card, but with a 2px Golden Amber left-border accent and an icon placeholder.

### Inputs & Selection
- Use 8px radius for all text fields.
- Focused state: 2px border using the Primary Crimson color.
- Checkboxes/Radios: Use the Primary Crimson for the selected state to maintain institutional branding.

### Lists
- Use "Zebra striping" for data-heavy research tables using F9F9F9 and FFFFFF to maintain horizontal tracking for the eye.
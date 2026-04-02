---
title: "Scrum UI Redesign Plan — project_scrum module"
date: 2026-04-02
type: journal
---

## Context

Module: `project_scrum` (Odoo). Covers the sprint board, agile dashboard, and chart views. Plan lives at `plans/260402-1122-scrum-ui-redesign-wireframe/`. Reference wireframe: `assets/designs/wireframe-agile-full.html`.

## What Happened

Created a 4-phase UI redesign plan (~14h total) to modernise the scrum module visuals and align them with the reference wireframe.

| # | Phase | Files | Priority | Est |
|---|-------|-------|----------|-----|
| 1 | Design tokens | `scrum-design-tokens.scss` (rewrite) | P0 | ~2h |
| 2 | Sprint board | `sprint-board.xml`, `sprint-board.scss` | P0 | ~5h |
| 3 | Dashboard | `agile-dashboard.xml`, `agile-dashboard.scss` | P1 | ~4h |
| 4 | Charts polish | `charts.scss`, `burndown-chart.xml`, `velocity-chart.xml` | P2 | ~3h |

Key design deltas planned:

- **Primary colour**: `#0052CC` (Jira blue) → `#2563EB` (enterprise blue)
- **Typography**: system font → Plus Jakarta Sans (Google Fonts)
- **Icons**: emoji → SVG Heroicons everywhere
- **Sprint card**: plain card → gradient hero (`linear-gradient 135deg, #2563EB → #1D4ED8`)
- **Board header**: plain heading → filter chips + "Create Issue" CTA
- **Border radius / depth**: 3px → 8px radius, shadows added, hover-lift effect

Tasks #8–#11 were created and hydrated. Task #8 (Phase 1) is the unblocking task; #9–#11 depend on it.

## Decisions

**Zero JS/Python changes** — all changes are XML (OWL templates / QWeb) and SCSS only. The functional logic is already correct; this is a visual-only pass. Keeping the diff narrow reduces regression risk and makes review straightforward.

**Wireframe alignment matters** — `wireframe-agile-full.html` is the agreed design contract. Every component decision (card gradient, chip layout, icon system) traces back to that file, so reviewers and future contributors have a single source of truth rather than scattered Figma comments or verbal descriptions.

**Token-first sequencing** — rewriting design tokens in Phase 1 before touching any component SCSS ensures colour, spacing, and typography variables are consistent across Phases 2–4 without duplication.

## Next

Start with **Phase 1 (task #8)** — rewrite `scrum-design-tokens.scss` with the new colour palette, Plus Jakarta Sans import, updated spacing scale, and shadow tokens. Completing this unblocks Phases 2–4 (tasks #9–#11) which can then proceed in order or partially in parallel.

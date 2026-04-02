---
title: "Project Scrum UI Redesign — Wireframe Alignment"
description: "Update all OWL templates and SCSS to match wireframe-agile-full.html design system (Plus Jakarta Sans, #2563EB primary, gradient sprint hero, SVG icons, filter chips)"
status: completed
priority: P1
effort: ~14h
branch: main
tags: [odoo, scrum, owl, scss, ui-redesign, wireframe]
created: 2026-04-02
blockedBy: []
blocks: []
---

# Project Scrum UI Redesign — Wireframe Alignment

## Overview

Update the visual design of all `project_scrum` OWL components to match
`assets/designs/wireframe-agile-full.html`. **Zero logic changes** — all
JavaScript stays the same; only templates (`.xml`) and styles (`.scss`) change.

**Reference:** `assets/designs/wireframe-agile-full.html`
**Prior plan:** `plans/260401-1000-project-scrum-owl-enhancement/` (completed)

> **Note:** Primarily XML/SCSS changes. Minimal JS touch-ups may be needed
> (e.g. badge class aliases, stub handlers). Chart.js config and OWL state
> logic stay untouched.

## What Changes (Design Delta)

| Area | Current | Target |
|------|---------|--------|
| Primary color | `#0052CC` (Jira blue) | `#2563EB` (enterprise blue) |
| Font | System font stack | Plus Jakarta Sans |
| Sprint board columns | `#F4F5F7` flat | `#F1F5F9` with proper radius, header badge |
| Task cards | 3px radius, gray border | 8px radius, shadow, hover lift |
| Type icons | Emoji | SVG (Heroicons inline) |
| Blocked indicator | Emoji + text | Red left border + `blocked-badge` chip |
| Board header | Select + stats | Filter chips + "Create Issue" CTA |
| Sprint hero (Dashboard) | Plain card | Gradient `linear-gradient(135deg, #2563EB, #1D4ED8)` |
| Widget headers | Emoji + text | SVG icon + proper type scale |
| Column add button | None | `+ Create Issue` dashed button |
| Chart wrapper | Plain border | Wireframe `stat-card` style + tab bar |

## What Does NOT Change

- OWL JS logic (drag-drop, RPC, state management) — minor class-name updates only
- Chart.js configuration and data pipelines
- Python models / controllers
- XML views / menus
- Tests
- Odoo chrome (navigation, topbar) — Odoo provides its own shell

## Phase Summary

| Phase | Scope | Files | Effort | Status |
|-------|-------|-------|--------|--------|
| [Phase 1](phase-01-design-tokens.md) | Update SCSS design tokens to wireframe system | `scrum-design-tokens.scss` | ~2h | Completed |
| [Phase 2](phase-02-sprint-board-redesign.md) | Sprint Board XML + SCSS redesign | `sprint-board.xml`, `sprint-board.scss` | ~5h | Completed |
| [Phase 3](phase-03-dashboard-redesign.md) | Agile Dashboard XML + SCSS redesign | `agile-dashboard.xml`, `agile-dashboard.scss` | ~4h | Completed |
| [Phase 4](phase-04-charts-redesign.md) | Charts SCSS update + XML polish | `charts.scss`, `burndown-chart.xml`, `velocity-chart.xml` | ~3h | Completed |

## Key Files

```
addons/project_scrum/static/src/
├── scss/
│   ├── scrum-design-tokens.scss   ← Phase 1
│   ├── sprint-board.scss          ← Phase 2
│   ├── agile-dashboard.scss       ← Phase 3
│   └── charts.scss                ← Phase 4
└── xml/
    ├── sprint-board.xml           ← Phase 2
    ├── agile-dashboard.xml        ← Phase 3
    ├── burndown-chart.xml         ← Phase 4
    └── velocity-chart.xml         ← Phase 4
```

## Design System Reference

From `wireframe-agile-full.html` `:root`:

```css
--primary:       #2563EB;
--primary-light: #3B82F6;
--accent:        #F97316;
--bg:            #F8FAFC;
--surface:       #FFFFFF;
--text:          #1E293B;
--text-sec:      #64748B;
--border:        #E2E8F0;
--nav-dark:      #0F172A;
--status-done:   #10B981;
--status-inprog: #3B82F6;
--status-review: #8B5CF6;
--status-test:   #F59E0B;
--status-todo:   #94A3B8;
--radius-card:   12px;
--radius-btn:    8px;
--shadow-card:   0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.06);
--shadow-hover:  0 4px 12px rgba(0,0,0,.12), 0 2px 6px rgba(0,0,0,.08);
```

Font: `Plus Jakarta Sans` (Google Fonts, weights 300–800)

## Success Criteria

- [x] All OWL components use `#2563EB` primary and Plus Jakarta Sans font
- [x] Sprint board columns visually match wireframe Screen 3
- [x] Task cards: 8px radius, shadow, hover lift, SVG type icons, no emojis
- [x] Blocked tasks: red left border + `blocked-badge` chip (no emoji)
- [x] Board header: filter chips + "Create Issue" button
- [x] Dashboard sprint widget: gradient hero background, white text
- [x] Dashboard widget headers: SVG icons, no emojis
- [x] All chart wrappers use wireframe card style
- [x] No emojis used anywhere in templates
- [x] All `cursor: pointer` on clickable elements
- [x] Smooth transitions on hover states (150–300ms)
- [x] Responsive: columns scroll on mobile

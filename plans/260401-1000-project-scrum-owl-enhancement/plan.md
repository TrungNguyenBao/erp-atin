---
title: "Project Scrum OWL Enhancement & Completion"
description: "OWL Sprint Board, Charts, Dashboard, Ceremony model, Security roles, Tests for project_scrum addon"
status: completed
priority: P1
effort: 42h
branch: main
tags: [odoo, scrum, owl, chart.js, testing, project-management]
created: 2026-04-01
blockedBy: []
blocks: []
---

# Project Scrum OWL Enhancement & Completion

## Overview

Extend the existing `project_scrum` addon (v18.0.4.0.0) with interactive OWL components, dedicated Scrum Ceremony model, enhanced Scrum security roles, Sprint PDF report, and full test coverage.

**Module:** `addons/project_scrum/`
**Depends:** `project`, `mail`, `web`
**Prior plan:** [260318-0906 (completed)](../260318-0906-project-scrum-agile-module/plan.md)

## Current State (What Exists)

| Feature | Status |
|---------|--------|
| Sprint lifecycle (draft/active/closed) | Done |
| Story points, task extension | Done |
| Epic & Release models | Done |
| Product Backlog view | Done |
| Burndown/Velocity SQL reports | Done |
| Sprint Planning/Close wizards | Done |
| Security (user/manager groups) | Done |
| Review/Retro text fields on Sprint | Done |
| Daily standup view | Done |
| Cron daily snapshot | Done |

## Gaps (What This Plan Delivers)

| Gap | Phase | Priority |
|-----|-------|----------|
| UI/UX wireframes for all OWL components | Phase 2 | P0 |
| OWL Sprint Board with drag-drop | Phase 3 | P0 |
| OWL Burndown Chart (Chart.js) | Phase 4 | P0 |
| OWL Velocity Chart (Chart.js) | Phase 4 | P1 |
| OWL Agile Dashboard | Phase 5 | P1 |
| Scrum Ceremony model | Phase 1 | P1 |
| Scrum Master/PO security groups | Phase 1 | P1 |
| Missing task fields (acceptance_criteria, task_type) | Phase 1 | P2 |
| Sprint PDF report | Phase 1 | P2 |
| Unit & integration tests | Phase 6 | P1 |

## Phase Summary

| Phase | Scope | Effort | Status |
|-------|-------|--------|--------|
| [Phase 1](phase-01-ceremony-model-and-security.md) | Ceremony model, Scrum roles, task fields, PDF report | ~6h | Completed |
| [Phase 2](phase-02-wireframe-ui-ux-design.md) | Wireframe & UI/UX design for all OWL components | ~4h | Completed |
| [Phase 3](phase-03-owl-sprint-board.md) | Sprint Board OWL component with drag-drop | ~10h | Completed |
| [Phase 4](phase-04-owl-charts-burndown-velocity.md) | Burndown + Velocity Chart.js OWL widgets | ~8h | Completed |
| [Phase 5](phase-05-owl-agile-dashboard.md) | Agile Dashboard OWL + Backlog Panel | ~6h | Completed |
| [Phase 6](phase-06-testing-and-polish.md) | Unit tests, integration tests, perf optimization | ~8h | Completed |

## Key Architecture Decisions

1. **OWL components register as client actions** -- Sprint Board and Dashboard are standalone OWL views, not inherited kanban. Accessed via menu actions.
2. **Chart.js via OWL** -- Follow Odoo 18 pattern (`project/static/src/views/burndown_chart/`). Import Chart.js from `web.libs`, render in `onMounted`.
3. **Ceremony as dedicated model** -- `scrum.ceremony` with type selection, attendees, meeting notes. Replaces text fields on sprint (kept for backward compat).
4. **Three security groups** -- Scrum User (view), Scrum Master (manage sprints/ceremonies), Product Owner (manage backlog/epics). Inherit from project groups.
5. **Drag-drop via Sortable.js** -- Already bundled in Odoo 18 web assets. Use for Sprint Board column transitions.

## Dependencies & Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| OWL API changes between Odoo 18 patches | High | Pin to Odoo 18.0 stable, use `@web/core/` imports |
| Chart.js version mismatch | Medium | Use Odoo-bundled Chart.js, no external CDN |
| Drag-drop performance on large sprints | Medium | Paginate tasks, lazy load columns |
| Ceremony model migration from text fields | Low | Keep text fields, ceremony model is additive |
| Test isolation in Odoo test framework | Low | Use TransactionCase, separate test database |

## File Impact Summary

### New Files

| File | Phase | Purpose |
|------|-------|---------|
| `models/scrum_ceremony.py` | P1 | Ceremony tracking model |
| `views/scrum-ceremony-views.xml` | P1 | Ceremony form/list/calendar |
| `report/sprint-report-template.xml` | P1 | Sprint PDF QWeb template |
| `report/sprint-report.py` | P1 | Sprint report data model |
| `static/src/js/sprint-board.js` | P2 | Sprint Board OWL component |
| `static/src/xml/sprint-board.xml` | P2 | Sprint Board QWeb template |
| `static/src/js/burndown-chart.js` | P3 | Burndown Chart OWL widget |
| `static/src/xml/burndown-chart.xml` | P3 | Burndown QWeb template |
| `static/src/js/velocity-chart.js` | P3 | Velocity Chart OWL widget |
| `static/src/xml/velocity-chart.xml` | P3 | Velocity QWeb template |
| `static/src/js/agile-dashboard.js` | P4 | Dashboard OWL component |
| `static/src/xml/agile-dashboard.xml` | P4 | Dashboard QWeb template |
| `static/src/scss/sprint-board.scss` | P2 | Sprint Board styles |
| `static/src/scss/agile-dashboard.scss` | P4 | Dashboard styles |
| `tests/__init__.py` | P5 | Test package init |
| `tests/test_sprint.py` | P5 | Sprint lifecycle tests |
| `tests/test_backlog.py` | P5 | Backlog management tests |
| `tests/test_velocity.py` | P5 | Velocity calculation tests |
| `tests/test_ceremony.py` | P5 | Ceremony CRUD tests |

### Modified Files

| File | Phase | Changes |
|------|-------|---------|
| `models/__init__.py` | P1 | Add ceremony import |
| `__manifest__.py` | P1-P4 | Add new data/assets entries |
| `security/project-scrum-security.xml` | P1 | Add SM/PO groups |
| `security/ir.model.access.csv` | P1 | Add ceremony ACLs |
| `models/project_task_scrum.py` | P1 | Add acceptance_criteria, expand task_type |
| `views/project-scrum-menus.xml` | P1-P4 | Add ceremony/dashboard menus |
| `models/project_sprint.py` | P1 | Add ceremony_ids relation |

## Success Criteria

- [ ] Sprint Board renders with drag-drop between columns (To Do / In Progress / Review / Done)
- [ ] Burndown chart shows ideal vs actual lines for active sprint
- [ ] Velocity chart shows bar comparison across last 6 sprints
- [ ] Dashboard aggregates: active sprint status, burndown mini, velocity, team workload
- [ ] Ceremony model supports planning/daily/review/retrospective with attendees
- [ ] SM/PO/User security groups enforce appropriate access
- [ ] Sprint PDF report generates downloadable summary
- [ ] All tests pass: `python odoo-bin -d test_db --test-enable -i project_scrum`
- [ ] Module installs/uninstalls cleanly on fresh database

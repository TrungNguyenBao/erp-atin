---
title: "Scrum/Agile Enhancement Module for Odoo 18 CE"
description: "Three-phase implementation of project_scrum addon: sprint model, boards, analytics, ceremonies, epics"
status: completed
priority: P1
effort: 30h
branch: main
tags: [odoo, scrum, agile, project-management, addon]
created: 2026-03-18
---

# Project Scrum Module - Implementation Plan

## Overview

Custom Odoo 18 CE addon `project_scrum` adding Scrum/Agile workflow: per-project sprints, story points, velocity tracking, sprint ceremonies, and advanced features (epics, releases, impediments).

**Module:** `addons/project_scrum/`
**Depends:** `project`, `mail`, `web`

## Research Reports

- [Odoo Project Internals](../reports/researcher-260318-0856-odoo-project-internals.md)
- [Scrum/Agile Best Practices](../reports/researcher-260318-0856-scrum-agile-best-practices.md)

## Design Decisions

1. **New `project.sprint` model** -- NOT extending milestone (clean separation of concerns)
2. **Per-project sprints** -- each project has independent sprint cycles
3. **Both story_points + allocated_hours** -- points for velocity, hours for time tracking
4. **Feature flag** -- `enable_scrum` Boolean on project.project gates all Scrum UI

## Addon File Structure

```
addons/project_scrum/
+-- __init__.py
+-- __manifest__.py
+-- models/
|   +-- __init__.py
|   +-- project-sprint.py              # P1: project.sprint model (~150 lines)
|   +-- project-sprint-daily-log.py    # P2: daily snapshot for burndown (~80 lines)
|   +-- project-task-scrum.py          # P1: project.task extension (~100 lines)
|   +-- project-project-scrum.py       # P1: project.project extension (~80 lines)
|   +-- project-epic.py               # P3: project.epic model (~80 lines)
|   +-- project-release.py            # P3: project.release model (~70 lines)
+-- views/
|   +-- project-sprint-views.xml       # P1: Sprint form/kanban/list views
|   +-- project-sprint-board-views.xml # P1: Sprint board (tasks by stage)
|   +-- project-backlog-views.xml      # P1: Product backlog view
|   +-- project-task-views-inherit.xml # P1: Task form/kanban extensions
|   +-- project-project-views-inherit.xml # P1: Project form extension
|   +-- project-scrum-menus.xml        # P1: Menu items (updated in P2/P3)
|   +-- project-epic-views.xml        # P3: Epic form/list/kanban
|   +-- project-release-views.xml     # P3: Release form/list
+-- wizard/
|   +-- __init__.py
|   +-- sprint-planning-wizard.py      # P1: Bulk assign tasks to sprint
|   +-- sprint-planning-wizard-views.xml
|   +-- sprint-close-wizard.py         # P1: Sprint closure + velocity snapshot
|   +-- sprint-close-wizard-views.xml
+-- report/
|   +-- __init__.py
|   +-- sprint-burndown-report.py      # P2: SQL view for burndown chart
|   +-- sprint-burndown-report-views.xml
|   +-- sprint-velocity-report.py      # P2: SQL view for velocity chart
|   +-- sprint-velocity-report-views.xml
+-- security/
|   +-- project-scrum-security.xml     # Groups + record rules
|   +-- ir.model.access.csv            # ACL matrix
+-- data/
|   +-- project-scrum-data.xml         # Feature group toggle, cron jobs
|   +-- standup-digest-mail-template.xml  # P3: Email template
+-- static/
|   +-- description/
|   |   +-- icon.png
|   +-- src/
|       +-- scss/
|       |   +-- sprint-board.scss      # P2: Sprint UI styles
|       +-- js/
|       |   +-- sprint-burndown-chart.js  # P2: OWL burndown widget
|       |   +-- sprint-velocity-chart.js  # P2: OWL velocity widget
|       +-- xml/
|           +-- sprint-burndown-chart.xml # P2: QWeb template
|           +-- sprint-velocity-chart.xml # P2: QWeb template
+-- tests/
    +-- __init__.py
    +-- test-project-sprint.py
```

## Complete Model Inventory

| Model | Type | Phase | Description |
|-------|------|-------|-------------|
| `project.sprint` | New | P1 | Sprint container: name, dates, goal, state, capacity, velocity |
| `project.sprint.daily.log` | New | P2 | Daily snapshot of remaining/completed points per sprint |
| `project.sprint.burndown.report` | Abstract (SQL view) | P2 | Burndown chart data: remaining vs ideal line |
| `project.sprint.velocity.report` | Abstract (SQL view) | P2 | Velocity per sprint + rolling average |
| `project.epic` | New | P3 | Cross-sprint story grouping with progress tracking |
| `project.release` | New | P3 | Sprint grouping for release planning |
| `project.sprint.planning.wizard` | Transient | P1 | Bulk backlog-to-sprint assignment |
| `project.sprint.close.wizard` | Transient | P1 | Sprint closure with velocity snapshot |
| `project.task` | Inherited | P1+P3 | +sprint_id, +story_points, +epic_id, +blocker fields |
| `project.project` | Inherited | P1+P3 | +enable_scrum, +sprint_ids, +enable_standup_digest, +velocity_forecast |

## Phase Summary

| Phase | Scope | Effort | Status |
|-------|-------|--------|--------|
| [Phase 1](phase-01-foundation-sprint-model-and-boards.md) | Sprint model, task extension, boards, backlog, planning wizard, security | ~14h | Completed |
| [Phase 2](phase-02-analytics-and-ceremonies.md) | Burndown chart, velocity tracking, sprint review/retro, standup view | ~10h | Completed |
| [Phase 3](phase-03-advanced-features.md) | Epics, releases, impediment tracking, email digest, velocity forecast | ~6h | Completed |

## Key Architecture Decisions

1. **project.sprint as standalone model** (not inheriting project.milestone) -- milestones = delivery targets, sprints = time-boxed work containers. Different lifecycle, different computed fields.
2. **Sprint daily log model** for burndown -- snapshot remaining_points daily via cron, avoids complex SQL CTE on mail.tracking.
3. **Wizard-based sprint planning** -- TransientModel for bulk backlog-to-sprint assignment with capacity visualization.
4. **Wizard-based sprint closure** -- captures velocity snapshot, validates all tasks reviewed, triggers retrospective.
5. **Feature flag pattern** -- `enable_scrum` on project.project, conditional visibility via `invisible` attribute. No feature group needed.

## Dependencies & Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| sprint_id on task conflicts with milestone_id UX | Medium | Clear UI separation: milestone = delivery target, sprint = work container |
| Burndown chart JS widget complexity | High | Phase 2; use Chart.js via OWL component, same pattern as existing burndown |
| Performance on large backlogs | Medium | Indexed sprint_id field; pagination on backlog view |
| Existing projects adoption | Low | enable_scrum defaults False; no data migration needed |

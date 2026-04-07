# Phase 5: OWL Agile Dashboard

## Context Links

- [Plan Overview](plan.md)
- [Phase 2: Wireframes](phase-02-wireframe-ui-ux-design.md)
- [Phase 3: Sprint Board](phase-03-owl-sprint-board.md)
- [Phase 4: Charts](phase-04-owl-charts-burndown-velocity.md)
- Odoo 18 dashboard pattern: `addons/project/static/src/views/`

## Overview

- **Priority:** P1 -- High
- **Status:** Completed
- **Effort:** ~6h
- **Depends on:** Phase 3 (reuses BurndownChart + VelocityChart components)
- **Description:** Central Agile Dashboard combining sprint status, burndown mini-chart, velocity overview, team workload, and recent activity

## Requirements

### Functional

- F1: Dashboard shows active sprint summary (name, dates, progress bar, days remaining)
- F2: Mini burndown chart for active sprint (reuse BurndownChart component)
- F3: Velocity overview with last 6 sprints (reuse VelocityChart component)
- F4: Team workload: assigned SP per team member in active sprint
- F5: Backlog health: total backlog items count, unestimated count, top-priority items
- F6: Recent activity feed: last 10 task stage changes
- F7: Project selector to switch between Scrum-enabled projects

### Non-Functional

- NF1: Dashboard loads within 3s for all widgets
- NF2: Each widget fetches data independently (parallel RPC)
- NF3: Graceful degradation: if no active sprint, show "No active sprint" placeholder

## Architecture

### Component Hierarchy

```
AgileDashboardAction (client action)
├── ProjectSelector (dropdown, Scrum-enabled projects only)
├── SprintSummaryCard (active sprint stats)
├── BurndownChart (from Phase 3, mini mode)
├── VelocityChart (from Phase 3, compact mode)
├── TeamWorkloadWidget (bar chart or table)
├── BacklogHealthWidget (stats cards)
└── ActivityFeedWidget (timeline list)
```

### Dashboard Data RPC

```python
# New method on project.project
def get_dashboard_data(self):
    self.ensure_one()
    active_sprint = self.active_sprint_id
    return {
        'sprint': active_sprint and {
            'id': active_sprint.id,
            'name': active_sprint.name,
            'start_date': active_sprint.start_date,
            'end_date': active_sprint.end_date,
            'committed': active_sprint.committed_points,
            'completed': active_sprint.completed_points,
            'completion_pct': active_sprint.completion_percentage,
            'days_remaining': (active_sprint.end_date - fields.Date.today()).days,
            'task_count': active_sprint.task_count,
        } or False,
        'team_workload': self._get_team_workload(),
        'backlog_health': self._get_backlog_health(),
        'recent_activity': self._get_recent_activity(limit=10),
    }
```

## Implementation Steps

### Step 1: Dashboard data endpoints (~1.5h)

- [ ] Add `get_dashboard_data()` to `project_project_scrum.py`
- [ ] Implement `_get_team_workload()`: group active sprint tasks by user, sum SP
- [ ] Implement `_get_backlog_health()`: count backlog tasks, unestimated, by priority
- [ ] Implement `_get_recent_activity()`: recent task stage changes from mail.tracking

### Step 2: AgileDashboardAction OWL component (~2h)

- [ ] Create `static/src/js/agile-dashboard.js`
- [ ] Project selector with `onChange` handler
- [ ] Load all widget data in `onWillStart` (parallel promises)
- [ ] State management for project switching
- [ ] Register as client action: `registry.category("actions").add("agile_dashboard", ...)`

### Step 3: Dashboard QWeb template (~1.5h)

- [ ] Create `static/src/xml/agile-dashboard.xml`
- [ ] Grid layout: 2-column on desktop, single column on mobile
- [ ] Sprint summary card: progress bar, dates, SP counters
- [ ] Team workload: horizontal bar chart or simple table
- [ ] Backlog health: stat cards (total, unestimated, critical)
- [ ] Activity feed: timeline with task name, old→new stage, timestamp

### Step 4: SCSS & polish (~0.5h)

- [ ] Create `static/src/scss/agile-dashboard.scss`
- [ ] Card-based layout with consistent spacing
- [ ] Color coding: green (on track), amber (at risk), red (behind)
- [ ] Dark mode support (inherit Odoo's CSS variables)

### Step 5: Menu & manifest (~0.5h)

- [ ] Add dashboard client action XML
- [ ] Add "Agile Dashboard" menu item (top of Scrum menu)
- [ ] Update `__manifest__.py` with new assets
- [ ] Test end-to-end: menu → dashboard → all widgets render

## Risks

| Risk | Mitigation |
|------|------------|
| Too many RPCs slowing load | Consolidate into single `get_dashboard_data()` call |
| Activity feed requires mail module queries | Use `self.env['mail.tracking.value']` with indexed domain |
| No active sprint edge case | Show empty state with "Start a Sprint" CTA button |

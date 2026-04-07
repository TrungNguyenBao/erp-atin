# Phase 1: Ceremony Model, Security Roles & Task Fields

## Context Links

- [Plan Overview](plan.md)
- Existing sprint model: `addons/project_scrum/models/project_sprint.py`
- Existing security: `addons/project_scrum/security/project-scrum-security.xml`
- Existing task extension: `addons/project_scrum/models/project_task_scrum.py`
- Odoo project security pattern: `addons/project/security/project_security.xml`

## Overview

- **Priority:** P1 -- High
- **Status:** Completed
- **Effort:** ~6h
- **Description:** Add dedicated `scrum.ceremony` model, create Scrum Master/Product Owner/Scrum User security groups, extend task fields, add Sprint PDF report

## Requirements

### Functional

- F1: `scrum.ceremony` model with types: planning, daily, review, retrospective
- F2: Ceremony tracks attendees (Many2many res.users), notes, action items, duration
- F3: Retrospective ceremonies have went_well, to_improve, action_items fields
- F4: Three security groups: Scrum User (view), Scrum Master (manage sprints/ceremonies), Product Owner (manage backlog/epics)
- F5: Task gets `acceptance_criteria` (Text) and expanded `task_type` (add 'epic', 'improvement')
- F6: Sprint PDF report with QWeb template showing sprint summary, task list, velocity

### Non-Functional

- NF1: Groups inherit from existing project groups (no breaking changes)
- NF2: Ceremony text fields on Sprint remain for backward compatibility
- NF3: PDF report follows Odoo report standards (action + template)

## Architecture

### scrum.ceremony Model

```python
class ScrumCeremony(models.Model):
    _name = 'scrum.ceremony'
    _description = 'Scrum Ceremony'
    _inherit = ['mail.thread']
    _order = 'date desc'

    name = fields.Char(required=True)
    sprint_id = fields.Many2one('project.sprint', required=True, ondelete='cascade')
    project_id = fields.Many2one(related='sprint_id.project_id', store=True)
    ceremony_type = fields.Selection([
        ('planning', 'Sprint Planning'),
        ('daily', 'Daily Standup'),
        ('review', 'Sprint Review'),
        ('retrospective', 'Retrospective'),
    ], required=True)
    date = fields.Datetime(required=True)
    duration = fields.Float('Duration (hours)', default=1.0)
    attendee_ids = fields.Many2many('res.users')
    notes = fields.Html('Meeting Notes')
    action_items = fields.Text('Action Items')
    # Retro-specific
    went_well = fields.Text('What Went Well')
    to_improve = fields.Text('To Improve')
```

### Security Groups Hierarchy

```
project.group_project_user
  └── project_scrum.group_scrum_user        # View sprints, tasks, ceremonies
        └── project_scrum.group_scrum_master # Manage sprints, ceremonies, boards
              └── project_scrum.group_product_owner  # Manage backlog, epics, priorities
```

### Sprint PDF Report

- `report/sprint-report.py`: Abstract model `project.sprint.report` with data methods
- `report/sprint-report-template.xml`: QWeb template rendering sprint summary
- Action on sprint form: "Print Sprint Report" button

## Implementation Steps

### Step 1: scrum.ceremony model (~1.5h)

- [ ] Create `models/scrum_ceremony.py` with fields above
- [ ] Add `ceremony_ids = fields.One2many('scrum.ceremony', 'sprint_id')` to `project_sprint.py`
- [ ] Update `models/__init__.py` with ceremony import
- [ ] Create `views/scrum-ceremony-views.xml` (form, list, calendar views)
- [ ] Add ceremony menu item under Scrum menu

### Step 2: Security groups (~1.5h)

- [ ] Add 3 groups to `security/project-scrum-security.xml`:
  - `group_scrum_user` (implied by `project.group_project_user`)
  - `group_scrum_master` (implies `group_scrum_user`)
  - `group_product_owner` (implies `group_scrum_master`)
- [ ] Update `ir.model.access.csv` with ceremony ACLs per group
- [ ] Add record rules: ceremonies follow sprint's project privacy
- [ ] Update existing field visibility to use new groups where appropriate

### Step 3: Task field extension (~1h)

- [ ] Add `acceptance_criteria = fields.Text('Acceptance Criteria')` to `project_task_scrum.py`
- [ ] Expand `task_type` selection: add `('epic', 'Epic')`, `('improvement', 'Improvement')`
- [ ] Update `views/project-task-views-inherit.xml` to show new fields in Scrum tab

### Step 4: Sprint PDF report (~1.5h)

- [ ] Create `report/sprint-report.py` with `_get_report_values()` 
- [ ] Create `report/sprint-report-template.xml` with QWeb layout:
  - Sprint header (name, dates, goal, state)
  - Task summary table (name, assignee, story_points, status)
  - Velocity metrics (committed, completed, %)
- [ ] Add print button to sprint form view header
- [ ] Register report action in `__manifest__.py`

### Step 5: Manifest & menu updates (~0.5h)

- [ ] Add all new files to `__manifest__.py` data list
- [ ] Add ceremony menu + calendar to menus XML
- [ ] Verify module installs cleanly

## Risks

| Risk | Mitigation |
|------|------------|
| Group hierarchy conflicts with existing access | Test with fresh DB; groups are additive, never remove existing permissions |
| Ceremony calendar view performance | Use date-based domain filters, limit default view to current month |

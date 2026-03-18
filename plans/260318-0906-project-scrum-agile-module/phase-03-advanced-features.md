# Phase 3: Advanced Features

## Context Links

- [Plan Overview](plan.md)
- [Phase 1: Foundation](phase-01-foundation-sprint-model-and-boards.md)
- [Phase 2: Analytics & Ceremonies](phase-02-analytics-and-ceremonies.md)
- [Scrum Best Practices Report](../reports/researcher-260318-0856-scrum-agile-best-practices.md)

## Overview

- **Priority:** P3 -- Nice-to-have
- **Status:** Pending
- **Effort:** ~6h
- **Depends on:** Phase 1 + Phase 2 complete
- **Description:** Epics, release planning, impediment tracking, automated standup digest, velocity forecasting

## Key Insights

1. Epics = grouping mechanism above stories. Odoo already has `parent_id`/`child_ids` on tasks. But epics span sprints, so a lightweight model or tag-based approach is cleaner than task hierarchy.
2. Releases = group of sprints. Lightweight model with sprint Many2many.
3. Impediment tracking = flag on task + blocker reason. Simpler than a separate model.
4. Standup digest = scheduled email using `mail.template` + cron. Odoo's mail infrastructure handles this natively.
5. Velocity forecast = computed field using rolling average from Phase 2's velocity report. No new model.

## Requirements

### Functional
- F1: Epic model -- group stories across sprints, track progress across multiple sprints
- F2: Release model -- group sprints into releases, track release scope/progress
- F3: Impediment tracking -- flag tasks as blocked with reason + owner + resolution
- F4: Automated standup digest -- daily email to project followers summarizing active sprint status
- F5: Velocity forecasting -- predict next sprint capacity from 3-sprint rolling average

### Non-Functional
- NF1: Epics/releases are opt-in (don't clutter UI for teams not using them)
- NF2: Digest email is configurable per-project (enable/disable)
- NF3: All files < 200 lines

## Architecture

### Epic Model (`models/project-epic.py`)

```python
class ProjectEpic(models.Model):
    _name = 'project.epic'
    _description = 'Epic'
    _inherit = ['mail.thread']
    _order = 'sequence, id'

    name = fields.Char(required=True, tracking=True)
    description = fields.Html()
    project_id = fields.Many2one('project.project', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    color = fields.Integer()

    # Relationships
    task_ids = fields.One2many('project.task', 'epic_id', string='Stories')
    tag_ids = fields.Many2many('project.tags')

    # Computed progress
    task_count = fields.Integer(compute='_compute_progress', store=True)
    done_task_count = fields.Integer(compute='_compute_progress', store=True)
    total_points = fields.Integer(compute='_compute_progress', store=True)
    completed_points = fields.Integer(compute='_compute_progress', store=True)
    progress_percentage = fields.Float(compute='_compute_progress', store=True)
    company_id = fields.Many2one(related='project_id.company_id', store=True)
```

Task extension (add to `models/project-task-scrum.py`):
```python
epic_id = fields.Many2one('project.epic', string='Epic',
    domain="[('project_id', '=', project_id)]",
    tracking=True, groups='project.group_project_scrum')
```

### Release Model (`models/project-release.py`)

```python
class ProjectRelease(models.Model):
    _name = 'project.release'
    _description = 'Release'
    _inherit = ['mail.thread']
    _order = 'target_date desc, id desc'

    RELEASE_STATES = [
        ('planning', 'Planning'),
        ('in_progress', 'In Progress'),
        ('released', 'Released'),
    ]

    name = fields.Char(required=True, tracking=True)
    project_id = fields.Many2one('project.project', required=True, ondelete='cascade')
    target_date = fields.Date(tracking=True)
    state = fields.Selection(RELEASE_STATES, default='planning', tracking=True)
    description = fields.Html()
    sprint_ids = fields.Many2many('project.sprint', string='Sprints')
    company_id = fields.Many2one(related='project_id.company_id', store=True)

    # Computed
    sprint_count = fields.Integer(compute='_compute_stats')
    total_points = fields.Integer(compute='_compute_stats')
    completed_points = fields.Integer(compute='_compute_stats')
```

### Impediment Fields on Task (`models/project-task-scrum.py` additions)

```python
is_blocked = fields.Boolean(string='Blocked', tracking=True,
    groups='project.group_project_scrum')
blocker_description = fields.Text(string='Blocker Description',
    groups='project.group_project_scrum')
blocker_owner_id = fields.Many2one('res.users', string='Blocker Owner',
    groups='project.group_project_scrum',
    help='Person responsible for resolving this impediment')
blocker_resolved_date = fields.Date(string='Resolved Date', readonly=True,
    groups='project.group_project_scrum')
```

Auto-clear: `@api.onchange('is_blocked')` -- when unchecked, set `blocker_resolved_date = today`.

### Standup Digest (`models/project-project-scrum.py` additions)

Add to project model:
```python
enable_standup_digest = fields.Boolean(string='Daily Standup Digest',
    help='Send daily email summary of active sprint status to project followers')
```

Cron method on `project.project`:
```python
def _cron_send_standup_digest(self):
    """Send daily standup digest for projects with enable_standup_digest=True."""
    projects = self.search([
        ('enable_scrum', '=', True),
        ('enable_standup_digest', '=', True),
    ])
    for project in projects:
        sprint = project.active_sprint_id
        if not sprint:
            continue
        # Build digest: tasks in progress grouped by user, blocked tasks highlighted
        # Send via mail.template
```

Mail template in `data/project-scrum-data.xml`:
- Subject: "[{project}] Sprint Standup - {date}"
- Body: QWeb template listing tasks by assignee, highlighting blocked items
- Recipients: project followers

### Velocity Forecast (computed on project)

Add to `models/project-project-scrum.py`:
```python
velocity_forecast = fields.Float(string='Forecasted Velocity',
    compute='_compute_velocity_forecast',
    help='Predicted next sprint capacity based on 3-sprint rolling average')

def _compute_velocity_forecast(self):
    for project in self:
        closed_sprints = self.env['project.sprint'].search([
            ('project_id', '=', project.id),
            ('state', '=', 'closed'),
            ('velocity', '>', 0),
        ], order='end_date desc', limit=3)
        if closed_sprints:
            project.velocity_forecast = sum(closed_sprints.mapped('velocity')) / len(closed_sprints)
        else:
            project.velocity_forecast = 0
```

Displayed on sprint planning wizard to guide capacity setting.

## Related Code Files

### Files to CREATE

| File | Purpose | Est. Lines |
|------|---------|-----------|
| `models/project-epic.py` | Epic model | 80 |
| `models/project-release.py` | Release model | 70 |
| `views/project-epic-views.xml` | Epic form/list/kanban views | 120 |
| `views/project-release-views.xml` | Release form/list views | 90 |
| `data/standup-digest-mail-template.xml` | Email template for digest | 50 |

### Files to MODIFY (from Phase 1/2)

| File | Changes |
|------|---------|
| `models/__init__.py` | Add imports for epic, release |
| `models/project-task-scrum.py` | Add epic_id + impediment fields (~15 lines) |
| `models/project-project-scrum.py` | Add enable_standup_digest, velocity_forecast, cron method (~30 lines) |
| `views/project-task-views-inherit.xml` | Add epic_id field, blocker section to task form |
| `views/project-project-views-inherit.xml` | Add enable_standup_digest toggle |
| `views/project-scrum-menus.xml` | Add Epics, Releases menu items |
| `wizard/sprint-planning-wizard.py` | Show velocity_forecast in capacity section |
| `__manifest__.py` | Add new data/view files |
| `security/ir.model.access.csv` | Add ACL for epic, release models |
| `security/project-scrum-security.xml` | Add record rules for epic, release |
| `data/project-scrum-data.xml` | Add standup digest cron |

## Implementation Steps

### Step 1: Epic Model + Views (2h)

1. Create `models/project-epic.py` with computed progress fields
2. Add `epic_id` to task model in `models/project-task-scrum.py`
3. Create `views/project-epic-views.xml`: form (name, description, progress bar, task list), list, kanban
4. Add epic filter/group-by to task search view inheritance
5. Add Epics menu item under Scrum
6. Update ACL + record rules
7. Compile + test

### Step 2: Release Model + Views (1.5h)

1. Create `models/project-release.py`
2. Create `views/project-release-views.xml`: form (name, target_date, state, sprint list), list
3. Add Releases menu item
4. Update ACL + record rules
5. Compile + test

### Step 3: Impediment Tracking (1h)

1. Add blocker fields to `models/project-task-scrum.py`
2. Add blocker section to task form view (collapsible group, visible when is_blocked=True)
3. Add "Blocked" filter to task search view
4. Add visual indicator on task kanban (red border or icon when is_blocked=True)
5. Compile + test

### Step 4: Standup Digest Email (1h)

1. Add `enable_standup_digest` to project model
2. Add toggle to project form settings
3. Create mail template in `data/standup-digest-mail-template.xml`
4. Implement `_cron_send_standup_digest()` on project model
5. Add cron record to data XML
6. Test: enable digest on project, trigger cron manually, verify email

### Step 5: Velocity Forecast (30 min)

1. Add `velocity_forecast` computed field to project model
2. Display in sprint planning wizard next to capacity_points
3. Display on project form (Scrum stats section)
4. Test with closed sprints data

## Todo List

- [ ] Create epic model + computed progress
- [ ] Add epic_id to task model
- [ ] Create epic views (form/list/kanban)
- [ ] Create release model
- [ ] Create release views
- [ ] Add impediment fields to task
- [ ] Add blocker UI to task form + kanban
- [ ] Add "Blocked" filter to task search
- [ ] Implement standup digest cron + mail template
- [ ] Add velocity forecast computed field
- [ ] Update menus, ACL, record rules
- [ ] Test all features end-to-end

## Success Criteria

1. Epics group tasks across sprints; progress bar shows completion
2. Releases group sprints; status tracks release lifecycle
3. Blocked tasks show visual indicator on kanban + have structured blocker info
4. Standup digest email sends daily with correct sprint status
5. Velocity forecast shows on planning wizard, matches rolling average

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Email delivery issues (SMTP config) | Medium | Low | Digest is nice-to-have; works with any Odoo mail setup |
| Epic vs parent_id confusion | Low | Medium | Clear UI labeling; epic = cross-sprint grouping, parent = task decomposition |
| Too many fields on task form | Medium | Medium | Use conditional visibility (invisible= attrs); group in collapsible sections |

## Security Considerations

- Epic/Release: same access pattern as sprint (read for users, CRUD for managers)
- Blocker fields: writable by task assignees + managers
- Standup digest: sent only to project followers (respects privacy_visibility)
- Multi-company rules mirror sprint pattern

## Unresolved Questions

1. **Epic color coding:** Should epics have configurable colors for kanban badges, or use project tags?
2. **Release notes generation:** Auto-generate release notes from completed epics/stories, or manual?
3. **Digest frequency:** Fixed daily, or configurable (daily/weekly)?

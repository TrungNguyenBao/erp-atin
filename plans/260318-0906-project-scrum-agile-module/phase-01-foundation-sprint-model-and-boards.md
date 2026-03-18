# Phase 1: Foundation -- Sprint Model, Boards & Planning

## Context Links

- [Plan Overview](plan.md)
- [Odoo Project Internals Report](../reports/researcher-260318-0856-odoo-project-internals.md)
- [Scrum Best Practices Report](../reports/researcher-260318-0856-scrum-agile-best-practices.md)
- Existing addon pattern: `addons/ui_enhance_crm_sale/`
- Project security: `addons/project/security/project_security.xml`
- Project menus: `addons/project/views/project_menus.xml`

## Overview

- **Priority:** P1 -- Critical
- **Status:** Pending
- **Effort:** ~14h
- **Description:** Core sprint infrastructure -- models, views, security, backlog, sprint board, planning wizard

## Key Insights

1. `project.milestone` exists but is lightweight (name, deadline, is_reached). Sprint needs status workflow, capacity, velocity -- separate model is cleaner.
2. Task already has `milestone_id`, `allocated_hours`, `priority`, `stage_id`, `depend_on_ids`. We add `sprint_id` + `story_points` without touching existing fields.
3. Existing security pattern: hidden feature groups (`group_project_milestone`, `group_project_task_dependencies`). We follow same for `group_project_scrum`.
4. Menu structure: top-level Project app has Tasks > My Tasks / All Tasks. We add Scrum section.
5. `CLOSED_STATES = {'1_done': 'Done', '1_canceled': 'Cancelled'}` -- reuse for velocity computation.

## Requirements

### Functional
- F1: Create/edit/delete sprints per project (name, dates, goal, status, capacity)
- F2: Sprint status workflow: draft -> active -> closed (only 1 active sprint per project)
- F3: Add story_points (Integer) to tasks
- F4: Assign tasks to sprints (Many2one task -> sprint)
- F5: Product backlog view: tasks where sprint_id = False, sorted by priority/sequence
- F6: Sprint board: kanban of tasks filtered by active sprint, grouped by stage
- F7: Sprint planning wizard: bulk-select backlog tasks, see capacity bar, assign to sprint
- F8: Sprint closure wizard: validate completion, snapshot velocity, move incomplete tasks
- F9: Feature flag `enable_scrum` on project.project gates all Scrum UI
- F10: Security group `group_project_scrum` (hidden, like group_project_milestone)

### Non-Functional
- NF1: All model files < 200 lines
- NF2: Kebab-case file names
- NF3: tracking=True on key fields (story_points, sprint_id, status) for chatter history
- NF4: Multi-company compatible (follow existing ir.rule pattern)

## Architecture

### Models

#### project.sprint (NEW -- `models/project-sprint.py`)

```python
class ProjectSprint(models.Model):
    _name = 'project.sprint'
    _description = 'Sprint'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc, id desc'

    SPRINT_STATES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]

    name = fields.Char(required=True, tracking=True)
    project_id = fields.Many2one('project.project', required=True, ondelete='cascade', tracking=True)
    goal = fields.Text(string='Sprint Goal', tracking=True)
    start_date = fields.Date(required=True, tracking=True)
    end_date = fields.Date(required=True, tracking=True)
    state = fields.Selection(SPRINT_STATES, default='draft', required=True, tracking=True)
    capacity_points = fields.Integer(string='Planned Capacity (Points)', tracking=True)

    # Relationships
    task_ids = fields.One2many('project.task', 'sprint_id', string='Tasks')
    company_id = fields.Many2one(related='project_id.company_id', store=True)

    # Computed
    task_count = fields.Integer(compute='_compute_task_stats', store=True)
    committed_points = fields.Integer(compute='_compute_task_stats', store=True,
        help='Sum of story points for all tasks in this sprint')
    completed_points = fields.Integer(compute='_compute_task_stats', store=True,
        help='Sum of story points for closed tasks')
    remaining_points = fields.Integer(compute='_compute_task_stats', store=True)
    completion_percentage = fields.Float(compute='_compute_task_stats', store=True)

    # Velocity (set at sprint close, not computed live)
    velocity = fields.Integer(string='Velocity (Closed Points)', readonly=True,
        help='Snapshot of completed_points at sprint closure')

    _sql_constraints = [
        ('date_check', 'CHECK(end_date >= start_date)', 'End date must be after start date.'),
    ]
```

**Key methods:**
- `_compute_task_stats()` -- depends on `task_ids.story_points`, `task_ids.state`
- `action_start_sprint()` -- validates no other active sprint on project, sets state='active'
- `action_close_sprint()` -- opens sprint-close wizard
- `_check_single_active_sprint()` -- constraint: max 1 active sprint per project

#### project.task extension (`models/project-task-scrum.py`)

```python
class ProjectTaskScrum(models.Model):
    _inherit = 'project.task'

    sprint_id = fields.Many2one('project.sprint', string='Sprint',
        domain="[('project_id', '=', project_id), ('state', '!=', 'closed')]",
        tracking=True, index=True,
        groups='project.group_project_scrum')
    story_points = fields.Integer(string='Story Points', tracking=True,
        groups='project.group_project_scrum',
        help='Relative complexity estimate (Fibonacci: 1, 2, 3, 5, 8, 13, 21)')
    is_in_backlog = fields.Boolean(compute='_compute_is_in_backlog', store=True,
        help='True if task has no sprint assigned')

    @api.depends('sprint_id')
    def _compute_is_in_backlog(self):
        for task in self:
            task.is_in_backlog = not task.sprint_id
```

**SELF_READABLE_FIELDS / SELF_WRITABLE_FIELDS:** Extend to include `sprint_id`, `story_points` for portal sharing if needed.

#### project.project extension (`models/project-project-scrum.py`)

```python
class ProjectProjectScrum(models.Model):
    _inherit = 'project.project'

    enable_scrum = fields.Boolean(string='Scrum', default=False,
        help='Enable Scrum features: sprints, story points, velocity tracking')
    sprint_ids = fields.One2many('project.sprint', 'project_id', string='Sprints')
    active_sprint_id = fields.Many2one('project.sprint', compute='_compute_active_sprint_id',
        string='Active Sprint')
    sprint_count = fields.Integer(compute='_compute_sprint_count')

    @api.depends('sprint_ids.state')
    def _compute_active_sprint_id(self):
        for project in self:
            project.active_sprint_id = self.env['project.sprint'].search([
                ('project_id', '=', project.id),
                ('state', '=', 'active'),
            ], limit=1)
```

### Security

#### New Group (`security/project-scrum-security.xml`)

```xml
<record id="group_project_scrum" model="res.groups">
    <field name="name">Use Scrum</field>
    <field name="category_id" ref="base.module_category_hidden"/>
</record>
```

Hidden feature group (like `group_project_milestone`). Toggled automatically when `enable_scrum=True` on any project.

#### ACL Matrix (`security/ir.model.access.csv`)

| Model | Group | Read | Write | Create | Unlink |
|-------|-------|------|-------|--------|--------|
| project.sprint | group_project_user | 1 | 0 | 0 | 0 |
| project.sprint | group_project_manager | 1 | 1 | 1 | 1 |
| project.sprint | base.group_portal | 1 | 0 | 0 | 0 |

#### Record Rules

- `sprint_comp_rule` -- multi-company: `('company_id', 'in', company_ids + [False])`
- `sprint_visibility_rule` -- follow project privacy (same pattern as milestone_visibility_rule)
- `sprint_manager_rule` -- managers see all: `[(1, '=', 1)]`

### Views

#### Sprint Form (`views/project-sprint-views.xml`)

Header with status bar (draft/active/closed), buttons (Start Sprint, Close Sprint).
Sheet: name, project_id, goal, start_date, end_date, capacity_points.
Stat buttons: task_count, committed_points, completed_points.
Notebook tab: task_ids list (inline, showing name, story_points, stage_id, state, user_ids).

#### Sprint List

Columns: name, project_id, start_date, end_date, state, committed_points, completed_points, velocity.
Decorations: `decoration-info="state == 'active'"`, `decoration-muted="state == 'closed'"`.

#### Sprint Kanban

Cards showing: name, date range, state badge, capacity bar (committed/capacity), task_count.

#### Sprint Board (`views/project-sprint-board-views.xml`)

Action: `action_sprint_board` -- opens task kanban filtered by `sprint_id = active_sprint_id`.
Context: `{'search_default_sprint_id': active_sprint_id, 'default_sprint_id': active_sprint_id}`.
Reuses existing `project.task` kanban view with inherited sprint badge on cards.

#### Product Backlog (`views/project-backlog-views.xml`)

Action: `action_product_backlog` -- task list/kanban filtered by `is_in_backlog = True`.
Sorted by: priority desc, sequence asc.
Shows: name, story_points, priority, stage_id, user_ids.
Group by: priority, tags, no-group (flat list for drag-reorder).

#### Task Form Inherit (`views/project-task-views-inherit.xml`)

```xml
<!-- Add story_points next to allocated_hours -->
<xpath expr="//field[@name='allocated_hours']" position="before">
    <field name="story_points"
           invisible="not parent.enable_scrum"
           groups="project.group_project_scrum"/>
</xpath>

<!-- Add sprint_id in task form header area or group -->
<xpath expr="//field[@name='milestone_id']" position="after">
    <field name="sprint_id"
           invisible="not parent.enable_scrum"
           groups="project.group_project_scrum"
           options="{'no_create': True}"/>
</xpath>
```

#### Task Kanban Inherit

Add story points badge on kanban card (small pill showing "5 SP").

#### Project Form Inherit (`views/project-project-views-inherit.xml`)

Add `enable_scrum` toggle in project settings tab (near `allow_milestones`, `allow_task_dependencies`).
Add stat button for sprint_count linking to sprint list view.

#### Menus (`views/project-scrum-menus.xml`)

```
Project (menu_main_pm)
  +-- Scrum (NEW, sequence=15, visible when group_project_scrum)
  |   +-- Sprint Board (action_sprint_board)
  |   +-- Product Backlog (action_product_backlog)
  |   +-- Sprints (action_view_all_sprints)
```

### Wizards

#### Sprint Planning Wizard (`wizard/sprint-planning-wizard.py`)

TransientModel `project.sprint.planning.wizard`:
- `sprint_id` (Many2one, required)
- `project_id` (related to sprint)
- `backlog_task_ids` (Many2many → project.task, domain: backlog tasks of project)
- `capacity_points` (related to sprint)
- `committed_points` (computed: sum of selected tasks' story_points)
- `remaining_capacity` (computed: capacity - committed)

**action_assign():** Sets `sprint_id` on selected tasks. Warns if over-capacity.

#### Sprint Close Wizard (`wizard/sprint-close-wizard.py`)

TransientModel `project.sprint.close.wizard`:
- `sprint_id` (Many2one, required)
- `incomplete_task_ids` (computed: tasks not in CLOSED_STATES)
- `move_to_sprint_id` (Many2one, optional: target sprint for incomplete tasks)
- `move_to_backlog` (Boolean, default True)

**action_close():**
1. Snapshot velocity = sprint.completed_points
2. Move incomplete tasks to target sprint or backlog (sprint_id = False)
3. Set sprint.state = 'closed'

### Data

`data/project-scrum-data.xml`:
- Settings record linking `enable_scrum` to `group_project_scrum` (same pattern as `allow_milestones` -> `group_project_milestone` in res.config.settings)

## Related Code Files

### Files to CREATE

| File | Purpose | Est. Lines |
|------|---------|-----------|
| `addons/project_scrum/__init__.py` | Module init | 5 |
| `addons/project_scrum/__manifest__.py` | Manifest | 45 |
| `addons/project_scrum/models/__init__.py` | Models init | 5 |
| `addons/project_scrum/models/project-sprint.py` | Sprint model | 150 |
| `addons/project_scrum/models/project-task-scrum.py` | Task extension | 80 |
| `addons/project_scrum/models/project-project-scrum.py` | Project extension | 70 |
| `addons/project_scrum/views/project-sprint-views.xml` | Sprint CRUD views | 180 |
| `addons/project_scrum/views/project-sprint-board-views.xml` | Sprint board action | 60 |
| `addons/project_scrum/views/project-backlog-views.xml` | Backlog view | 80 |
| `addons/project_scrum/views/project-task-views-inherit.xml` | Task view extensions | 80 |
| `addons/project_scrum/views/project-project-views-inherit.xml` | Project form extensions | 50 |
| `addons/project_scrum/views/project-scrum-menus.xml` | Menu structure | 40 |
| `addons/project_scrum/wizard/__init__.py` | Wizard init | 4 |
| `addons/project_scrum/wizard/sprint-planning-wizard.py` | Planning wizard model | 90 |
| `addons/project_scrum/wizard/sprint-planning-wizard-views.xml` | Planning wizard form | 50 |
| `addons/project_scrum/wizard/sprint-close-wizard.py` | Close wizard model | 80 |
| `addons/project_scrum/wizard/sprint-close-wizard-views.xml` | Close wizard form | 50 |
| `addons/project_scrum/security/project-scrum-security.xml` | Groups + rules | 80 |
| `addons/project_scrum/security/ir.model.access.csv` | ACL matrix | 15 |
| `addons/project_scrum/data/project-scrum-data.xml` | Default data | 20 |

### Files to MODIFY

None -- this is a standalone addon. All changes via inheritance.

### Files to REFERENCE (read-only context)

| File | Why |
|------|-----|
| `addons/project/models/project_task.py` | CLOSED_STATES, field names, compute patterns |
| `addons/project/models/project_project.py` | Feature flag pattern, field layout |
| `addons/project/models/project_milestone.py` | Similar model structure reference |
| `addons/project/security/project_security.xml` | Record rule patterns |
| `addons/project/security/ir.model.access.csv` | ACL pattern |
| `addons/project/views/project_menus.xml` | Menu IDs for inheritance |
| `addons/project/views/project_task_views.xml` | xpath targets for task form/kanban |
| `addons/project/views/project_project_views.xml` | xpath targets for project form |
| `addons/project/views/project_milestone_views.xml` | View structure reference |

## Implementation Steps

### Step 1: Module Scaffold (30 min)

1. Create `addons/project_scrum/` directory structure (all folders)
2. Create `__init__.py` (root): `from . import models, wizard`
3. Create `models/__init__.py`: import all 3 model files
4. Create `wizard/__init__.py`: import both wizard files
5. Create `__manifest__.py`:
   - `name`: 'Project Scrum'
   - `version`: '18.0.1.0.0'
   - `category`: 'Services/Project'
   - `depends`: `['project', 'mail', 'web']`
   - `data`: list all XML files in correct load order (security first, then data, then views, then menus)
   - `assets`: empty for Phase 1 (SCSS/JS in Phase 2)
   - `application`: False
   - `installable`: True
   - `license`: 'LGPL-3'

### Step 2: Security Layer (30 min)

1. Create `security/project-scrum-security.xml`:
   - Define `group_project_scrum` (hidden category)
   - Record rules: sprint_comp_rule, sprint_visibility_rule, sprint_manager_rule
   - Follow exact pattern from `addons/project/security/project_security.xml`
2. Create `security/ir.model.access.csv`:
   - Sprint model: read for group_project_user, full CRUD for group_project_manager
   - Wizard models: full access for group_project_user (transient models)

### Step 3: Sprint Model (1.5h)

1. Create `models/project-sprint.py`:
   - Define fields as specified in Architecture section
   - `_compute_task_stats()`: read_group on task_ids by state, compute committed/completed/remaining points
   - `action_start_sprint()`: check no active sprint on project, write state='active'
   - `action_close_sprint()`: return wizard action
   - `_check_single_active_sprint()`: `@api.constrains('state')` -- at most 1 active per project
   - `name_get()`: show "[PROJECT] Sprint Name" format
2. Compile check: `python odoo-bin -c deploy/config/odoo.conf --stop-after-init -u project_scrum`

### Step 4: Task Extension (45 min)

1. Create `models/project-task-scrum.py`:
   - Add `sprint_id`, `story_points`, `is_in_backlog` fields
   - Domain on sprint_id: same project, not closed
   - `_compute_is_in_backlog()`: simple boolean
   - Override `_read_group_sprint_id()` for group_expand if needed
2. Compile check

### Step 5: Project Extension (30 min)

1. Create `models/project-project-scrum.py`:
   - Add `enable_scrum`, `sprint_ids`, `active_sprint_id`, `sprint_count`
   - `_compute_active_sprint_id()`: search for state='active' sprint
   - `_compute_sprint_count()`: len(sprint_ids)
   - Wire `enable_scrum` toggle to `group_project_scrum` via `res.config.settings` or direct `_onchange`
2. Compile check

### Step 6: Sprint Views (2h)

1. Create `views/project-sprint-views.xml`:
   - Form view with statusbar, header buttons, sheet layout
   - List view with decorations
   - Kanban view with capacity progress bar
   - Search view with filters: Draft, Active, Closed, group by project
   - Window action: `action_view_all_sprints`
2. Create `views/project-sprint-board-views.xml`:
   - Action opening task kanban filtered by active sprint
   - Include sprint info in context
3. Create `views/project-backlog-views.xml`:
   - Action opening task list/kanban filtered by is_in_backlog=True and project's enable_scrum=True
   - Custom search filters: Unestimated (story_points = 0), By Priority

### Step 7: Inherited Views (1.5h)

1. Create `views/project-task-views-inherit.xml`:
   - Inherit task form: add story_points, sprint_id fields
   - Inherit task kanban: add story points badge
   - Inherit task search: add sprint filter, sprint group-by
   - All gated by `invisible="not parent.enable_scrum"` or `groups="project.group_project_scrum"`
2. Create `views/project-project-views-inherit.xml`:
   - Inherit project form settings tab: add enable_scrum checkbox
   - Add sprint stat button in button_box
3. Compile check (install module, verify views render)

### Step 8: Menu Structure (30 min)

1. Create `views/project-scrum-menus.xml`:
   - Top-level "Scrum" menu under Project app (sequence=15)
   - Sub-menus: Sprint Board, Product Backlog, Sprints
   - Gated by `groups="project.group_project_scrum"`

### Step 9: Sprint Planning Wizard (1.5h)

1. Create `wizard/sprint-planning-wizard.py`:
   - TransientModel with fields as specified
   - `_default_backlog_tasks()`: fetch unassigned tasks for project
   - `action_assign()`: write sprint_id on selected tasks
   - Capacity bar computed field for UX
2. Create `wizard/sprint-planning-wizard-views.xml`:
   - Form with backlog task list (checkboxes), capacity indicator
   - Footer with Assign + Cancel buttons

### Step 10: Sprint Close Wizard (1.5h)

1. Create `wizard/sprint-close-wizard.py`:
   - Show incomplete tasks, option to move to next sprint or backlog
   - `action_close()`: snapshot velocity, move tasks, close sprint
2. Create `wizard/sprint-close-wizard-views.xml`:
   - Form showing incomplete tasks, target sprint selector, close button

### Step 11: Default Data (15 min)

1. Create `data/project-scrum-data.xml`:
   - Link `enable_scrum` config field to `group_project_scrum` (same pattern as `allow_milestones` -> `group_project_milestone`)

### Step 12: Testing & Validation (2h)

1. Install module on dev instance
2. Create test project, enable Scrum
3. Create sprint, assign tasks, verify board
4. Test planning wizard flow
5. Test close wizard flow
6. Verify security: regular user vs manager
7. Verify multi-company isolation
8. Write basic unit test `tests/test-project-sprint.py`

## Todo List

- [ ] Create module directory structure and scaffold files
- [ ] Implement security XML + ACL CSV
- [ ] Implement project.sprint model
- [ ] Implement project.task extension (sprint_id, story_points)
- [ ] Implement project.project extension (enable_scrum, sprint_ids)
- [ ] Create sprint form/list/kanban/search views
- [ ] Create sprint board action (task kanban filtered by sprint)
- [ ] Create product backlog action
- [ ] Create task view inheritance (form + kanban + search)
- [ ] Create project form inheritance (enable_scrum toggle + stat button)
- [ ] Create menu structure
- [ ] Implement sprint planning wizard + views
- [ ] Implement sprint close wizard + views
- [ ] Create default data XML
- [ ] Install and smoke test on dev instance
- [ ] Write unit tests

## Success Criteria

1. Module installs without errors on clean Odoo 18 CE
2. Enabling Scrum on a project shows sprint-related UI; disabling hides it
3. Sprint lifecycle works: create (draft) -> start (active) -> close (closed)
4. Only 1 active sprint per project enforced
5. Tasks can be assigned to sprint; backlog view shows unassigned tasks
6. Planning wizard assigns selected backlog tasks to sprint with capacity feedback
7. Close wizard snapshots velocity, moves incomplete tasks
8. Security: regular users can read sprints, managers can CRUD
9. Multi-company isolation works

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Task form xpath breaks on Odoo minor update | Low | High | Use stable xpath targets (field names, not positions); test on each update |
| `enable_scrum` -> group toggle race condition | Low | Low | Use `_onchange` or `res.config.settings` pattern |
| Sprint-task domain performance on large projects | Medium | Medium | Index on sprint_id (done via `index=True`); limit backlog view pagination |
| Kanban card story_points badge layout breaks | Low | Low | Use SCSS isolation; test responsive |

## Security Considerations

- Sprint CRUD restricted to `group_project_manager`
- Sprint read follows project privacy visibility (reuses existing record rule pattern)
- Multi-company isolation via `company_id` related field + ir.rule
- Wizard access for `group_project_user` (transient models, no persistent data risk)
- No portal write access to sprints (read-only for shared projects)
- `story_points` and `sprint_id` fields gated by `groups="project.group_project_scrum"`

## Next Steps

After Phase 1 completion:
- Phase 2 depends on: sprint model + task extension (for burndown/velocity data)
- Phase 2 can start immediately after Phase 1 smoke test passes

# Odoo 18 Project Module Internals: Scrum/Agile Extension Research

**Date:** 2026-03-18
**Status:** Complete
**Scope:** Analyze extension points, models, security, and existing Agile-mapped concepts in Odoo 18 project module

---

## Executive Summary

Odoo 18 project module has robust foundations for Scrum/Agile features. Core concepts (tasks, stages, milestones) are extensible, with well-defined security roles and inheritance patterns. Missing elements: sprint concept, story points, velocity tracking, sprint ceremonies metadata, and detailed agile metrics. The addon pattern (confirmed via ui_enhance_crm_sale) supports clean inheritance without core modifications.

---

## 1. Core Model Fields & Extension Points

### 1.1 Project (project.project)

**Key Fields:**
- `name` (Char, required, indexed trigram) - Project name
- `label_tasks` (Char, translatable, default "Tasks") - **Custom label support (e.g., "Stories")**
- `tasks` (One2many → project.task) - All tasks in project
- `task_ids` (One2many → project.task, filtered for open tasks)
- `type_ids` (Many2many → project.task.type) - Stages/workflow columns
- `milestone_ids` (One2many → project.milestone) - **Maps to sprints**
- `allow_task_dependencies` (Boolean) - Feature flag for task blocking
- `allow_milestones` (Boolean) - Feature flag for milestone use
- `tag_ids` (Many2many → project.tags) - Categorization
- `task_properties_definition` (PropertiesDefinition) - **Custom task fields support**
- `date_start`, `date` (Date) - Project timeline bounds
- `rating_active`, `rating_status` - Customer feedback system
- `update_ids` (One2many → project.update) - **Project status snapshots**
- `stage_id` (Many2one → project.project.stage) - Project lifecycle stage
- `privacy_visibility` (Selection: followers/employees/portal)
- `collaborator_ids` (One2many → project.collaborator) - **Project sharing/team**

**Extension Points:**
- Inherit `project.project` to add sprint-specific fields (sprint_duration, sprint_start_date, etc.)
- Use `task_properties_definition` to add story points, complexity, AC (Acceptance Criteria) as custom task fields
- Leverage `milestone_ids` one2many as sprints container
- Override `label_tasks` to "User Stories" or "Backlog Items"

**Security Groups:**
- `group_project_user` - Base access
- `group_project_manager` - Full access
- Multi-company rules enforce isolation

---

### 1.2 Task (project.task)

**Core Fields:**

| Field | Type | Key For Agile |
|-------|------|---------------|
| `name` | Char (required, trigram indexed) | Story title |
| `description` | Html | Story details/AC |
| `priority` | Selection (0/1 Low/High) | No, maps to complexity in Scrum |
| `state` | Selection (01_in_progress, 02_changes_requested, 03_approved, 1_done, 1_canceled, 04_waiting_normal) | Task workflow state |
| `stage_id` | Many2one → project.task.type | Kanban column/workflow |
| `project_id` | Many2one → project.project | Parent project |
| `user_ids` | Many2many → res.users | Assignees (team members) |
| `allocated_hours` | Float | **Time estimate (story points equivalent)** |
| `date_deadline` | Datetime | Deadline tracking |
| `date_assign` | Datetime | Readonly, assignment timestamp |
| `date_last_stage_update` | Datetime | Readonly, stage change timestamp |
| `tag_ids` | Many2many → project.tags | Epic/type classification |
| `parent_id` | Many2one → project.task | Parent task (epic/story hierarchy) |
| `child_ids` | One2many → project.task | Sub-tasks (story to tasks breakdown) |
| `subtask_count`, `closed_subtask_count` | Integer (computed) | Sub-task tracking |
| `milestone_id` | Many2one → project.milestone | Sprint assignment |
| `depend_on_ids` | Many2many (task_dependencies_rel) | **Task blocking (dependency tracking)** |
| `dependent_ids` | Many2many (inverse of depend_on_ids) | Tasks blocked by this |
| `recurring_task` | Boolean | Recurring task flag |
| `recurrence_id` | Many2one → project.task.recurrence | Recurrence pattern |
| `task_properties` | Properties (based on project definition) | **Custom fields per project** |
| `is_closed` | Boolean (computed) | Closed state indicator |
| `color` | Integer | Visual indicator |
| `active` | Boolean | Soft-delete flag |

**Computed/Related Fields:**
- `portal_user_names` - Portal user tracking
- `personal_stage_id` (Many2one → project.task.stage.personal) - Per-user kanban state
- `subtask_completion_percentage` - Computed from child states
- `working_hours_open`, `working_hours_close` - **Time tracking analytics**
- `working_days_open`, `working_days_close` - Business day analytics

**State Constants:**
```python
CLOSED_STATES = {'1_done': 'Done', '1_canceled': 'Cancelled'}
OPEN_STATES = complement of above
```

**Extension Points:**
- Inherit `project.task` to add Scrum fields: story_points, acceptance_criteria_ids, effort_estimate
- Use `task_properties` for sprint-specific custom fields (e.g., "Definition of Done checklist")
- Leverage `depend_on_ids` for sprint dependency visualization
- Override `allocated_hours` display to "Story Points"
- Extend state machine with Scrum-specific states (e.g., "Review", "Testing")

**Key Methods (Inheritance hooks):**
- `_compute_state()` - Determines state based on dependencies; override to add velocity-based auto-closure
- `_get_default_stage_id()` - Stage assignment on creation
- `stage_find()` - Stage discovery (overrideable)
- `_compute_display_name()` - Name parsing for quick shortcuts (@user, #tags, !)

**Portal Security Fields:**
- `SELF_READABLE_FIELDS` - Fields visible to portal users
- `SELF_WRITABLE_FIELDS` - Fields editable by portal users
- Custom via `project_sharing_chatter` controller

---

### 1.3 Milestone (project.milestone)

**Fields:**
- `name` (Char, required) - Milestone name
- `project_id` (Many2one → project.project, required, cascade delete) - Parent project
- `deadline` (Date) - Target completion date
- `is_reached` (Boolean) - Completion flag
- `reached_date` (Date, computed & stored) - Auto-set when marked done
- `task_ids` (One2many → project.task, related via milestone_id) - Associated tasks
- `task_count` (Integer, computed) - Task count
- `done_task_count` (Integer, computed) - Closed task count
- `can_be_marked_as_done` (Boolean, computed) - Auto-completion eligibility

**Computed Fields:**
- `is_deadline_exceeded` - Late detection
- `is_deadline_future` - Upcoming flag

**Methods:**
- `toggle_is_reached()` - Mark milestone complete (webhook for sprint closure)
- `action_view_tasks()` - Navigate to related tasks
- `_get_data()` / `_get_data_list()` - Serialization for JSON APIs

**Extension Points:**
- **Milestone IS the Sprint concept** - Map directly to Scrum sprints
- Inherit to add sprint fields: sprint_goal, retrospective_notes, sprint_velocity_target
- Use deadline as sprint end date
- Leverage task_ids relationship to gather sprint backlog
- Override toggle_is_reached() to trigger velocity calculations, retrospective workflows

---

### 1.4 Task Type / Stage (project.task.type)

**Fields:**
- `name` (Char, required, translatable) - Stage/workflow name
- `sequence` (Integer) - Kanban column order
- `project_ids` (Many2many → project.project) - Projects using this stage
- `active` (Boolean) - Soft-delete flag
- `fold` (Boolean) - Collapsed in kanban
- `mail_template_id` (Many2one → mail.template) - Auto-email on entry
- `rating_template_id` (Many2one → mail.template) - Auto-rating request on stage
- `auto_validation_state` (Boolean) - Auto-update state on customer feedback
- `user_id` (Many2one → res.users) - Personal stage owner (for user-specific workflows)
- `disabled_rating_warning` (Text, computed) - Warning if rating disabled

**Constraints:**
- Personal stages (user_id set) cannot be linked to projects
- Stage deletion triggers warning if tasks exist

**Extension Points:**
- Create custom stages for Agile states: "Backlog Ready", "In Review", "In Testing", "Demo Ready"
- Leverage `mail_template_id` to notify team on state changes (e.g., "Ready for Demo")
- Use `fold` to hide completed stages in kanban
- Inherit to add stage-type (feature, bug, technical debt) classification

---

### 1.5 Project Update (project.update)

**Fields:**
- `name` (Char, required) - Update title
- `status` (Selection: on_track/at_risk/off_track/on_hold/done) - Project status
- `color` (Integer, computed from status) - Visual indicator
- `progress` (Integer) - Manual progress percentage
- `progress_percentage` (Float, computed) - Progress as decimal
- `user_id` (Many2one → res.users) - Author
- `description` (Html) - Detailed narrative
- `date` (Date, default today) - Update date
- `project_id` (Many2one → project.project, required) - Parent
- `task_count` (Integer, readonly) - Snapshot of task count at update time
- `closed_task_count` (Integer, readonly) - Snapshot of closed tasks
- `closed_task_percentage` (Integer, computed) - Percentage closed

**Methods:**
- `_build_description()` - Auto-generate default description from project state
- `_get_milestone_values()` - Fetch milestone updates since last update
- `_get_last_updated_milestone()` - SQL-based milestone change detection

**Extension Points:**
- **Maps to sprint retrospective/review notes**
- Inherit to add: sprint_velocity_actual, sprint_burn_down_data, impediments_list
- Use `description` as sprint review summary
- Leverage milestone tracking for "completed milestones this sprint" dashboard
- Create views to show update history as velocity trend

---

## 2. Security & Access Control

### 2.1 Groups Hierarchy

```
group_project_manager (implied: group_project_user, group_user)
  ├─ Full CRUD on: project.project, project.task, project.task.type, project.milestone
  ├─ Can create/manage stages for all projects
  └─ Visible to public projects

group_project_user
  ├─ Read project.project (non-private)
  ├─ Read/write own assigned tasks
  ├─ Create new tasks in assigned projects
  └─ Cannot delete or manage settings

group_project_rating
  └─ Implies group_user
  └─ Can send/receive rating requests

group_project_milestone
  └─ Implies: access to milestone views/actions

group_project_task_dependencies
  └─ Implies: access to task blocking UI

group_project_stages
  └─ Implies: project stage management
```

### 2.2 Record Rules (ir.rule)

| Rule | Enforces | Impact |
|------|----------|--------|
| `project_comp_rule` | Multi-company isolation | Users see only company's projects |
| `project_public_members_rule` | Privacy visibility (followers-only) | Non-followers blocked from private projects |
| `task_comp_rule` | Multi-company task isolation | Tasks stay within company boundaries |
| `task_visibility_rule` | Follower-only task access | Employees blocked if not follower + non-manager |
| `project_manager_all_project_tasks_rule` | Managers see all linked or own tasks | No task hiding from managers |
| `task_type_visibility_rule` | Personal stages (user_id) scope | Users see own + shared stages |
| `ir_rule_private_task` | Private task access | Non-followers blocked, assignees can see own |
| `project_task_rule_portal` | Portal user access | Collaborators of shared projects only |
| `milestone_visibility_rule` | Milestone follower enforcement | Consistency with project privacy |
| `burndown_chart_*_rule` | Analytics access | Managers see all, users see assigned |

**Custom Access Fields:**
- `group_expand` on stage_id allows stages to show in kanban even if not used
- `@api.property` SELF_READABLE/WRITABLE_FIELDS on Task override field visibility per user

### 2.3 Implications for Agile Extension

- Create new group `group_project_scrum_master` (implied: group_project_manager)
- Add rule to restrict sprint retrospective editing to SM or manager
- Use `privacy_visibility` to enforce team access to sprints
- Leverage existing `collaborator_ids` for team membership tracking

---

## 3. View Structure & Extension Pattern

### 3.1 Task Views (project_task_views.xml)

**Existing Views:**
- `view_task_search_form_base` - Base search with filters for stage, milestone, tags, priority
- `view_task_search_form_project_fsm_base` - Adds user_ids filtering
- `view_task_search_form_project_base` - Adds deadline filters, grouping options
- `view_task_search_form` - Final view with activity overdue/today/upcoming
- `view_project_task_graph` - Bar chart: stage vs working_hours_open/close

**Extension Pattern:**
```xml
<record id="project.view_task_search_form_project_base" model="ir.ui.view">
  <field name="inherit_id" ref="project.view_task_search_form_project_base"/>
  <field name="priority">15</field>
  <field name="arch" type="xml">
    <!-- Use xpath to inject sprint filters -->
    <filter name="milestone" position="after">
      <filter string="Sprint" name="sprint_id" context="{'group_by': 'sprint_id'}" groups="project.group_project_scrum"/>
      <filter string="Story Points" name="story_points" context="{'group_by': 'story_points_estimate'}"/>
    </filter>
  </field>
</record>
```

### 3.2 Milestone Views (project_milestone_views.xml)

- `project_milestone_view_form` - Form with task stats button
- `project_milestone_view_tree` - Editable list with deadline/status decoration

**Directly Extensible** - Inheritable via:
```xml
<field name="inherit_id" ref="project.project_milestone_view_form"/>
```

### 3.3 Burndown Chart Report (project_task_burndown_chart_report.py/xml)

**Current Scope:**
- Abstract model: `project.task.burndown.chart.report`
- SQL-based CTE query: Tracks task state changes over time via mail_tracking_value
- Groups by date (month/week/day) and stage_id
- Computes: count, allocated_hours sum

**Queryable Fields:**
- allocated_hours (Float) - Total time on tasks in period
- date (Date) - Period date
- stage_id (Many2one) - Task stage for filtering
- is_closed (Selection: open/closed) - Task completion status
- state (Selection) - Task workflow state

**Extension Opportunity:**
- Model already supports custom computed fields
- Can add `velocity_actual` = count of closed tasks per sprint/period
- Create new report view for "Sprint Burndown" by filtering stage_id + milestone_id
- Add sprint velocity trendline via new fields

---

## 4. What Already Exists = Scrum Mapping

### 4.1 Direct Mappings

| Scrum Concept | Odoo Object | Fields | Status |
|---------------|-------------|--------|--------|
| **Sprint** | project.milestone | deadline, name, is_reached | ✓ Exists, fully extensible |
| **Sprint Backlog** | Tasks with milestone_id set | milestone_id (Many2one) | ✓ Exists |
| **User Story** | project.task | name, description, parent_id | ✓ Exists |
| **Sub-task** | project.task (parent_id) | child_ids, parent_id | ✓ Exists |
| **Workflow/State** | project.task.type (stage_id) | 6 built-in states | ✓ Exists |
| **Task Blocking** | depend_on_ids / dependent_ids | Many2many rel | ✓ Exists, UI partial |
| **Team** | project.collaborator + user_ids | collaborator_ids on project | ✓ Exists |
| **Burndown** | project.task.burndown.chart.report | Date + task state tracking | ✓ Exists |
| **Status Update** | project.update | status, progress, description | ✓ Exists, maps to sprint review |
| **Effort Tracking** | allocated_hours | Float on task | ✓ Exists (maps to story points) |

### 4.2 Partially Implemented

| Concept | Current | Gap |
|---------|---------|-----|
| **Task Priority** | Selection (0/1 Low/High) | Only binary; Scrum needs: Low/Medium/High/Critical |
| **Task Dependencies** | Exist but UI minimal | Need visual dependency graph, impediment tracking |
| **Recurring Tasks** | Support via recurrence_id | Not Scrum-aligned (for sprints = bad practice) |
| **Estimates** | allocated_hours (float) | No explicit "story points" field; no effort vs actual tracking |
| **Velocity** | Computable from burndown | No pre-computed velocity metric field |

### 4.3 Completely Missing = Must Build

| Scrum Feature | Why Needed | Impact |
|---------------|-----------|----|
| **Sprint Goal** | Guides team focus, DoD acceptance | Custom field on milestone |
| **Story Points** | Velocity tracking, capacity planning | Custom field on task (numeric, not hours) |
| **Acceptance Criteria** | Definition of done per story | Either task_properties or separate model |
| **Velocity Tracking** | Sprint metrics, planning confidence | Computed field aggregating closed story points per sprint |
| **Sprint Retrospective** | Team improvement ritual | Extend project.update or new model |
| **Impediments/Blockers** | Risk tracking | New model or depend_on_ids + blocker reason |
| **Sprint Planning Board** | Visual planning capability | New view type or kanban enhancement |
| **Commitment Metric** | Team accountability | Computed from planned vs closed story points |
| **Velocity Trend** | Release planning, forecast | Chart/report showing velocity per sprint |
| **Release/Epic Tracking** | Multi-sprint features | Parent milestone or new model |

---

## 5. Addon Pattern Reference (ui_enhance_crm_sale)

**Structure:**
```
ui_enhance_crm_sale/
├── __manifest__.py                    # Dependency declaration
├── __init__.py                        # Module init (usually empty)
├── views/
│   ├── crm-lead-views-inherit.xml    # Inherited view modifications
│   └── sale-order-views-inherit.xml  # Inherited view modifications
├── static/src/
│   ├── scss/
│   │   ├── _variables.scss           # Design tokens
│   │   ├── _mixins.scss              # Reusable styles
│   │   ├── common-enhance.scss       # Shared CSS
│   │   ├── crm-form-enhance.scss     # CRM-specific styles
│   │   ├── crm-kanban-enhance.scss   # CRM kanban styles
│   │   └── sale-*.scss               # Sale-specific styles
│   └── js/
│       ├── crm-kanban-enhance-patch.js  # JS patches
│       └── form-save-feedback-patch.js  # JS patches
```

**Manifest Pattern:**
```python
{
    'name': 'UI Enhancement Name',
    'version': '18.0.X.0.0',
    'category': 'Category',
    'summary': 'Brief description',
    'description': """
        Detailed features with markdown formatting
        - Feature 1
        - Feature 2
    """,
    'depends': ['base_module1', 'base_module2'],  # Minimal deps
    'data': [
        'views/view-file1-inherit.xml',          # View inheritance files
        'views/view-file2-inherit.xml',
    ],
    'assets': {
        'web.assets_backend': [                   # Frontend assets
            'addon_name/static/src/scss/variables.scss',
            'addon_name/static/src/scss/mixins.scss',
            'addon_name/static/src/scss/common.scss',
            'addon_name/static/src/scss/module1.scss',
            'addon_name/static/src/js/patches.js',
        ],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
```

**Key Principles:**
- Only inherit existing views (no new core model changes)
- Use xpath position="after/before/attributes" for safe modifications
- SCSS isolation via prefixed classes
- JS patches for behavioral changes, not model logic
- No direct modifications to base addon files

---

## 6. Database Schema: Key Relationships

```sql
-- Task to Task hierarchy (parent/child)
project_task.parent_id → project_task.id

-- Task to Stage (workflow)
project_task.stage_id → project_task_type.id

-- Task to Milestone (sprint membership)
project_task.milestone_id → project_milestone.id

-- Task dependencies (blocking)
task_dependencies_rel(task_id, depends_on_id) → project_task.id (self-join)

-- Task to Project
project_task.project_id → project_project.id

-- Stage to Project (many projects can share a stage)
project_task_type_rel(type_id, project_id)

-- Milestone to Project (one project owns milestones)
project_milestone.project_id → project_project.id (ondelete='cascade')

-- Task to Assignees (team members)
project_task_user_rel(task_id, user_id) → res.users.id

-- Task to Tags (categorization)
project_tags_project_task_rel(project_task_id, project_tags_id)

-- Project Updates (status snapshots)
project_update.project_id → project_project.id (ondelete='cascade')
```

**Indices:**
- project_task.stage_id (btree)
- project_task.project_id (btree)
- project_task.date_deadline (btree)
- project_task.milestone_id (btree_not_null)
- project_milestone.project_id (on delete cascade)

---

## 7. Extensibility Analysis

### 7.1 Inheritance-Ready Models (✓ Safe to extend)

- `project.project` - Clean inheritance, @api.depends calls override-friendly
- `project.task` - Extensive compute methods, state machine override hooks
- `project.milestone` - Lightweight, can add sprint-specific fields easily
- `project.task.type` - Simple CRUD, extensible

### 7.2 View Inheritance (✓ Safe and tested pattern)

- All views use xpath-based inheritance (position attribute)
- No conflicts with inheritance priority system
- Can target specific elements without overwriting entire view
- Safe to add new elements (filter, group, field) via position="after/before"

### 7.3 Security Rules (⚠ Requires care)

- New fields require ACL entries (ir.model.access.csv)
- New models need ir.rule records for multi-company/privacy
- Groups hierarchy is immutable (don't override group_project_manager)
- Create new groups as needed (e.g., group_project_scrum_master)

### 7.4 Report Models (✓ Extensible)

- project.task.burndown.chart.report is Abstract (_auto=False)
- Can create custom report models (burnup, velocity, etc.) following same SQL CTE pattern
- Existing report view system supports multi-report dashboards

---

## 8. API & Controller Access Points

**Task Quick-Creation Parser** (project.task._compute_display_name):
- `#tag` syntax for adding tags
- `@user` syntax for assigning
- `!` for high priority
- Can extend in custom module

**Portal Access** (controllers/portal.py):
- Task sharing via project collaborator_ids
- Custom portal views per privacy_visibility level
- Controllable field visibility via SELF_READABLE_FIELDS

**Chatter Tracking** (mail integration):
- All field changes tracked via mail_tracking_value
- Burndown report relies on this for history
- Extensible via tracking=True on custom fields

---

## 9. Critical Caveats & Constraints

1. **Milestone as Sprint:** Is conceptually correct but lacks sprint-specific fields. Must inherit and add.

2. **allocated_hours vs Story Points:** Currently conflated. Odoo treats as time estimate, Scrum uses for points. Need custom field to avoid confusion.

3. **Task States:** Built-in states (01_in_progress, 02_changes_requested, etc.) are stored as strings in DB. Changing them breaks existing data. Create custom states via custom addon, not inheritance.

4. **Burndown Report:** Uses complex SQL CTE. Custom velocity report should follow same pattern, not create ad-hoc queries.

5. **Privacy Visibility:** Tasks inherit project privacy. Cannot have task-level overrides. Plan team structure within privacy model.

6. **No Built-in Planning Board:** Kanban is stage-based. Sprint planning (backlog to sprint transfer) needs custom view or bulk action.

7. **Recurrence Model:** exists but incompatible with sprint planning (tasks should not repeat within sprints).

---

## 10. Recommended Extension Architecture

### Phase 1: Model Extensions (Inheritance)
```python
# in addon_name/models/project_scrum_sprint.py
class ProjectSprint(models.Model):
    _name = 'project.sprint'
    _description = 'Sprint'
    _inherit = 'project.milestone'  # Inherit milestone base

    # Add sprint-specific fields
    sprint_goal = fields.Char('Sprint Goal')
    sprint_velocity_target = fields.Integer('Target Velocity')
    sprint_velocity_actual = fields.Integer(compute='_compute_velocity')
    # ... etc
```

### Phase 2: Task Field Extensions
```python
# Extend project.task with story points
class ProjectTask(models.Model):
    _inherit = 'project.task'

    story_points = fields.Integer('Story Points')
    acceptance_criteria = fields.Html('Acceptance Criteria')
    # Use task_properties for custom sprint fields
```

### Phase 3: View Inheritance (Safe)
```xml
<!-- Inherit milestone form to add sprint goal field -->
<record id="project.project_milestone_view_form" model="ir.ui.view">
    <field name="inherit_id" ref="project.project_milestone_view_form"/>
    <field name="arch" type="xml">
        <field name="deadline" position="after">
            <field name="sprint_goal" groups="project.group_project_scrum_master"/>
        </field>
    </field>
</record>
```

### Phase 4: Reporting & Analytics
```python
# New report model for sprint metrics
class ProjectSprintBurndown(models.AbstractModel):
    _name = 'project.sprint.burndown.report'
    # SQL-based like existing burndown
```

---

## Unresolved Questions

1. **How to handle Story Points vs Allocated Hours?** Should we deprecate allocated_hours UI in favor of story_points on task form, or use both (hours for actual time tracking + points for estimation)?

2. **Velocity Computation Timing:** Should velocity be computed at sprint close or continuously? Affects if we store as snapshot or computed field.

3. **Acceptance Criteria Storage:** Create separate model (like task checklist) or use Html field in task description? Affects search/filtering capability.

4. **Sprint Planning UI:** Implement as kanban between project backlog and sprint, or as bulk action form? Affects UX significantly.

5. **Team Velocity Trends:** Should we create new report model or extend existing burndown? Existing pattern more robust but adds model.

6. **Retrospective Storage:** Store in project.update description or create dedicated model? Affects accessibility and metrics extraction.

7. **Multi-Sprint Epics:** How to track features spanning multiple sprints? Extend task parent/child or create new "epic" model level?

---

## Summary: Implementation-Ready Insights

✓ **Safe to Inherit:** project.project, project.task, project.milestone, project.task.type
✓ **Safe to View-Inherit:** All task, milestone, project views
✓ **Safe to Leverage:** depend_on_ids (blocking), collaborator_ids (team), burndown report
✓ **Must Build:** Sprint goal, story points custom field, velocity metrics, retrospective views
✓ **Use Pattern:** Follow ui_enhance_crm_sale for view + asset structure
⚠ **Avoid:** Modifying CLOSED_STATES, creating new states via inheritance (string DB storage issue)
⚠ **Plan Carefully:** Privacy model scope, allocated_hours naming collision, task state machine override


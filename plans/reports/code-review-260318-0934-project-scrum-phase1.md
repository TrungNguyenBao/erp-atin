# Code Review: project_scrum Phase 1

**Date:** 2026-03-18
**Reviewer:** code-reviewer agent
**Module:** `addons/project_scrum/`
**Scope:** Full module (21 files, ~650 LOC Python + ~500 LOC XML)
**Status:** Module installs successfully; reviewing for correctness, security, edge cases

---

## Overall Assessment

Solid first implementation. Good Odoo conventions, clean model design, proper use of stored computed fields, correct security group architecture. However, there is one **critical** bug (CLOSED_STATES type mismatch) and several medium-severity issues that should be addressed before production use.

---

## Critical Issues

### C1. CLOSED_STATES is a set of strings, but upstream is a dict - state matching will BREAK

**Files:** `models/project_sprint.py:7`, `wizard/sprint_close_wizard.py:8`

```python
# Module defines:
CLOSED_STATES = {'1_done', '1_canceled'}   # set of strings

# But upstream project.task (project_task.py:76-78) defines:
CLOSED_STATES = {
    '1_done': 'Done',
    '1_canceled': 'Cancelled',
}  # dict
```

The module's set works for `in` checks (`t.state in CLOSED_STATES`) because Python `in` on a dict checks keys. So functionally this is **correct today**. However:

1. It duplicates a magic constant instead of importing from `odoo.addons.project.models.project_task`.
2. If upstream ever changes state keys, this breaks silently.
3. Misleading comment says "Import CLOSED_STATES" but it's actually re-defining it.

**Fix:** Import from upstream:
```python
from odoo.addons.project.models.project_task import CLOSED_STATES
```

**Severity reclassified: HIGH** (not critical since behavior is currently correct, but a maintenance time bomb).

---

## High Priority Issues

### H1. Task form xpath uses `parent.enable_scrum` which won't resolve outside embedded forms

**File:** `views/project-task-views-inherit.xml:13`

```xml
<field name="story_points"
       invisible="not project_id or not parent.enable_scrum"/>
```

`parent.enable_scrum` only works when the task form is embedded inside a parent form (e.g., sprint form's `task_ids` One2many). When the task form is opened standalone (from task list/kanban), `parent` is undefined and this will either error or always hide the field.

**Fix:** Use a related field or check a different condition:
```python
# In project_task_scrum.py, add:
enable_scrum = fields.Boolean(related='project_id.enable_scrum', readonly=True)
```
```xml
<field name="story_points"
       invisible="not project_id or not enable_scrum"/>
```

### H2. `_compute_active_sprint_id` uses `search()` inside a loop - N+1 query

**File:** `models/project_project_scrum.py:26-29`

```python
for project in self:
    project.active_sprint_id = self.env['project.sprint'].search([
        ('project_id', '=', project.id),
        ('state', '=', 'active'),
    ], limit=1)
```

For batch operations (e.g., loading project list), this fires one SQL query per project.

**Fix:** Use `read_group` or a single search with grouping:
```python
@api.depends('sprint_ids.state')
def _compute_active_sprint_id(self):
    active_sprints = self.env['project.sprint'].search([
        ('project_id', 'in', self.ids),
        ('state', '=', 'active'),
    ])
    sprint_map = {s.project_id.id: s for s in active_sprints}
    for project in self:
        project.active_sprint_id = sprint_map.get(project.id, False)
```

### H3. `set_values()` in res.config.settings searches ALL projects - unbounded write

**File:** `models/res_config_settings.py:16-20`

```python
projects = self.env['project.project'].search([])
```

On large Odoo instances with thousands of projects, this writes to every single project record when toggling the Scrum setting. This is both a performance issue and a logic issue (it overwrites per-project scrum preferences).

**Fix:** Only sync when disabling (to turn off scrum on all projects). When enabling, let the per-project toggle remain as-is:
```python
def set_values(self):
    was_enabled = self.env.user.has_group('project_scrum.group_project_scrum')
    super().set_values()
    if was_enabled and not self.group_project_scrum:
        # Only bulk-disable when turning off globally
        self.env['project.project'].search([
            ('enable_scrum', '=', True)
        ]).write({'enable_scrum': False})
```

Also note: `super().set_values()` should be called AFTER the check but the current code calls it at the end, which means `has_group` check happens before the group is actually toggled. This is correct ordering but fragile - better to call super first and compare differently.

### H4. Sprint planning wizard allows assigning to `draft` sprints only, but `action_plan_sprint` doesn't check state

**File:** `wizard/sprint_planning_wizard.py:13` vs `models/project_sprint.py:109-119`

The wizard domain restricts to `state == 'draft'`, but there's no server-side validation in `action_assign()`. A crafted RPC call could bypass the domain filter and assign tasks to any sprint.

**Fix:** Add validation in `action_assign()`:
```python
def action_assign(self):
    self.ensure_one()
    if self.sprint_id.state == 'closed':
        raise UserError(_('Cannot assign tasks to a closed sprint.'))
    ...
```

### H5. Missing `mail` in `depends` list

**File:** `__manifest__.py:18`

The model inherits `mail.thread` and `mail.activity.mixin` (in `project_sprint.py:19`) but only declares `project` as a dependency. While `project` transitively depends on `mail`, the Odoo convention is to explicitly declare all directly used dependencies.

**Fix:** Add `'mail'` to depends:
```python
'depends': ['project', 'mail'],
```

---

## Medium Priority Issues

### M1. Kanban xpath target `//field[@name='tag_ids']` may match multiple nodes

**File:** `views/project-task-views-inherit.xml:65`

In the task kanban template, `tag_ids` appears as a `<field>` element. The xpath `//field[@name='tag_ids']` should match correctly since it's within the kanban `<templates>` block. However, if another module adds a `tag_ids` field elsewhere in the kanban, this could match the wrong node.

**Recommendation:** More specific xpath if issues arise: `//t[@t-name='card']//field[@name='tag_ids']`

### M2. `completion_percentage` is Float but computed as integer-like value

**File:** `models/project_sprint.py:53-54, 81-82`

The field is `Float` but the computation `completed / committed * 100` produces a value like `66.66666...`. This is fine for display but consider rounding:
```python
sprint.completion_percentage = round((completed / committed * 100), 1) if committed else 0
```

### M3. No `_check_company` on sprint model

**File:** `models/project_sprint.py`

The `company_id` is a related stored field from `project_id.company_id`, but there's no `_check_company` to validate multi-company consistency when tasks from different companies could theoretically be assigned.

**Fix:**
```python
_check_company_auto = True
```

### M4. Sprint stat button on project form doesn't filter by project

**File:** `views/project-project-views-inherit.xml:20-27`

The stat button uses `action_view_all_sprints` which shows ALL sprints across all projects. It should filter to the current project.

**Fix:** Use a Python action method instead:
```python
def action_view_project_sprints(self):
    self.ensure_one()
    return {
        'name': _('Sprints'),
        'type': 'ir.actions.act_window',
        'res_model': 'project.sprint',
        'view_mode': 'list,kanban,form',
        'domain': [('project_id', '=', self.id)],
        'context': {'default_project_id': self.id},
    }
```

### M5. `_compute_sprint_count` not using `search_count` or `read_group`

**File:** `models/project_project_scrum.py:32-34`

```python
project.sprint_count = len(project.sprint_ids)
```

This prefetches all sprint records just to count them. For display-only stat buttons, use:
```python
sprint_data = self.env['project.sprint']._read_group(
    [('project_id', 'in', self.ids)],
    groupby=['project_id'],
    aggregates=['__count'],
)
count_map = {p.id: c for p, c in sprint_data}
for project in self:
    project.sprint_count = count_map.get(project.id, 0)
```

### M6. Sprint close wizard doesn't prevent closing sprint with zero tasks

**File:** `wizard/sprint_close_wizard.py:50-70`

Closing an empty sprint will set `velocity = 0` and state to `closed`. This is technically valid but may produce misleading velocity data. Consider a warning.

### M7. `backlog_task_ids` domain uses `is_closed` but field visibility depends on scrum group

**File:** `wizard/sprint_planning_wizard.py:23-25`

The `is_closed` field is from base `project.task` - correct. But the domain doesn't filter by `project_id.enable_scrum`, so tasks from non-scrum projects could technically appear if manually invoked. Low risk since wizard is opened from sprint context.

### M8. No `index=True` on `is_in_backlog` stored computed field

**File:** `models/project_task_scrum.py:18-20`

The `is_in_backlog` field is used in the backlog action domain filter. Without an index, queries will be slower on large task tables.

**Fix:** Add `index=True` to `is_in_backlog`.

---

## Low Priority Issues

### L1. `data/project-scrum-data.xml` is empty placeholder

**File:** `data/project-scrum-data.xml`

Either add useful demo/default data or remove the file and its manifest entry.

### L2. Kanban view uses `o_kanban_mobile` class

**File:** `views/project-sprint-views.xml:108`

`o_kanban_mobile` forces mobile layout. Consider if this is intentional or should be standard kanban.

### L3. `_compute_display_name` uses f-string directly

**File:** `models/project_sprint.py:160-161`

Works fine, but if `project_id` is empty (shouldn't happen due to `required=True`), this would show `[False] name`. Edge case is protected by the required constraint.

### L4. Wizard models missing `_rec_name` declaration

Minor - default `display_name` works for transient models used only in dialogs.

### L5. `portal` group gets read access to sprints but no portal views exist

**File:** `security/ir.model.access.csv:4`

Portal users can read sprint data but there are no portal templates to display it. Either remove portal ACL or plan portal views for a later phase.

---

## Positive Observations

1. **Clean model design** - proper `_inherit` pattern, good field choices, correct use of `ondelete='cascade'`
2. **Good security architecture** - hidden group, multi-company record rules, follower-based visibility, manager override
3. **SQL constraint** for date validation - prevents invalid data at DB level
4. **Single active sprint constraint** - well-implemented with `search_count` and proper error message
5. **Stored computed fields** with correct `@api.depends` triggers
6. **Proper tracking** on key fields for chatter history
7. **Well-structured XML** - correct use of `noupdate=1` for record rules, proper view inheritance IDs
8. **Wizard pattern** is clean - both planning and close wizards follow Odoo conventions
9. **Kebab-case file naming** for XML files aligns with project conventions

---

## Recommended Actions (Priority Order)

1. **Fix H1** - `parent.enable_scrum` xpath issue (will break standalone task form)
2. **Fix H2** - N+1 query in `_compute_active_sprint_id`
3. **Fix C1/H1** - Import `CLOSED_STATES` from upstream instead of redefining
4. **Fix M4** - Sprint stat button should filter by project
5. **Fix H3** - Unbounded project write in `set_values()`
6. **Fix H4** - Add server-side state validation in wizard actions
7. **Fix M8** - Add index on `is_in_backlog`
8. **Fix H5** - Add `mail` to manifest depends
9. **Fix M5** - Use `_read_group` for sprint count

---

## Metrics

| Metric | Value |
|--------|-------|
| Python files | 8 |
| XML files | 10 |
| Python LOC | ~200 |
| XML LOC | ~450 |
| Models | 4 (1 new + 3 inherited) |
| Wizards | 2 |
| Security rules | 3 record rules + 5 ACL lines |
| Critical issues | 0 |
| High issues | 5 |
| Medium issues | 8 |
| Low issues | 5 |

---

## Unresolved Questions

1. Is portal sprint read access intentional for Phase 1, or should it be deferred until portal views exist?
2. Should `story_points` enforce Fibonacci values via constraint, or leave it free-form as currently implemented?
3. The sprint board shows tasks from ALL active sprints across projects - is this the desired behavior, or should it filter by a specific project context?
4. Should `enable_scrum` default to `True` when the group is active (current behavior via `has_group` lambda), or default to `False` requiring manual opt-in per project?

# Phase 2: Analytics & Ceremonies

## Context Links

- [Plan Overview](plan.md)
- [Phase 1: Foundation](phase-01-foundation-sprint-model-and-boards.md)
- [Odoo Project Internals Report](../reports/researcher-260318-0856-odoo-project-internals.md)
- Existing burndown report: `addons/project/report/project_task_burndown_chart_report.py`
- Existing burndown views: `addons/project/report/project_task_burndown_chart_report_views.xml`

## Overview

- **Priority:** P2 -- High
- **Status:** Pending
- **Effort:** ~10h
- **Depends on:** Phase 1 complete (sprint model, task extension)
- **Description:** Sprint burndown chart, velocity tracking, sprint review/retrospective artifacts, daily standup quick-view

## Key Insights

1. Odoo 18 has `project.task.burndown.chart.report` -- Abstract model using SQL CTE on `mail_tracking_value`. Complex approach. For sprint burndown we use a simpler daily snapshot model via cron.
2. Velocity = completed_points at sprint close. Already captured in Phase 1 `sprint.velocity` field. This phase adds the chart visualization.
3. OWL components with Chart.js are the standard for Odoo 18 graph widgets (see `project/static/src/views/burndown_chart/`).
4. Sprint review/retrospective are lightweight -- text fields on sprint model + dedicated form views. No new model needed.
5. Daily standup is a filtered task view, not a new model.

## Requirements

### Functional
- F1: Sprint burndown chart showing daily remaining points vs ideal burn line
- F2: Daily snapshot cron job recording remaining_points per sprint per day
- F3: Velocity chart showing completed points per closed sprint (bar chart + 3-sprint rolling avg line)
- F4: Sprint review form: completed items summary, stakeholder feedback text area
- F5: Sprint retrospective form: what went well / what didn't / action items
- F6: Daily standup view: compact task cards grouped by assignee, showing task name + stage + blocker flag
- F7: Sprint summary dashboard: key metrics (committed vs completed, completion %, velocity trend)

### Non-Functional
- NF1: Burndown chart renders in < 2s for sprints with up to 200 tasks
- NF2: Cron runs daily at 00:05 server time; no performance impact
- NF3: Charts use Chart.js via OWL (consistent with Odoo 18 patterns)
- NF4: All files < 200 lines

## Architecture

### New Model: Sprint Daily Log (`models/project-sprint-daily-log.py`)

```python
class ProjectSprintDailyLog(models.Model):
    _name = 'project.sprint.daily.log'
    _description = 'Sprint Daily Snapshot'
    _order = 'date asc'
    _rec_name = 'date'

    sprint_id = fields.Many2one('project.sprint', required=True, ondelete='cascade', index=True)
    project_id = fields.Many2one(related='sprint_id.project_id', store=True)
    date = fields.Date(required=True, index=True)
    remaining_points = fields.Integer(string='Remaining Points')
    completed_points = fields.Integer(string='Completed Points')
    total_tasks = fields.Integer()
    closed_tasks = fields.Integer()

    _sql_constraints = [
        ('unique_sprint_date', 'UNIQUE(sprint_id, date)', 'One snapshot per sprint per day.'),
    ]
```

**Cron job** (`data/project-scrum-data.xml`):
- Model: `project.sprint.daily.log`
- Method: `_cron_create_daily_snapshots()`
- Interval: 1 day, at 00:05
- Logic: For each active sprint, create/update today's log entry with current remaining/completed points

### Sprint Model Extensions for Ceremonies (`models/project-sprint.py` additions)

```python
# Add to existing project.sprint model (Phase 1 file)
# Review fields
review_notes = fields.Html(string='Sprint Review Notes',
    help='Summary of completed items and stakeholder feedback')
review_date = fields.Datetime(string='Review Date')

# Retrospective fields
retro_went_well = fields.Html(string='What Went Well')
retro_went_wrong = fields.Html(string='What Could Improve')
retro_action_items = fields.Html(string='Action Items')
retro_date = fields.Datetime(string='Retrospective Date')
```

These fields are added to the existing sprint model file from Phase 1. No new model needed -- keeps it under 200 lines by using Html fields instead of child models.

### Burndown Report Model (`report/sprint-burndown-report.py`)

```python
class SprintBurndownReport(models.AbstractModel):
    _name = 'project.sprint.burndown.report'
    _description = 'Sprint Burndown Report'
    _auto = False

    sprint_id = fields.Many2one('project.sprint')
    date = fields.Date()
    remaining_points = fields.Integer()
    ideal_points = fields.Float()

    def init(self):
        # SQL view joining sprint_daily_log with ideal line computation
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    l.id,
                    l.sprint_id,
                    l.date,
                    l.remaining_points,
                    -- ideal line: linear from capacity to 0
                    s.capacity_points * (1.0 -
                        (l.date - s.start_date)::float /
                        GREATEST((s.end_date - s.start_date)::float, 1)
                    ) as ideal_points
                FROM project_sprint_daily_log l
                JOIN project_sprint s ON s.id = l.sprint_id
            )
        """ % self._table)
```

### Velocity Report Model (`report/sprint-velocity-report.py`)

```python
class SprintVelocityReport(models.AbstractModel):
    _name = 'project.sprint.velocity.report'
    _description = 'Sprint Velocity Report'
    _auto = False

    sprint_id = fields.Many2one('project.sprint')
    project_id = fields.Many2one('project.project')
    sprint_name = fields.Char()
    end_date = fields.Date()
    velocity = fields.Integer()
    rolling_avg_3 = fields.Float(string='3-Sprint Rolling Average')

    def init(self):
        # SQL view with window function for rolling average
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    s.id,
                    s.id as sprint_id,
                    s.project_id,
                    s.name as sprint_name,
                    s.end_date,
                    s.velocity,
                    AVG(s.velocity) OVER (
                        PARTITION BY s.project_id
                        ORDER BY s.end_date
                        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
                    ) as rolling_avg_3
                FROM project_sprint s
                WHERE s.state = 'closed' AND s.velocity > 0
                ORDER BY s.end_date
            )
        """ % self._table)
```

### OWL Components

#### Burndown Chart Widget (`static/src/js/sprint-burndown-chart.js`)

OWL component wrapping Chart.js line chart:
- X-axis: dates from sprint start to end
- Y-axis: story points
- Two lines: "Remaining" (actual from daily log) + "Ideal" (linear descent)
- Tooltip showing date, remaining, ideal, delta
- Color: blue for actual, gray dashed for ideal, red zone when actual > ideal

Follows pattern from `project/static/src/views/burndown_chart/`.

#### Velocity Chart Widget (`static/src/js/sprint-velocity-chart.js`)

OWL component wrapping Chart.js bar+line chart:
- X-axis: sprint names (chronological)
- Y-axis: story points
- Bars: velocity per sprint
- Line: 3-sprint rolling average
- Filtered by project_id

### Views

#### Burndown Chart View (`report/sprint-burndown-report-views.xml`)

Graph view on `project.sprint.burndown.report`:
- Type: line
- Measure: remaining_points, ideal_points
- Group: date (day)
- Filter: sprint_id (default = active sprint)

Custom OWL widget registered as alternative to standard graph for richer UX.

#### Velocity Chart View (`report/sprint-velocity-report-views.xml`)

Graph view on `project.sprint.velocity.report`:
- Type: bar
- Measure: velocity
- Group: sprint_name
- Filter: project_id

#### Sprint Review Tab (inherit `project-sprint-views.xml`)

Add notebook page to sprint form:
```xml
<page string="Review" name="review" invisible="state == 'draft'">
    <group>
        <field name="review_date"/>
        <field name="review_notes" placeholder="Summarize completed work and stakeholder feedback..."/>
    </group>
</page>
```

#### Sprint Retrospective Tab

Add notebook page to sprint form:
```xml
<page string="Retrospective" name="retrospective" invisible="state != 'closed'">
    <group>
        <field name="retro_date"/>
    </group>
    <group string="What Went Well">
        <field name="retro_went_well" nolabel="1"/>
    </group>
    <group string="What Could Improve">
        <field name="retro_went_wrong" nolabel="1"/>
    </group>
    <group string="Action Items">
        <field name="retro_action_items" nolabel="1"/>
    </group>
</page>
```

#### Daily Standup View

Action: `action_daily_standup` -- task list filtered by:
- `sprint_id = active_sprint_id` of current project
- `state not in CLOSED_STATES`
- Group by: `user_ids`

Compact list showing: task name, stage_id, story_points, priority indicator.
Add to Scrum menu: "Daily Standup" (sequence=5, first item).

## Related Code Files

### Files to CREATE

| File | Purpose | Est. Lines |
|------|---------|-----------|
| `models/project-sprint-daily-log.py` | Daily snapshot model + cron method | 80 |
| `report/__init__.py` | Report init | 4 |
| `report/sprint-burndown-report.py` | Burndown SQL view | 60 |
| `report/sprint-burndown-report-views.xml` | Burndown graph view + action | 50 |
| `report/sprint-velocity-report.py` | Velocity SQL view | 50 |
| `report/sprint-velocity-report-views.xml` | Velocity graph view + action | 50 |
| `static/src/js/sprint-burndown-chart.js` | OWL burndown widget | 150 |
| `static/src/js/sprint-velocity-chart.js` | OWL velocity widget | 120 |
| `static/src/xml/sprint-burndown-chart.xml` | QWeb template | 30 |
| `static/src/xml/sprint-velocity-chart.xml` | QWeb template | 30 |
| `static/src/scss/sprint-board.scss` | Sprint-specific styles | 60 |

### Files to MODIFY (from Phase 1)

| File | Changes |
|------|---------|
| `models/__init__.py` | Add import for daily-log |
| `models/project-sprint.py` | Add review/retro fields (~20 lines) |
| `__manifest__.py` | Add report files, assets, cron data |
| `views/project-sprint-views.xml` | Add Review + Retrospective notebook tabs |
| `views/project-scrum-menus.xml` | Add Daily Standup, Burndown, Velocity menu items |
| `security/ir.model.access.csv` | Add ACL for daily.log + report models |
| `data/project-scrum-data.xml` | Add cron job record |

## Implementation Steps

### Step 1: Daily Log Model (1h)

1. Create `models/project-sprint-daily-log.py`
2. Add `_cron_create_daily_snapshots()`:
   - Search active sprints
   - For each: compute remaining/completed points from task_ids
   - Create or update daily log record for today
3. Add cron record to `data/project-scrum-data.xml`
4. Update `models/__init__.py`, `__manifest__.py`
5. Compile check

### Step 2: Ceremony Fields on Sprint (30 min)

1. Add review + retrospective fields to `models/project-sprint.py`
2. Add Review and Retrospective tabs to `views/project-sprint-views.xml`
3. Compile check

### Step 3: Burndown Report (2h)

1. Create `report/__init__.py`
2. Create `report/sprint-burndown-report.py` (SQL view)
3. Create `report/sprint-burndown-report-views.xml` (graph view + search + action)
4. Update `__manifest__.py` with report data files
5. Update ACL CSV
6. Compile + test with sample data

### Step 4: Velocity Report (1.5h)

1. Create `report/sprint-velocity-report.py` (SQL view with window function)
2. Create `report/sprint-velocity-report-views.xml`
3. Update `__manifest__.py`, ACL CSV
4. Compile + test

### Step 5: OWL Burndown Widget (2h)

1. Create `static/src/js/sprint-burndown-chart.js` -- OWL component
2. Create `static/src/xml/sprint-burndown-chart.xml` -- QWeb template
3. Register as field widget or standalone view component
4. Reference pattern: `addons/project/static/src/views/burndown_chart/`
5. Update `__manifest__.py` assets section

### Step 6: OWL Velocity Widget (1.5h)

1. Create `static/src/js/sprint-velocity-chart.js`
2. Create `static/src/xml/sprint-velocity-chart.xml`
3. Update assets

### Step 7: Standup View + Menus (1h)

1. Create daily standup action in `views/project-sprint-board-views.xml` or new file
2. Add menu items: Daily Standup, Burndown Chart, Velocity Chart under Scrum > Reporting
3. Update menu structure

### Step 8: SCSS + Polish (30 min)

1. Create `static/src/scss/sprint-board.scss`:
   - Sprint card styles for kanban
   - Capacity bar progress styling
   - Story points badge on task cards
   - Burndown/velocity chart container styles

### Step 9: Testing (1h)

1. Create sprint with tasks, close sprint to generate velocity
2. Verify cron creates daily snapshots
3. Verify burndown chart renders correctly
4. Verify velocity chart shows historical data
5. Test review/retro form save and display
6. Test standup view filtering

## Todo List

- [ ] Create sprint daily log model + cron method
- [ ] Add cron job record to data XML
- [ ] Add review/retro fields to sprint model
- [ ] Add Review + Retrospective tabs to sprint form
- [ ] Create burndown report SQL view + graph view
- [ ] Create velocity report SQL view + graph view
- [ ] Create OWL burndown chart widget
- [ ] Create OWL velocity chart widget
- [ ] Create daily standup action/view
- [ ] Add reporting menu items
- [ ] Create sprint board SCSS
- [ ] Update manifest with new files + assets
- [ ] Update ACL for new models
- [ ] Smoke test all charts with sample data

## Success Criteria

1. Daily cron creates snapshot records for active sprints
2. Burndown chart shows remaining vs ideal line for any sprint
3. Velocity chart shows bar per closed sprint + rolling average line
4. Review/retrospective forms save and display on sprint record
5. Standup view shows active sprint tasks grouped by assignee
6. All report views load in < 2s for 200-task sprints
7. Charts render correctly in Odoo 18 backend

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Chart.js version incompatibility with Odoo 18 bundled version | Low | High | Use Odoo's bundled Chart.js; check version in web module assets |
| SQL view breaks on PostgreSQL version differences | Low | Medium | Use standard SQL; test on PG 14+ |
| Cron job missing days (server downtime) | Medium | Low | Backfill logic: check for gaps, fill from task state at that date |
| OWL component registration conflicts | Low | Medium | Use unique component name prefix `SprintBurndown`, `SprintVelocity` |

## Security Considerations

- Daily log model: read for group_project_user, write for group_project_manager
- Report models (Abstract, _auto=False): read-only access for group_project_user
- Review/retro fields: writable by anyone who can write sprint (group_project_manager)
- No sensitive data in charts -- only aggregated point counts

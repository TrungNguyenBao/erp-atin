# Phase 4: OWL Burndown & Velocity Charts

## Context Links

- [Plan Overview](plan.md)
- [Phase 2: Wireframes](phase-02-wireframe-ui-ux-design.md)
- [Phase 3: Sprint Board](phase-03-owl-sprint-board.md)
- Existing burndown SQL report: `addons/project_scrum/report/sprint_burndown_report.py`
- Existing velocity SQL report: `addons/project_scrum/report/sprint_velocity_report.py`
- Odoo 18 burndown chart pattern: `addons/project/static/src/views/burndown_chart/`
- Odoo Chart.js usage: `addons/web/static/lib/Chart/`

## Overview

- **Priority:** P0/P1
- **Status:** Completed
- **Effort:** ~8h
- **Depends on:** Phase 2 (shares OWL patterns + asset pipeline)
- **Description:** Interactive Chart.js-based OWL widgets for sprint burndown and velocity tracking. Complement existing SQL report views with rich client-side charts.

## Requirements

### Functional

- F1: Burndown chart -- line chart showing remaining SP vs ideal burn line per day
- F2: X-axis = sprint days (date_start to date_end), Y-axis = story points
- F3: Ideal line = straight line from total_sp to 0
- F4: Actual line = from `sprint.daily.log` data
- F5: Velocity chart -- bar chart comparing committed vs completed SP per sprint
- F6: Rolling average line overlaid on velocity bars
- F7: Both charts accessible from Sprint form, Dashboard, and standalone menu

### Non-Functional

- NF1: Use Odoo-bundled Chart.js (no external CDN)
- NF2: Charts render in <1s for typical sprint data (14-30 days)
- NF3: Responsive sizing (chart fills container)
- NF4: Tooltips on hover with exact values

## Architecture

### Burndown Chart Data Flow

```
sprint.daily.log records → get_burndown_data() RPC → BurndownChart OWL → Chart.js line chart
```

```python
# On project.sprint model
def get_burndown_data(self):
    self.ensure_one()
    logs = self.env['project.sprint.daily.log'].search([
        ('sprint_id', '=', self.id)
    ], order='date asc')
    
    total_sp = self.committed_points or self.total_story_points
    days = (self.end_date - self.start_date).days + 1
    
    return {
        'labels': [log.date.strftime('%m/%d') for log in logs],
        'actual': [log.remaining_points for log in logs],
        'ideal': [total_sp - (total_sp / days * i) for i in range(days + 1)],
        'ideal_labels': [(self.start_date + timedelta(days=i)).strftime('%m/%d') for i in range(days + 1)],
        'sprint_name': self.name,
        'total_sp': total_sp,
    }
```

### Velocity Chart Data Flow

```
Sprint records (closed) → get_velocity_data() RPC → VelocityChart OWL → Chart.js bar chart
```

```python
# On project.project model
def get_velocity_data(self, limit=6):
    sprints = self.env['project.sprint'].search([
        ('project_id', '=', self.id),
        ('state', '=', 'closed'),
    ], order='end_date desc', limit=limit)
    
    sprints_sorted = sprints.sorted('end_date')
    velocities = [s.velocity for s in sprints_sorted]
    
    return {
        'labels': [s.name for s in sprints_sorted],
        'committed': [s.committed_points for s in sprints_sorted],
        'completed': [s.completed_points for s in sprints_sorted],
        'rolling_avg': self._compute_rolling_avg(velocities, window=3),
    }
```

### OWL Widget Pattern

```javascript
/** @odoo-module **/
import { Component, onMounted, useRef } from "@odoo/owl";
import { loadJS } from "@web/core/assets";

class BurndownChart extends Component {
    static template = "project_scrum.BurndownChart";
    static props = { sprintId: Number };

    setup() {
        this.orm = useService("orm");
        this.canvasRef = useRef("canvas");
        this.chart = null;
        onMounted(() => this.renderChart());
    }

    async renderChart() {
        const data = await this.orm.call(
            "project.sprint", "get_burndown_data", [this.props.sprintId]
        );
        const ctx = this.canvasRef.el.getContext("2d");
        this.chart = new Chart(ctx, {
            type: "line",
            data: { /* ... */ },
            options: { responsive: true, maintainAspectRatio: false },
        });
    }
}
```

## Implementation Steps

### Step 1: Burndown data RPC (~1h)

- [ ] Add `get_burndown_data()` to `project_sprint.py`
- [ ] Handle edge cases: no daily logs yet, sprint not started, zero SP
- [ ] Compute ideal line from total_sp over sprint duration

### Step 2: BurndownChart OWL component (~2.5h)

- [ ] Create `static/src/js/burndown-chart.js`
- [ ] Import Chart.js from `@web/core/assets` or `web.libs`
- [ ] Implement `renderChart()` with line chart config:
  - Ideal line: dashed blue
  - Actual line: solid green (below ideal = good) / solid red (above ideal = behind)
- [ ] Create `static/src/xml/burndown-chart.xml` template
- [ ] Add chart container with proper sizing

### Step 3: Velocity data RPC (~1h)

- [ ] Add `get_velocity_data(limit=6)` to `project_project_scrum.py`
- [ ] Compute rolling average (window=3)
- [ ] Handle edge cases: <3 sprints, no closed sprints

### Step 4: VelocityChart OWL component (~2.5h)

- [ ] Create `static/src/js/velocity-chart.js`
- [ ] Bar chart config:
  - Committed SP: light blue bars
  - Completed SP: dark blue bars (grouped)
  - Rolling average: orange line overlay
- [ ] Create `static/src/xml/velocity-chart.xml` template
- [ ] Tooltip showing committed, completed, difference

### Step 5: Integration & registration (~1h)

- [ ] Register both as reusable OWL components (not standalone actions)
- [ ] Add Burndown chart to Sprint form view (notebook tab or inline widget)
- [ ] Add Velocity chart to Project Scrum settings page
- [ ] Update `__manifest__.py` assets
- [ ] Standalone chart actions for menu access (optional)

## Risks

| Risk | Mitigation |
|------|------------|
| Chart.js import path varies by Odoo version | Check `addons/web/static/lib/Chart/` exists; fallback to `loadJS` |
| Daily log gaps (cron missed days) | Interpolate missing days in `get_burndown_data()` |
| Canvas sizing issues in OWL lifecycle | Use `onMounted` + `onPatched` for re-render on resize |

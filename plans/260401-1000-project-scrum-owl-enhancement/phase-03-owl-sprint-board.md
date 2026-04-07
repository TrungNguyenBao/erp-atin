# Phase 3: OWL Sprint Board Component

## Context Links

- [Plan Overview](plan.md)
- [Phase 1: Ceremony & Security](phase-01-ceremony-model-and-security.md)
- [Phase 2: Wireframes](phase-02-wireframe-ui-ux-design.md)
- Odoo 18 OWL patterns: `addons/web/static/src/views/`
- Existing Sprint Board view: `addons/project_scrum/views/project-sprint-board-views.xml`
- Odoo kanban controller: `addons/web/static/src/views/kanban/`
- Task stages: `addons/project/models/project_task_type.py`

## Overview

- **Priority:** P0 -- Critical
- **Status:** Completed
- **Effort:** ~10h
- **Depends on:** Phase 1 (security groups for board access)
- **Description:** Interactive Sprint Board OWL component with drag-drop task movement between stage columns, sprint selector, task cards with story points, WIP limits

## Requirements

### Functional

- F1: Kanban-style board with columns per task stage (To Do, In Progress, Review, Done)
- F2: Drag-and-drop tasks between columns updates `stage_id` via ORM
- F3: Sprint selector dropdown in header switches between sprints
- F4: Task cards show: title, assignee avatar, story points badge, task type icon, blocked indicator
- F5: Column headers show task count and total story points
- F6: WIP (Work In Progress) limit indicator -- highlight column when task count exceeds limit
- F7: Backlog panel (collapsible sidebar) shows unassigned tasks for quick assignment

### Non-Functional

- NF1: Board loads within 2s for sprints with up to 100 tasks
- NF2: Drag-drop feedback is instant (optimistic update, revert on error)
- NF3: Responsive layout -- columns stack on mobile
- NF4: Follow Odoo 18 OWL component patterns (setup, onWillStart, template)

## Architecture

### Component Hierarchy

```
SprintBoardAction (client action, registered via registry)
├── SprintSelector (dropdown, loads sprints for current project)
├── SprintBoardColumns (main kanban area)
│   └── SprintBoardColumn (per stage)
│       ├── ColumnHeader (stage name, task count, SP total, WIP indicator)
│       └── TaskCard[] (draggable items)
│           ├── TaskTitle
│           ├── AssigneeAvatar
│           ├── StoryPointsBadge
│           └── BlockedIndicator
└── BacklogSidebar (collapsible, unassigned tasks)
```

### OWL Component Pattern (Odoo 18)

```javascript
/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { useSortable } from "@web/core/utils/sortable";

class SprintBoardAction extends Component {
    static template = "project_scrum.SprintBoard";
    static props = { action: Object };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            sprintId: null,
            sprints: [],
            columns: [],
            backlogTasks: [],
        });
        onWillStart(() => this.loadData());
    }

    async loadData() {
        // Load sprints for project, load tasks grouped by stage
    }

    async onTaskDrop(taskId, newStageId) {
        // Optimistic update + ORM write
    }
}

registry.category("actions").add("sprint_board", SprintBoardAction);
```

### Drag-Drop Strategy

- Use `@web/core/utils/sortable` (Odoo's Sortable wrapper) or `useSortable` hook
- Each column is a sortable container
- On drop: call `this.orm.write('project.task', [taskId], { stage_id: newStageId })`
- Optimistic UI: move card immediately, revert if RPC fails
- Cross-column sorting via `connectWith` option

### Data Loading

```python
# New RPC method on project.sprint
def get_board_data(self):
    """Return sprint board data grouped by stage."""
    self.ensure_one()
    stages = self.project_id.type_ids
    result = []
    for stage in stages:
        tasks = self.task_ids.filtered(lambda t: t.stage_id == stage)
        result.append({
            'stage_id': stage.id,
            'stage_name': stage.name,
            'is_closed': stage.fold,
            'tasks': [{
                'id': t.id,
                'name': t.name,
                'story_points': t.story_points,
                'user_id': t.user_ids[:1].id if t.user_ids else False,
                'user_name': t.user_ids[:1].name if t.user_ids else '',
                'user_avatar': f'/web/image/res.users/{t.user_ids[:1].id}/avatar_128' if t.user_ids else '',
                'task_type': t.task_type,
                'is_blocked': t.is_blocked,
            } for t in tasks],
            'task_count': len(tasks),
            'total_sp': sum(tasks.mapped('story_points')),
        })
    return result
```

## Implementation Steps

### Step 1: Sprint Board RPC endpoint (~1h)

- [ ] Add `get_board_data()` method to `project.sprint` model
- [ ] Add `get_backlog_tasks()` method for sidebar
- [ ] Add `move_task_to_sprint(task_id)` method for backlog → sprint assignment

### Step 2: SprintBoardAction OWL component (~3h)

- [ ] Create `static/src/js/sprint-board.js` with SprintBoardAction
- [ ] Implement `loadData()`: fetch sprints, load board data
- [ ] Implement sprint selector with `onSprintChange()`
- [ ] Register as client action: `registry.category("actions").add("sprint_board", ...)`

### Step 3: Sprint Board QWeb template (~2h)

- [ ] Create `static/src/xml/sprint-board.xml`
- [ ] Template sections: header (sprint selector + stats), columns grid, task cards
- [ ] Task card template: title, avatar, SP badge, type icon, blocked indicator
- [ ] Column header template: stage name, count, SP total, WIP bar

### Step 4: Drag-drop implementation (~2h)

- [ ] Implement `useSortable` on each column container
- [ ] Handle `onDrop` event: extract taskId + new stageId
- [ ] Optimistic UI update (move in state before RPC)
- [ ] RPC `orm.write` to persist stage change
- [ ] Error handling: revert UI on failure, show notification
- [ ] Support cross-column drag (connectWith groups)

### Step 5: SCSS styling (~1h)

- [ ] Create `static/src/scss/sprint-board.scss`
- [ ] Column layout: flexbox row, equal-width columns, scrollable
- [ ] Task card: shadow, rounded, hover state, type color coding
- [ ] SP badge: circular, Fibonacci-colored (1-green, 5-yellow, 13-red)
- [ ] WIP limit: column header turns amber/red when over limit
- [ ] Blocked indicator: red stripe or icon overlay
- [ ] Responsive: columns stack vertically below 768px

### Step 6: Menu & action registration (~1h)

- [ ] Add client action XML in `views/project-sprint-board-views.xml` (update existing)
- [ ] Update menu to point to new client action
- [ ] Add Sprint Board assets to `__manifest__.py` web.assets_backend
- [ ] Test: navigate to Sprint Board from menu, verify render

## Risks

| Risk | Mitigation |
|------|------------|
| Sortable.js API differs from expected | Check `@web/core/utils/sortable` source; fallback to vanilla Sortable if needed |
| Performance with 100+ tasks | Paginate tasks per column (show 20 + "Load more"), use `read_group` for counts |
| Concurrent edits (two users dragging) | Reload board data after each drop; show notification if conflict |
| OWL reactivity with nested state | Use `useState` with flat structure, avoid deep nesting |

# PMS vs Odoo Gap Analysis Report

**Date:** 2026-03-18 | **Source:** user-storie-pms.md (38 stories, 10 epics)

---

## Summary

| Category | Total Stories | ✅ Covered | ⚠️ Partial | ❌ Gap |
|----------|-------------|-----------|-----------|-------|
| Epic 1: Project Management | 6 | 4 | 2 | 0 |
| Epic 2: Section Management | 2 | 1 | 1 | 0 |
| Epic 3: Task Management | 10 | 8 | 1 | 1 |
| Epic 4: Agile/Sprint | 6 | 6 | 0 | 0 |
| Epic 5: Goals & OKR | 3 | 0 | 0 | 3 |
| Epic 6: Collaboration | 3 | 3 | 0 | 0 |
| Epic 7: Custom Fields | 2 | 2 | 0 | 0 |
| Epic 8: Tag Management | 1 | 1 | 0 | 0 |
| Epic 9: RBAC | 1 | 0 | 1 | 0 |
| Epic 10: Dashboard & Views | 4 | 2 | 1 | 1 |
| **TOTAL** | **38** | **27** | **6** | **5** |

**Coverage: 71% full, 16% partial, 13% gap**

---

## Detailed Story-by-Story Mapping

### ✅ FULLY COVERED (27 stories — no work needed)

| ID | Story | Odoo Feature |
|----|-------|--------------|
| US-002 | Xem danh sách dự án | Project kanban/list views, privacy filters |
| US-003 | Chỉnh sửa thông tin dự án | Project form view, mail.thread tracking |
| US-004 | Lưu trữ/Xóa dự án | `active` field (archive), delete with cascade |
| US-005 | Quản lý thành viên | user_id (manager), portal collaborators, Odoo groups |
| US-006 | Xem thống kê dự án | task_count, open_task_count, task_completion_percentage |
| US-007 | Tạo/quản lý Section | project.task.type — stages with sequence, fold, rename |
| US-010 | Xem/chỉnh sửa task | Task form view, inline editing, chatter |
| US-011 | Kéo thả task Kanban | Native kanban drag-drop, sequence reorder |
| US-012 | Tạo Subtask | parent_id/child_ids, subtask_completion_percentage |
| US-013 | Task Dependency | depend_on_ids Many2many, _has_cycle validation |
| US-014 | Gắn Tag cho Task | tag_ids Many2many to project.tags, color support |
| US-015 | Theo dõi Task | mail.thread followers (message_subscribe) |
| US-016 | Recurring Task | project.task.recurrence model, repeat_interval/unit/type |
| US-018 | Hoàn thành Task | state field, is_closed, date_end timestamps |
| US-019 | Tạo Sprint | project.sprint model (draft→active→closed) |
| US-020 | Sprint Planning | sprint_planning_wizard, backlog → sprint assignment |
| US-021 | Start/Complete Sprint | action_start_sprint, sprint_close_wizard |
| US-022 | Sprint Board | Kanban filtered by active sprint tasks |
| US-023 | Burndown Chart | project.sprint.burndown.report SQL view |
| US-024 | Velocity Chart | project.sprint.velocity.report, velocity_forecast |
| US-028 | Bình luận Task | mail.thread chatter, rich-text messages |
| US-029 | Đính kèm file | ir.attachment One2many on tasks |
| US-030 | Activity Log | mail.tracking.value, mail.activity history |
| US-031 | Custom Field Definition | task_properties_definition (PropertiesDefinition) |
| US-032 | Custom Field Values | task_properties (Properties field per task) |
| US-033 | Tạo/quản lý Tags | project.tags model, workspace-level tags |
| US-036 | My Tasks | Built-in "My Tasks" filter (user_ids contains current) |

### ⚠️ PARTIALLY COVERED (6 stories — cần enhance)

| ID | Story | What Exists | Gap |
|----|-------|-------------|-----|
| US-001 | Tạo dự án mới | Project create form + methodology wizard | Missing: project type selector (kanban/list/board view mode), icon selector. Wizard chỉ có methodology, chưa có view type |
| US-008 | WIP Limit | project.task.type model exists | Missing: `wip_limit` field + visual warning khi vượt limit |
| US-009 | Tạo task mới | Task create form full-featured | Missing: `task_type` field (task/bug/story/epic), quick-add chỉ title+Enter |
| US-017 | Full-text Search | name field has trigram index | Missing: tsvector on description, PostgreSQL full-text search |
| US-034 | RBAC per-project | Odoo groups (admin/user/portal) | Missing: per-project roles (owner/editor/commenter/viewer). Odoo chỉ có global groups, không có project-level RBAC |
| US-037 | Calendar View | Calendar view exists for tasks | Missing: drag-to-reschedule chưa rõ có native hay không, cần verify |

### ❌ NOT COVERED (5 stories — cần build mới)

| ID | Story | Gap Description | Effort |
|----|-------|----------------|--------|
| US-025 | Tạo Goal | Không có Goal/OKR model. Gamification module tồn tại nhưng không liên quan project | Medium |
| US-026 | Link Goal ↔ Projects/Tasks | Cần GoalProjectLink, GoalTaskLink, auto-progress calculation | Medium |
| US-027 | Theo dõi Goal status | Status flow (on_track/at_risk/off_track/achieved), manual + auto progress | Low |
| US-035 | PMS Dashboard | Odoo có project stats nhưng không có unified dashboard view với KPI cards, charts, activity feed | High |
| US-038 | Timeline/Gantt View | Enterprise-only feature. Community edition không có Gantt | High |

---

## Implementation Priority Matrix

### Tier 1: Quick Wins (1-2 days each)

| Feature | Story | Files to Modify | Effort |
|---------|-------|----------------|--------|
| WIP Limits on stages | US-008 | project_task_type.py (inherit), views | 1 day |
| Task Type field | US-009 | project_task.py (inherit), views | 1 day |
| Full-text search | US-017 | SQL migration + search view | 1-2 days |

### Tier 2: Medium Features (3-5 days each)

| Feature | Stories | New Models | Effort |
|---------|---------|------------|--------|
| Goals & OKR system | US-025, 026, 027 | project.goal, project.goal.link | 5 days |
| Project-level RBAC | US-034 | Extend project.collaborator | 3-4 days |
| Project create enhance | US-001 | Extend wizard + view type | 1-2 days |

### Tier 3: Major Features (1-2 weeks each)

| Feature | Stories | Complexity | Effort |
|---------|---------|-----------|--------|
| PMS Dashboard | US-035 | Custom OWL component, multiple data sources | 1-2 weeks |
| Gantt/Timeline View | US-038 | Custom JS widget or third-party library | 2 weeks |

---

## Recommended Implementation Order

```
Phase 1 (Sprint 1): Quick Wins
├── US-008: WIP Limits
├── US-009: Task Type field (task/bug/story/epic)
└── US-001: Enhance project creation wizard (view type)

Phase 2 (Sprint 2): Goals & OKR
├── US-025: Goal model + CRUD
├── US-026: Goal ↔ Project/Task links
└── US-027: Goal status tracking + auto-progress

Phase 3 (Sprint 3): RBAC & Search
├── US-034: Project-level RBAC
└── US-017: Full-text search (tsvector)

Phase 4 (Sprint 4): Dashboard & Views
├── US-035: PMS Dashboard (KPI cards, charts)
└── US-038: Timeline/Gantt View (if needed)
```

---

## Architecture Decision: New Module vs Extend

**Recommendation:** Create new module `project_pms_enhance` that depends on `project_scrum`.

Reasons:
- `project_scrum` is stable and complete for Agile features
- PMS-specific features (Goals, Dashboard, RBAC) are orthogonal to Scrum
- Separate module = easier to test, deploy, and maintain
- Can install independently of scrum features

---

## Unresolved Questions

1. **Gantt view**: Build custom or accept Enterprise dependency? Custom = 2 weeks, dhtmlxGantt open-source possible
2. **RBAC scope**: Per-project roles override global Odoo groups or layer on top?
3. **Workspace**: Is Odoo `res.company` sufficient as workspace, or need new model?
4. **Dashboard**: Use Odoo's native dashboard framework or custom OWL component?
5. **Calendar drag-drop**: Need to verify if Odoo 18 calendar supports native drag-to-reschedule

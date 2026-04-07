# Phase 6: Testing & Polish

## Context Links

- [Plan Overview](plan.md)
- [Phase 1-5](phase-01-ceremony-model-and-security.md)
- Odoo test patterns: `addons/project/tests/`
- Existing module: `addons/project_scrum/`

## Overview

- **Priority:** P1 -- High
- **Status:** Completed
- **Effort:** ~8h
- **Depends on:** All previous phases complete
- **Description:** Comprehensive unit tests, integration tests, performance optimization, install/uninstall verification

## Requirements

### Functional

- F1: Unit tests for sprint lifecycle (create, start, close, cancel)
- F2: Unit tests for velocity computation and burndown data
- F3: Unit tests for ceremony CRUD and type validation
- F4: Unit tests for backlog management (task assignment/unassignment)
- F5: Unit tests for security group access control
- F6: Integration test for full sprint lifecycle end-to-end
- F7: Performance test: no N+1 queries in board data loading

### Non-Functional

- NF1: Tests use `TransactionCase` (rollback after each test)
- NF2: Follow Odoo test naming: `test_*.py`, class `TestXxx(TransactionCase)`
- NF3: All tests pass with `--test-enable -i project_scrum`
- NF4: No external dependencies for tests (self-contained fixtures)

## Architecture

### Test Structure

```
tests/
├── __init__.py
├── common.py              # Shared fixtures: project, sprint, tasks, users
├── test_sprint.py         # Sprint lifecycle tests
├── test_backlog.py        # Backlog management tests
├── test_velocity.py       # Velocity & burndown computation tests
├── test_ceremony.py       # Ceremony CRUD tests
└── test_security.py       # Access control tests
```

### Common Fixtures (`common.py`)

```python
from odoo.tests.common import TransactionCase

class ScrumTestCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env['project.project'].create({
            'name': 'Test Scrum Project',
            'methodology': 'scrum',
        })
        cls.sprint = cls.env['project.sprint'].create({
            'name': 'Sprint 1',
            'project_id': cls.project.id,
            'start_date': fields.Date.today(),
            'end_date': fields.Date.today() + timedelta(days=14),
            'capacity_points': 30,
        })
        # Create test tasks, users, stages...
```

## Implementation Steps

### Step 1: Test infrastructure (~1h)

- [x] Create `tests/__init__.py` with imports
- [x] Create `tests/common.py` with shared fixtures
- [x] Setup: project, sprint, stages, users (scrum_user, scrum_master, product_owner)
- [x] Helper methods: `_create_task()`, `_close_task()`, `_create_ceremony()`

### Step 2: Sprint lifecycle tests (~2h)

- [x] `test_sprint.py::TestSprintLifecycle`
  - `test_create_sprint_defaults`: fields default correctly
  - `test_start_sprint`: draft → active
  - `test_start_sprint_already_active_raises`: ValidationError on double-start
  - `test_single_active_sprint_constraint`: can't start 2nd sprint
  - `test_date_constraint_end_before_start`: SQL constraint enforced
  - `test_computed_story_points_with_tasks`: total SP computed correctly
  - `test_remaining_points_after_close_task`: remaining SP decreases
  - `test_get_board_data_structure`: OWL board data shape
  - `test_action_plan_sprint_returns_action`: wizard action

### Step 3: Backlog & velocity tests (~2h)

- [x] `test_backlog.py::TestBacklog`
  - `test_task_without_sprint_is_in_backlog`: is_in_backlog=True
  - `test_assign_task_to_sprint`: sprint_id set, removed from backlog
  - `test_get_backlog_tasks_excludes_sprint_tasks`: filtering correct
  - `test_move_task_to_sprint`: RPC method works
  - `test_backlog_health_counts`: total/unestimated/high_prio counts

- [x] `test_velocity.py::TestVelocity`
  - `test_velocity_forecast_rolling_average`: 3-sprint rolling avg
  - `test_velocity_forecast_ignores_zero_velocity`: zero excluded
  - `test_get_burndown_data_ideal_line`: starts at total_sp, ends at 0
  - `test_daily_log_cron_creates_snapshot`: cron creates daily log
  - `test_daily_log_cron_idempotent`: no duplicate logs

### Step 4: Ceremony & security tests (~2h)

- [x] `test_ceremony.py::TestCeremony`
  - `test_create_ceremony_all_types`: all types work
  - `test_duplicate_planning_ceremony_raises`: ValidationError
  - `test_ceremony_attendees`: Many2many relation
  - `test_retrospective_fields`: went_well, to_improve stored
  - `test_ceremony_cascade_delete`: deleting sprint deletes ceremonies

- [x] `test_security.py::TestScrumSecurity`
  - `test_project_user_can_read_sprint`: read access confirmed
  - `test_project_user_cannot_create_sprint`: AccessError raised
  - `test_scrum_master_can_create_ceremony`: create access confirmed
  - `test_scrum_user_cannot_create_ceremony`: AccessError raised
  - `test_company_isolation_sprint`: cross-company not visible
  - `test_dashboard_data_structure`: all required keys present

## Risks

| Risk | Mitigation |
|------|------------|
| Test DB setup time | Use `setUpClass` for shared fixtures (not `setUp`) |
| Flaky tests from date-dependent logic | Use `freezegun` or mock `fields.Date.today()` |
| Security tests need multiple users | Create users in fixture with proper group assignment |

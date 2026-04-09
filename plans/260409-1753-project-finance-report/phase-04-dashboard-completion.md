# Phase 4: Dashboard Completion

## Priority: P2 | Status: completed

## Overview

Complete OWL financial dashboard. Existing JS/XML/SCSS are functional but missing:
1. `get_dashboard_data` Python method (dashboard calls it but it doesn't exist)
2. Dashboard action not in manifest data list
3. Consider adding project filter dropdown to dashboard

## Files to Modify

- `addons/project_finance_report/models/project_revenue_report.py` — add `get_dashboard_data` (done in Phase 1)
- `addons/project_finance_report/__manifest__.py` — add `views/project-finance-dashboard-action.xml` to data
- `addons/project_finance_report/static/src/js/finance-dashboard.js` — optional: add project filter
- `addons/project_finance_report/static/src/xml/finance-dashboard.xml` — optional: add filter UI

## `get_dashboard_data` Implementation (in Phase 1)

Already planned in Phase 1. This phase focuses on:
- Verifying dashboard action registration works
- Adding manifest entry
- Optional UX enhancements

## Manifest Fix

Add to `data` list:
```python
'views/project-finance-dashboard-action.xml',
```

Must be BEFORE `project-finance-menus.xml` (menus reference the action).

## Optional: Project Filter on Dashboard

Add a dropdown to filter dashboard data by project:
```js
// In setup()
this.state.selectedProject = false;

async onProjectChange(ev) {
    this.state.selectedProject = parseInt(ev.target.value) || false;
    await this.onRefresh();
}

async fetchData() {
    const data = await this.orm.call(
        "project.revenue.report", "get_dashboard_data",
        [this.state.selectedProject]
    );
    // ...
}
```

## Implementation Steps

1. Add `views/project-finance-dashboard-action.xml` to manifest data (before menus XML)
2. Verify `get_dashboard_data` from Phase 1 returns correct shape
3. Test dashboard loads without JS errors
4. (Optional) Add project filter dropdown

## Todo

- [x] Fix manifest — add dashboard action XML
- [x] Verify dashboard action tag matches JS registry
- [x] Test Chart.js loading
- [x] (Optional) Add project filter to dashboard

## Success Criteria

- Dashboard menu item appears under Project Finance
- KPI cards show real totals
- Revenue vs Cost bar chart renders
- Aging doughnut chart renders
- Refresh button works

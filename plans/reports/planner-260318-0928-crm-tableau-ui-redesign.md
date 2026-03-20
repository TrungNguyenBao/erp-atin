# Planner Report: CRM Tableau/Salesforce UI Redesign

**Date:** 2026-03-18
**Plan:** `plans/260318-0928-crm-tableau-ui-redesign/`

## Summary

Created 7-phase implementation plan to transform the CRM module UI from a vibrant blue, animated style to a flat Tableau/Salesforce corporate aesthetic. All changes are SCSS-only (no JS/XML changes needed). No new files unless sidebar section exceeds 200-line file limit.

## Phase Overview

| Phase | Description | File(s) | Effort | Risk |
|-------|-------------|---------|--------|------|
| 1 | Design tokens - muted palette, flat shadows, reduced radius | `_variables.scss` | 20min | Low |
| 2 | Mixins - remove hover lift, fade-in, accent border | `_mixins.scss` | 15min | Low |
| 3 | Common styles - flatten cards, remove animations, thicken progress bars | `common-enhance.scss` | 30min | Low |
| 4 | CRM Kanban - remove left borders, flatten cards, native progress colors | `crm-kanban-enhance.scss` | 45min | Low |
| 5 | CRM Form - reduce button shadows, remove star scale | `crm-form-enhance.scss` | 20min | Low |
| 6 | Sidebar & Navbar - dark navy sidebar, white navbar | `common-enhance.scss` (or new file) | 30min | **High** |
| 7 | Sale views - cascade token changes, reduce shadows | `sale-*.scss` | 20min | Low |

**Total effort:** ~3 hours

## Key Design Decisions

1. **Color shift:** #2563EB (vibrant) -> #2B5797 (muted corporate blue)
2. **Shadows:** Near-zero. Cards use `0 1px 2px rgba(0,0,0,0.03)`
3. **No hover transforms:** All `translateY(-2px)` and `rotate(2deg)` removed
4. **No left accent borders** on cards
5. **Progress bars:** Height increased 5-6px -> 8px, native Odoo stage colors preserved (not overridden to blue)
6. **Sidebar:** Dark navy #1B2559 (HIGH RISK - selector verification needed against running instance)

## Implementation Order

Must execute sequentially: Phase 1 -> 2 -> 3 -> 4/5/6/7 (last four can be parallel)

## Risks

- **Phase 6 (Sidebar):** Odoo 18/19 sidebar CSS selectors unknown without DOM inspection. Developer must inspect running instance first. Phase can be deferred independently.
- **File size:** `common-enhance.scss` at 288 lines - adding sidebar section may push over 200. Mitigation: extract to new `sidebar-navbar-enhance.scss` if needed.

## Files Delivered

- `plans/260318-0928-crm-tableau-ui-redesign/plan.md`
- `plans/260318-0928-crm-tableau-ui-redesign/phase-01-design-tokens.md`
- `plans/260318-0928-crm-tableau-ui-redesign/phase-02-mixins-update.md`
- `plans/260318-0928-crm-tableau-ui-redesign/phase-03-common-styles.md`
- `plans/260318-0928-crm-tableau-ui-redesign/phase-04-crm-kanban.md`
- `plans/260318-0928-crm-tableau-ui-redesign/phase-05-crm-form.md`
- `plans/260318-0928-crm-tableau-ui-redesign/phase-06-sidebar-navbar.md`
- `plans/260318-0928-crm-tableau-ui-redesign/phase-07-sale-views.md`

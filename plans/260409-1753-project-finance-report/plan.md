---
status: completed
created: 2026-04-09
slug: project-finance-report
blockedBy: []
blocks: []
---

# Project Finance Report Module — Rewrite to SO-Based Spec

Rewrite `project_finance_report` module to match VisionAI draft spec (`report_plan_draf.md`).
Existing code uses analytic_distribution JSONB; draft spec uses SO/PO-based approach with richer columns.

## Critical Change: Data Source Strategy

| Aspect | Current (analytic) | Target (SO-based) |
|--------|-------------------|-------------------|
| Revenue source | invoice lines via analytic_distribution | sale_order.amount_untaxed |
| Cost source | vendor bill lines via analytic_distribution | purchase_order via PO.origin = SO.name |
| AR/AP link | analytic → project_id | invoice_origin → SO/PO name |
| Extra columns | none | user_id, labor_cost, invoiced, paid, residual |
| Dependencies | account, project, analytic | sale, purchase, account, project |

## Module: `project_finance_report`

Keep existing module name (not `visionai_reports` as draft suggests — already scaffolded).

## Phases

| # | Phase | Status | Effort |
|---|-------|--------|--------|
| 1 | [Revenue report rewrite (SO-based)](phase-01-revenue-report-rewrite.md) | completed | M |
| 2 | [AR/AP report rewrite](phase-02-receivable-payable-rewrite.md) | completed | M |
| 3 | [Security & record rules](phase-03-security-record-rules.md) | completed | S |
| 4 | [Dashboard completion](phase-04-dashboard-completion.md) | completed | M |
| 5 | [Manifest fix & local test](phase-05-manifest-fix-and-test.md) | completed | S |

## Installed Modules (relevant)

account, analytic, project, project_account, sale, sale_project, purchase, purchase_stock, stock_account, mrp_account, sale_timesheet

## Rollback

Self-contained module. Uninstall via Apps menu drops SQL views and menus cleanly.

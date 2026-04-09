# Phase 1: Revenue Report Rewrite (SO-Based)

## Priority: P1 | Status: completed

## Overview

Rewrite `project_revenue_report.py` from analytic_distribution JSONB approach to SO-based approach per draft spec. SO is the primary row; PO costs linked via `origin`; invoice data linked via `invoice_origin`.

## Key Insights

- `sale_order.amount_untaxed` = revenue (confirmed SO only: state in sale/done)
- `purchase_order.origin` = SO name (auto for MTO, manual for manual POs)
- `account_move.invoice_origin` = SO name (auto when creating invoice from SO)
- Labor cost from `account_analytic_line` (timesheet) linked via SO → project → analytic_account
- `sale_timesheet` module already installed — provides timesheet cost data

## Files to Modify

- `addons/project_finance_report/models/project_revenue_report.py` — full rewrite of SQL view + add `get_dashboard_data`
- `addons/project_finance_report/views/project-revenue-report-views.xml` — add new columns to tree/pivot/graph/search
- `addons/project_finance_report/__manifest__.py` — add `sale`, `purchase` to depends

## SQL View Design

```sql
CREATE OR REPLACE VIEW project_revenue_report AS (
    SELECT
        so.id AS id,
        so.id AS sale_order_id,
        so.partner_id,
        so.user_id,
        so.date_order,
        pp.id AS project_id,
        so.amount_untaxed AS revenue,
        COALESCE(po_agg.purchase_cost, 0) AS purchase_cost,
        COALESCE(ts_agg.labor_cost, 0) AS labor_cost,
        so.amount_untaxed - COALESCE(po_agg.purchase_cost, 0)
            - COALESCE(ts_agg.labor_cost, 0) AS gross_profit,
        CASE WHEN so.amount_untaxed > 0
            THEN (so.amount_untaxed - COALESCE(po_agg.purchase_cost, 0)
                  - COALESCE(ts_agg.labor_cost, 0))
                 / so.amount_untaxed * 100
            ELSE 0
        END AS margin_pct,
        COALESCE(inv_agg.invoiced, 0) AS invoiced,
        COALESCE(inv_agg.paid, 0) AS paid,
        COALESCE(inv_agg.residual, 0) AS residual,
        so.company_id
    FROM sale_order so
    -- Link SO → Project via sale_order_line.project_id or analytic
    LEFT JOIN project_project pp ON pp.sale_order_id = so.id
        OR EXISTS (
            SELECT 1 FROM sale_order_line sol
            WHERE sol.order_id = so.id AND sol.project_id = pp.id
        )
    -- PO costs via origin = SO name
    LEFT JOIN (
        SELECT origin, SUM(amount_untaxed) AS purchase_cost
        FROM purchase_order
        WHERE state IN ('purchase', 'done')
        GROUP BY origin
    ) po_agg ON po_agg.origin = so.name
    -- Timesheet labor cost via project analytic
    LEFT JOIN (
        SELECT so2.id AS sale_order_id,
               SUM(ABS(aal.amount)) AS labor_cost
        FROM account_analytic_line aal
        JOIN project_project pp2 ON pp2.analytic_account_id IS NOT NULL
            AND aal.account_id = pp2.analytic_account_id
        JOIN sale_order so2 ON so2.id = pp2.sale_order_id
        WHERE aal.project_id IS NOT NULL
        GROUP BY so2.id
    ) ts_agg ON ts_agg.sale_order_id = so.id
    -- Invoice totals via invoice_origin = SO name
    LEFT JOIN (
        SELECT invoice_origin,
            SUM(amount_total) AS invoiced,
            SUM(amount_total - amount_residual) AS paid,
            SUM(amount_residual) AS residual
        FROM account_move
        WHERE move_type = 'out_invoice' AND state = 'posted'
        GROUP BY invoice_origin
    ) inv_agg ON inv_agg.invoice_origin = so.name
    WHERE so.state IN ('sale', 'done')
);
```

**Note:** The SO → project link uses multiple strategies:
1. `project_project.sale_order_id = so.id` (sale_project module sets this)
2. `sale_order_line.project_id` (if task-based)
3. Fallback: analytic_distribution if neither exists

Validate which link exists on VPS DB before finalizing.

## Model Fields (Python)

```python
sale_order_id = fields.Many2one('sale.order', readonly=True)
partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
user_id = fields.Many2one('res.users', string='Salesperson', readonly=True)
date_order = fields.Datetime(string='Order Date', readonly=True)
project_id = fields.Many2one('project.project', readonly=True)
revenue = fields.Float(readonly=True)
purchase_cost = fields.Float(string='Purchase Cost', readonly=True)
labor_cost = fields.Float(string='Labor Cost', readonly=True)
gross_profit = fields.Float(readonly=True)
margin_pct = fields.Float(string='Margin %', readonly=True)
invoiced = fields.Float(string='Invoiced', readonly=True)
paid = fields.Float(string='Paid', readonly=True)
residual = fields.Float(string='Outstanding', readonly=True)
company_id = fields.Many2one('res.company', readonly=True)
```

## `get_dashboard_data` Method

Add `@api.model` method that returns:
```python
{
    "totals": {"revenue": X, "cost": X, "gross_profit": X, "receivable": X, "payable": X},
    "projects": [{"id": X, "name": "...", "revenue": X, "cost": X, "profit": X, "margin": X, "receivable": X, "payable": X}],
    "aging": {"current": X, "days_30": X, "days_60": X, "days_90": X, "over_90": X}
}
```

Query `project.revenue.report`, `project.receivable.report`, `project.payable.report` via ORM read_group.

## XML View Changes

### Tree view — add columns:
`user_id`, `purchase_cost`, `labor_cost`, `invoiced`, `paid`, `residual`

### Search view — add filters:
- `user_id` field for salesperson search
- Group by: Salesperson

### Pivot — add measures:
`purchase_cost`, `labor_cost`, `invoiced`, `paid`, `residual`

## Implementation Steps

1. Update `__manifest__.py`: add `'sale', 'purchase'` to depends
2. Rewrite `project_revenue_report.py`: new SQL view, new fields, `get_dashboard_data` method
3. Update `project-revenue-report-views.xml`: add new columns/filters
4. Verify SQL compiles against DB schema

## Todo

- [x] Update manifest depends
- [x] Rewrite revenue report SQL view
- [x] Add all new fields to model
- [x] Implement `get_dashboard_data` method
- [x] Update tree/pivot/graph/search XML views
- [x] Verify SQL against actual VPS DB schema

## Success Criteria

- Revenue report shows: project, customer, saler, date, revenue, purchase_cost, labor_cost, gross_profit, margin%, invoiced, paid, residual
- `get_dashboard_data` returns valid JSON for dashboard consumption
- Pivot/Graph views work with new measures

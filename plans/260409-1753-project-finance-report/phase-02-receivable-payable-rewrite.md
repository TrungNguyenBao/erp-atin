# Phase 2: AR/AP Report Rewrite

## Priority: P1 | Status: completed

## Overview

Rewrite receivable and payable reports to match draft spec. Key changes:
- Add `invoice_origin` (SO/PO name) for traceability
- Add `amount_paid`, `payment_state` columns
- Replace aging buckets: not_due, 1-30, 31-60, 61+ as Float fields (not Selection)
- Keep project_id linking via analytic_distribution (better for filtering than invoice_origin text)

## Files to Modify

- `addons/project_finance_report/models/project_receivable_report.py` — rewrite SQL + fields
- `addons/project_finance_report/models/project_payable_report.py` — rewrite SQL + fields
- `addons/project_finance_report/views/project-receivable-report-views.xml` — update views
- `addons/project_finance_report/views/project-payable-report-views.xml` — update views

## Receivable Report Changes

### New Fields
```python
invoice_number = fields.Char(string='Invoice', readonly=True)
invoice_origin = fields.Char(string='Source', readonly=True)  # SO name
amount_paid = fields.Float(string='Paid', readonly=True)
payment_state = fields.Selection([...], readonly=True)
not_due = fields.Float(string='Not Due', readonly=True)
overdue_1_30 = fields.Float(string='1-30 Days', readonly=True)
overdue_31_60 = fields.Float(string='31-60 Days', readonly=True)
overdue_61_plus = fields.Float(string='61+ Days', readonly=True)
```

### Remove
- `aging_bucket` Selection field — replaced by Float columns per draft

### SQL View (Receivable)
```sql
SELECT
    am.id,
    am.name AS invoice_number,
    pp.id AS project_id,
    am.partner_id,
    am.invoice_origin,
    am.invoice_date,
    am.invoice_date_due,
    am.amount_total,
    am.amount_total - am.amount_residual AS amount_paid,
    am.amount_residual,
    am.payment_state,
    GREATEST(CURRENT_DATE - am.invoice_date_due, 0) AS days_overdue,
    CASE WHEN am.invoice_date_due >= CURRENT_DATE
        THEN am.amount_residual ELSE 0 END AS not_due,
    CASE WHEN CURRENT_DATE - am.invoice_date_due BETWEEN 1 AND 30
        THEN am.amount_residual ELSE 0 END AS overdue_1_30,
    CASE WHEN CURRENT_DATE - am.invoice_date_due BETWEEN 31 AND 60
        THEN am.amount_residual ELSE 0 END AS overdue_31_60,
    CASE WHEN CURRENT_DATE - am.invoice_date_due > 60
        THEN am.amount_residual ELSE 0 END AS overdue_61_plus,
    am.company_id
FROM account_move am
-- Keep analytic link for project_id (reliable for filtering)
LEFT JOIN account_move_line aml ON aml.move_id = am.id AND aml.display_type = 'product'
LEFT JOIN project_project pp
    ON pp.analytic_account_id IS NOT NULL
    AND aml.analytic_distribution ? pp.analytic_account_id::text
WHERE am.move_type = 'out_invoice'
    AND am.state = 'posted'
    AND am.amount_residual > 0
GROUP BY am.id, pp.id, am.name, am.partner_id, am.invoice_origin,
    am.invoice_date, am.invoice_date_due, am.amount_total,
    am.amount_residual, am.payment_state, am.company_id
```

### Payable Report
Same structure but:
- `move_type = 'in_invoice'` (vendor bills)
- `invoice_origin` = PO name
- Partner = supplier

## XML View Changes

### Tree views — add columns:
`invoice_number`, `invoice_origin`, `amount_paid`, `payment_state`, `not_due`, `overdue_1_30`, `overdue_31_60`, `overdue_61_plus`

### Remove aging_bucket column from tree/search views

### Pivot — measures:
`not_due`, `overdue_1_30`, `overdue_31_60`, `overdue_61_plus` as sum measures (for aged totals)

### Search — add:
- `invoice_origin` field
- `payment_state` filter (not_paid, partial, paid)

## Implementation Steps

1. Rewrite `project_receivable_report.py` — new fields, new SQL
2. Rewrite `project_payable_report.py` — mirror receivable with in_invoice
3. Update `project-receivable-report-views.xml`
4. Update `project-payable-report-views.xml`
5. Update wizard `action_view_report` domain fields if needed

## Todo

- [x] Rewrite receivable report model + SQL
- [x] Rewrite payable report model + SQL
- [x] Update receivable XML views
- [x] Update payable XML views
- [x] Verify wizard domain compatibility

## Success Criteria

- AR report shows: invoice#, customer, source SO, dates, totals, paid, residual, aging Float columns
- AP report mirrors AR for vendor bills
- Pivot view can sum aging columns for total aged report
- Existing project_id filtering still works

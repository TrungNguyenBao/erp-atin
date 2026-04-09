# Phase 5: Manifest Fix & Local Test

## Priority: P1 | Status: completed

## Overview

Final assembly: fix manifest, verify all files load, test module install locally or on VPS.

## Files to Modify

- `addons/project_finance_report/__manifest__.py` — final depends + data list
- `addons/project_finance_report/models/__init__.py` — verify all imports
- `addons/project_finance_report/__init__.py` — verify imports

## Final Manifest

```python
{
    'name': 'Project Finance Report',
    'version': '18.0.2.0.0',  # bump version
    'category': 'Accounting/Reporting',
    'summary': 'Financial reports per project: revenue, receivable, payable, dashboard',
    'depends': ['account', 'project', 'analytic', 'sale', 'purchase', 'sales_team'],
    'data': [
        'security/ir.model.access.csv',
        'security/project-finance-security-rules.xml',
        'wizard/project-finance-wizard-views.xml',
        'views/project-revenue-report-views.xml',
        'views/project-receivable-report-views.xml',
        'views/project-payable-report-views.xml',
        'views/project-finance-dashboard-action.xml',
        'views/project-finance-menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'project_finance_report/static/src/scss/finance-dashboard.scss',
            'project_finance_report/static/src/xml/finance-dashboard.xml',
            'project_finance_report/static/src/js/finance-dashboard.js',
        ],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
```

## Testing Checklist

### SQL View Validation
- [x] Revenue view creates without error
- [x] Receivable view creates without error
- [x] Payable view creates without error
- [x] All views return data when SO/invoices exist

### Module Install
- [x] `odoo -i project_finance_report -d erp_atin --stop-after-init` succeeds
- [x] No Python import errors
- [x] No XML parsing errors
- [x] No missing dependency errors

### Functional Test
- [x] Revenue report: pivot shows data grouped by project
- [x] Revenue report: tree view shows all columns
- [x] Receivable report: aging Float columns sum correctly
- [x] Payable report: mirrors receivable for vendor bills
- [x] Dashboard: KPI cards show numbers
- [x] Dashboard: charts render
- [x] Wizard: opens report with date/project filters applied
- [x] Menu items all visible under Accounting > Project Finance

### Security Test
- [x] Salesperson user sees only own SO revenue
- [x] Purchase user cannot access revenue menu
- [x] Accountant sees all reports

## Deploy to VPS

After local validation:
```bash
./deploy/deploy-odoo.sh
# Then on VPS: odoo -u project_finance_report -d erp_atin --stop-after-init
```

## Success Criteria

- Module installs cleanly on fresh DB
- All 3 reports + dashboard + wizard functional
- Security rules enforced per role
- Deploy script pushes updated module to VPS

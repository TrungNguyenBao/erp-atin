# Phase 3: Security & Record Rules

## Priority: P2 | Status: completed

## Overview

Implement role-based access per draft spec section 5.2. Currently only basic ACL exists (read for `account.group_account_readonly`). Need granular record rules.

## Draft Spec Access Matrix

| Group | Revenue | AR | AP | Dashboard |
|-------|---------|-----|-----|-----------|
| CEO/Manager | Full | Full | Full | Full |
| Sales Manager | Full | Full | No | Partial |
| Salesperson | Own deals | Own customers | No | No |
| Accountant | Full | Full | Full | Full |
| Purchasing | No | No | Full | Partial |

## Files to Modify

- `addons/project_finance_report/security/ir.model.access.csv` — add group-specific ACL rows
- `addons/project_finance_report/security/project-finance-security-rules.xml` — NEW file for ir.rule records

## Files to Create

- `addons/project_finance_report/security/project-finance-security-rules.xml`

## ACL Updates (ir.model.access.csv)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
# Revenue — accessible to accounting + sales
access_revenue_accountant,revenue.accountant,model_project_revenue_report,account.group_account_readonly,1,0,0,0
access_revenue_sales,revenue.sales,model_project_revenue_report,sales_team.group_sale_salesman,1,0,0,0
# Receivable — accounting + sales
access_receivable_accountant,receivable.accountant,model_project_receivable_report,account.group_account_readonly,1,0,0,0
access_receivable_sales,receivable.sales,model_project_receivable_report,sales_team.group_sale_salesman,1,0,0,0
# Payable — accounting + purchase
access_payable_accountant,payable.accountant,model_project_payable_report,account.group_account_readonly,1,0,0,0
access_payable_purchase,payable.purchase,model_project_payable_report,purchase.group_purchase_user,1,0,0,0
# Wizard — all report users
access_wizard_accountant,wizard.accountant,model_project_finance_wizard,account.group_account_readonly,1,1,1,1
access_wizard_sales,wizard.sales,model_project_finance_wizard,sales_team.group_sale_salesman,1,1,1,1
access_wizard_purchase,wizard.purchase,model_project_finance_wizard,purchase.group_purchase_user,1,1,1,1
```

## Record Rules (ir.rule)

### Salesperson sees only own SO-based revenue
```xml
<record id="rule_revenue_salesperson" model="ir.rule">
    <field name="name">Salesperson: own deals only</field>
    <field name="model_id" ref="model_project_revenue_report"/>
    <field name="groups" eval="[(4, ref('sales_team.group_sale_salesman'))]"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
</record>
```

### Sales Manager sees all revenue (no restriction) — handled by group_sale_salesman_all_leads

### Purchasing group cannot see revenue/receivable — handled by NOT granting ACL

## Implementation Steps

1. Rewrite `ir.model.access.csv` with group-specific rows
2. Create `project-finance-security-rules.xml` with ir.rule records
3. Add security XML to `__manifest__.py` data list
4. Add `'sales_team', 'purchase'` to depends if not already

## Todo

- [x] Rewrite ACL csv
- [x] Create security rules XML
- [x] Update manifest data list
- [x] Verify group references exist in installed modules

## Success Criteria

- Salesperson sees only own revenue data
- Purchasing users cannot access revenue/receivable reports
- Sales users cannot access payable reports
- Accountants see everything

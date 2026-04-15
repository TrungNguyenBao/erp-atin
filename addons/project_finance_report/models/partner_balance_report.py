"""SQL view: partner debit/credit balance by project."""

from odoo import api, fields, models, tools


class PartnerBalanceReport(models.Model):
    _name = 'partner.balance.report'
    _description = 'Partner Balance by Project'
    _auto = False
    _order = 'partner_id, balance_type'

    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    balance_type = fields.Selection([
        ('receivable', 'Receivable (KH)'),
        ('payable', 'Payable (NCC)'),
    ], string='Type', readonly=True)
    project_name = fields.Char(string='Project', readonly=True)
    total_debit = fields.Float(string='Debit (Nợ)', readonly=True)
    total_credit = fields.Float(string='Credit (Có)', readonly=True)
    balance = fields.Float(string='Balance', readonly=True)
    total_invoiced = fields.Float(string='Total Invoiced', readonly=True)
    total_paid = fields.Float(string='Total Paid', readonly=True)
    amount_due = fields.Float(string='Amount Due', readonly=True)
    invoice_count = fields.Integer(string='Invoices', readonly=True)
    company_id = fields.Many2one('res.company', readonly=True)

    def init(self):
        """Create SQL view for partner balance by project."""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    row_number() OVER () AS id,
                    am.partner_id,
                    CASE
                        WHEN am.move_type IN ('out_invoice', 'out_refund')
                            THEN 'receivable'
                        ELSE 'payable'
                    END AS balance_type,
                    COALESCE(
                        -- Try analytic → project
                        (SELECT pp.name::text FROM account_move_line aml2
                         JOIN account_analytic_account aaa
                             ON aml2.analytic_distribution ? aaa.id::text
                         JOIN project_project pp ON pp.account_id = aaa.id
                         WHERE aml2.move_id = am.id
                         AND aml2.display_type = 'product'
                         LIMIT 1),
                        -- Try invoice_origin → SO → project
                        (SELECT pp2.name::text FROM sale_order so
                         JOIN sale_order_line sol ON sol.order_id = so.id
                         JOIN project_project pp2 ON sol.project_id = pp2.id
                         WHERE am.invoice_origin LIKE '%%' || so.name || '%%'
                         LIMIT 1),
                        -- Try invoice_origin → PO → SO → project
                        (SELECT pp3.name::text FROM purchase_order po
                         JOIN sale_order so2
                             ON po.origin IS NOT NULL
                             AND po.origin LIKE '%%' || so2.name || '%%'
                         JOIN sale_order_line sol2 ON sol2.order_id = so2.id
                         JOIN project_project pp3 ON sol2.project_id = pp3.id
                         WHERE am.invoice_origin LIKE '%%' || po.name || '%%'
                         LIMIT 1),
                        'Chưa gắn dự án'
                    ) AS project_name,
                    SUM(am.amount_total) AS total_invoiced,
                    SUM(am.amount_total - am.amount_residual) AS total_paid,
                    SUM(am.amount_residual) AS amount_due,
                    -- Debit/Credit based on move type
                    CASE
                        WHEN am.move_type IN ('out_invoice', 'in_refund')
                            THEN SUM(am.amount_total)
                        ELSE 0
                    END AS total_debit,
                    CASE
                        WHEN am.move_type IN ('in_invoice', 'out_refund')
                            THEN SUM(am.amount_total)
                        ELSE 0
                    END AS total_credit,
                    -- Balance = receivable positive, payable negative
                    CASE
                        WHEN am.move_type IN ('out_invoice', 'out_refund')
                            THEN SUM(am.amount_residual)
                        ELSE -SUM(am.amount_residual)
                    END AS balance,
                    COUNT(*) AS invoice_count,
                    am.company_id
                FROM account_move am
                WHERE am.state = 'posted'
                    AND am.move_type IN (
                        'out_invoice', 'out_refund',
                        'in_invoice', 'in_refund')
                GROUP BY
                    am.partner_id, am.move_type, am.company_id, am.id
            )
        """)

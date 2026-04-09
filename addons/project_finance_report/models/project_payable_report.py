"""SQL view: accounts payable by project and supplier."""

from odoo import fields, models, tools


class ProjectPayableReport(models.Model):
    _name = 'project.payable.report'
    _description = 'Project Accounts Payable Report'
    _auto = False
    _order = 'days_overdue desc'

    invoice_number = fields.Char(string='Bill Number', readonly=True)
    project_id = fields.Many2one('project.project', string='Project', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Supplier', readonly=True)
    move_id = fields.Many2one('account.move', string='Bill', readonly=True)
    invoice_origin = fields.Char(string='Source', readonly=True)
    invoice_date = fields.Date(readonly=True)
    invoice_date_due = fields.Date(string='Due Date', readonly=True)
    amount_total = fields.Float(string='Bill Total', readonly=True)
    amount_paid = fields.Float(string='Paid', readonly=True)
    amount_residual = fields.Float(string='Amount Due', readonly=True)
    payment_state = fields.Char(string='Payment Status', readonly=True)
    days_overdue = fields.Integer(string='Days Overdue', readonly=True)
    not_due = fields.Float(string='Not Due', readonly=True)
    overdue_1_30 = fields.Float(string='1-30 Days', readonly=True)
    overdue_31_60 = fields.Float(string='31-60 Days', readonly=True)
    overdue_61_90 = fields.Float(string='61-90 Days', readonly=True)
    overdue_91_plus = fields.Float(string='91+ Days', readonly=True)
    company_id = fields.Many2one('res.company', readonly=True)

    def init(self):
        """Create SQL view for payable aging by project."""
        tools.drop_view_if_exists(self.env.cr, self._table)
        # Use DISTINCT ON to prevent row duplication from multiple PO/SO joins
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    am.id AS id,
                    am.name AS invoice_number,
                    pp.id AS project_id,
                    am.partner_id,
                    am.id AS move_id,
                    am.invoice_origin,
                    am.invoice_date,
                    COALESCE(am.invoice_date_due, am.invoice_date) AS invoice_date_due,
                    am.amount_total,
                    am.amount_total - am.amount_residual AS amount_paid,
                    am.amount_residual,
                    am.payment_state::text AS payment_state,
                    GREATEST(
                        (CURRENT_DATE - COALESCE(am.invoice_date_due, am.invoice_date))::int, 0
                    ) AS days_overdue,
                    CASE WHEN COALESCE(am.invoice_date_due, am.invoice_date) >= CURRENT_DATE
                        THEN am.amount_residual ELSE 0
                    END AS not_due,
                    CASE WHEN (CURRENT_DATE - COALESCE(am.invoice_date_due, am.invoice_date))
                        BETWEEN 1 AND 30
                        THEN am.amount_residual ELSE 0
                    END AS overdue_1_30,
                    CASE WHEN (CURRENT_DATE - COALESCE(am.invoice_date_due, am.invoice_date))
                        BETWEEN 31 AND 60
                        THEN am.amount_residual ELSE 0
                    END AS overdue_31_60,
                    CASE WHEN (CURRENT_DATE - COALESCE(am.invoice_date_due, am.invoice_date))
                        BETWEEN 61 AND 90
                        THEN am.amount_residual ELSE 0
                    END AS overdue_61_90,
                    CASE WHEN (CURRENT_DATE - COALESCE(am.invoice_date_due, am.invoice_date)) > 90
                        THEN am.amount_residual ELSE 0
                    END AS overdue_91_plus,
                    am.company_id
                FROM account_move am
                -- Link vendor bill -> project via PO -> SO -> SOL -> project
                LEFT JOIN LATERAL (
                    SELECT pp2.id
                    FROM purchase_order po2
                    JOIN sale_order so2
                        ON po2.origin IS NOT NULL
                        AND po2.origin LIKE '%%' || so2.name || '%%'
                    JOIN sale_order_line sol2 ON sol2.order_id = so2.id
                    JOIN project_project pp2 ON pp2.sale_line_id = sol2.id
                    WHERE am.invoice_origin IS NOT NULL
                    AND am.invoice_origin LIKE '%%' || po2.name || '%%'
                    LIMIT 1
                ) pp ON true
                WHERE am.move_type = 'in_invoice'
                    AND am.state = 'posted'
                    AND am.amount_residual > 0
            )
        """)

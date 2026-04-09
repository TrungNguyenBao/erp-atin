"""SQL view: project revenue report based on sale orders."""

from odoo import api, fields, models, tools


class ProjectRevenueReport(models.Model):
    _name = 'project.revenue.report'
    _description = 'Project Revenue Report'
    _auto = False
    _order = 'date_order desc'

    sale_order_id = fields.Many2one('sale.order', string='Sales Order', readonly=True)
    project_id = fields.Many2one('project.project', string='Project', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    user_id = fields.Many2one('res.users', string='Salesperson', readonly=True)
    date_order = fields.Date(string='Order Date', readonly=True)
    revenue = fields.Float(string='Revenue', readonly=True)
    purchase_cost = fields.Float(string='Purchase Cost', readonly=True)
    gross_profit = fields.Float(string='Gross Profit', readonly=True)
    margin_pct = fields.Float(string='Margin %', readonly=True)
    invoiced = fields.Float(string='Invoiced', readonly=True)
    paid = fields.Float(string='Paid', readonly=True)
    residual = fields.Float(string='Outstanding', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)

    def init(self):
        """Create SQL view for SO-based revenue report."""
        tools.drop_view_if_exists(self.env.cr, self._table)
        # Use ROW_NUMBER to handle multiple projects per SO
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    row_number() OVER () AS id,
                    so.id AS sale_order_id,
                    pp.id AS project_id,
                    so.partner_id,
                    so.user_id,
                    so.date_order::date AS date_order,
                    so.amount_untaxed AS revenue,
                    COALESCE(po_agg.purchase_cost, 0) AS purchase_cost,
                    so.amount_untaxed - COALESCE(po_agg.purchase_cost, 0)
                        AS gross_profit,
                    CASE WHEN so.amount_untaxed > 0
                        THEN (so.amount_untaxed - COALESCE(po_agg.purchase_cost, 0))
                             / so.amount_untaxed * 100
                        ELSE 0
                    END AS margin_pct,
                    COALESCE(inv_agg.invoiced, 0) AS invoiced,
                    COALESCE(inv_agg.paid, 0) AS paid,
                    COALESCE(inv_agg.residual, 0) AS residual,
                    so.company_id
                FROM sale_order so
                -- Link SO -> project (first matching project via SOL or analytic)
                LEFT JOIN LATERAL (
                    SELECT pp2.id
                    FROM project_project pp2
                    WHERE pp2.sale_line_id IN (
                        SELECT sol2.id FROM sale_order_line sol2
                        WHERE sol2.order_id = so.id
                    )
                    LIMIT 1
                ) pp ON true
                -- PO costs: use LIKE for comma-separated origins
                LEFT JOIN (
                    SELECT origin,
                        SUM(amount_untaxed) AS purchase_cost
                    FROM purchase_order
                    WHERE state IN ('purchase', 'done')
                    GROUP BY origin
                ) po_agg ON po_agg.origin LIKE '%%' || so.name || '%%'
                -- Invoice totals: use LIKE for comma-separated origins
                LEFT JOIN (
                    SELECT invoice_origin,
                        SUM(amount_total) AS invoiced,
                        SUM(amount_total - amount_residual) AS paid,
                        SUM(amount_residual) AS residual
                    FROM account_move
                    WHERE move_type = 'out_invoice'
                        AND state = 'posted'
                    GROUP BY invoice_origin
                ) inv_agg ON inv_agg.invoice_origin LIKE '%%' || so.name || '%%'
                WHERE so.state IN ('sale', 'done')
            )
        """)

    @api.model
    def get_dashboard_data(self, project_id=False):
        """Return aggregated data for OWL financial dashboard."""
        self.check_access_rights('read', raise_exception=True)
        domain = []
        if project_id:
            domain.append(('project_id', '=', project_id))

        # Revenue totals
        revenue_data = self.read_group(
            domain, ['revenue', 'purchase_cost', 'gross_profit'], []
        )
        totals = {
            'revenue': revenue_data[0]['revenue'] or 0 if revenue_data else 0,
            'cost': revenue_data[0]['purchase_cost'] or 0 if revenue_data else 0,
            'gross_profit': revenue_data[0]['gross_profit'] or 0 if revenue_data else 0,
            'receivable': 0,
            'payable': 0,
        }

        # Receivable/Payable totals (batched)
        recv_model = self.env['project.receivable.report']
        pay_model = self.env['project.payable.report']
        recv_domain = [('project_id', '=', project_id)] if project_id else []
        pay_domain = [('project_id', '=', project_id)] if project_id else []

        recv_total = recv_model.read_group(recv_domain, ['amount_residual'], [])
        if recv_total:
            totals['receivable'] = recv_total[0]['amount_residual'] or 0
        pay_total = pay_model.read_group(pay_domain, ['amount_residual'], [])
        if pay_total:
            totals['payable'] = pay_total[0]['amount_residual'] or 0

        # Batched per-project receivable/payable (avoid N+1)
        recv_by_project = {}
        for r in recv_model.read_group(
            recv_domain, ['project_id', 'amount_residual'], ['project_id']
        ):
            if r['project_id']:
                recv_by_project[r['project_id'][0]] = r['amount_residual'] or 0

        pay_by_project = {}
        for r in pay_model.read_group(
            pay_domain, ['project_id', 'amount_residual'], ['project_id']
        ):
            if r['project_id']:
                pay_by_project[r['project_id'][0]] = r['amount_residual'] or 0

        # Per-project breakdown
        project_data = self.read_group(
            domain,
            ['project_id', 'revenue', 'purchase_cost', 'gross_profit'],
            ['project_id'],
        )
        projects = []
        for row in project_data:
            pid = row['project_id']
            if not pid:
                continue
            rev = row['revenue'] or 0
            cost = row['purchase_cost'] or 0
            profit = row['gross_profit'] or 0
            margin = round(profit / rev * 100, 1) if rev else 0
            projects.append({
                'id': pid[0],
                'name': pid[1],
                'revenue': rev,
                'cost': cost,
                'profit': profit,
                'margin': margin,
                'receivable': recv_by_project.get(pid[0], 0),
                'payable': pay_by_project.get(pid[0], 0),
            })

        # Aging buckets from receivable report (5 buckets)
        aging = {
            'current': 0, 'days_30': 0, 'days_60': 0,
            'days_90': 0, 'over_90': 0,
        }
        aging_data = recv_model.read_group(
            recv_domain,
            ['not_due', 'overdue_1_30', 'overdue_31_60',
             'overdue_61_90', 'overdue_91_plus'],
            [],
        )
        if aging_data:
            aging['current'] = aging_data[0].get('not_due', 0) or 0
            aging['days_30'] = aging_data[0].get('overdue_1_30', 0) or 0
            aging['days_60'] = aging_data[0].get('overdue_31_60', 0) or 0
            aging['days_90'] = aging_data[0].get('overdue_61_90', 0) or 0
            aging['over_90'] = aging_data[0].get('overdue_91_plus', 0) or 0

        return {
            'totals': totals,
            'projects': projects,
            'aging': aging,
        }

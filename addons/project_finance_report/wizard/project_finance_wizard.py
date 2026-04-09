"""Wizard for filtering project financial reports."""

from odoo import fields, models


class ProjectFinanceWizard(models.TransientModel):
    _name = 'project.finance.wizard'
    _description = 'Project Finance Report Filter'

    date_from = fields.Date(string='From', required=True,
                            default=fields.Date.context_today)
    date_to = fields.Date(string='To', required=True,
                          default=fields.Date.context_today)
    project_ids = fields.Many2many('project.project', string='Projects')
    partner_ids = fields.Many2many('res.partner', string='Partners')
    report_type = fields.Selection([
        ('revenue', 'Revenue Report'),
        ('receivable', 'Receivable Report'),
        ('payable', 'Payable Report'),
    ], string='Report Type', required=True, default='revenue')

    def action_view_report(self):
        """Open the selected report with applied filters."""
        self.ensure_one()

        report_map = {
            'revenue': {
                'model': 'project.revenue.report',
                'name': 'Revenue by Project',
                'date_field': 'date_order',
            },
            'receivable': {
                'model': 'project.receivable.report',
                'name': 'Receivable by Project',
                'date_field': 'invoice_date',
            },
            'payable': {
                'model': 'project.payable.report',
                'name': 'Payable by Project',
                'date_field': 'invoice_date',
            },
        }
        cfg = report_map[self.report_type]

        domain = [
            (cfg['date_field'], '>=', self.date_from),
            (cfg['date_field'], '<=', self.date_to),
        ]
        if self.project_ids:
            domain.append(('project_id', 'in', self.project_ids.ids))
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))

        return {
            'type': 'ir.actions.act_window',
            'name': cfg['name'],
            'res_model': cfg['model'],
            'view_mode': 'pivot,tree,graph',
            'domain': domain,
            'target': 'current',
            'context': {'group_by': ['project_id']},
        }

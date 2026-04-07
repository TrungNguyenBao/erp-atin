# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class SprintReport(models.AbstractModel):
    _name = 'report.project_scrum.report_sprint_summary'
    _description = 'Sprint Summary Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        sprints = self.env['project.sprint'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'project.sprint',
            'docs': sprints,
        }

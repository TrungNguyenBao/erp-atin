# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProjectTaskScrum(models.Model):
    _inherit = 'project.task'

    sprint_id = fields.Many2one(
        'project.sprint', string='Sprint',
        domain="[('project_id', '=', project_id), ('state', '!=', 'closed')]",
        tracking=True, index=True,
        groups='project_scrum.group_project_scrum')
    story_points = fields.Integer(
        string='Story Points', tracking=True,
        groups='project_scrum.group_project_scrum',
        help='Relative complexity estimate (Fibonacci: 1, 2, 3, 5, 8, 13, 21)')
    is_in_backlog = fields.Boolean(
        compute='_compute_is_in_backlog', store=True, index=True,
        help='True if task has no sprint assigned')
    # H1 fix: related field so task form can check scrum without parent context
    enable_scrum = fields.Boolean(
        related='project_id.enable_scrum', readonly=True)

    @api.depends('sprint_id')
    def _compute_is_in_backlog(self):
        for task in self:
            task.is_in_backlog = not task.sprint_id

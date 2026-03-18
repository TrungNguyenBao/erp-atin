# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

RELEASE_STATES = [
    ('planning', 'Planning'),
    ('in_progress', 'In Progress'),
    ('released', 'Released'),
]


class ProjectRelease(models.Model):
    _name = 'project.release'
    _description = 'Release'
    _inherit = ['mail.thread']
    _order = 'target_date desc, id desc'
    _check_company_auto = True

    name = fields.Char(required=True, tracking=True)
    project_id = fields.Many2one(
        'project.project', required=True,
        ondelete='cascade', index=True)
    target_date = fields.Date(tracking=True)
    state = fields.Selection(
        RELEASE_STATES, default='planning', tracking=True)
    description = fields.Html()
    sprint_ids = fields.Many2many('project.sprint', string='Sprints')
    company_id = fields.Many2one(
        related='project_id.company_id', store=True, index=True)

    # Computed stats
    sprint_count = fields.Integer(compute='_compute_stats')
    total_points = fields.Integer(compute='_compute_stats')
    completed_points = fields.Integer(compute='_compute_stats')

    @api.depends('sprint_ids.committed_points', 'sprint_ids.completed_points')
    def _compute_stats(self):
        for release in self:
            sprints = release.sprint_ids
            release.sprint_count = len(sprints)
            release.total_points = sum(sprints.mapped('committed_points'))
            release.completed_points = sum(sprints.mapped('completed_points'))

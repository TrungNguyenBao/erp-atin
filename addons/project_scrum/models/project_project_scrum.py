# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


METHODOLOGY_SELECTION = [
    ('default', 'Default'),
    ('scrum', 'Scrum'),
    ('kanban', 'Kanban'),
]


class ProjectProjectScrum(models.Model):
    _inherit = 'project.project'

    methodology = fields.Selection(
        METHODOLOGY_SELECTION, default='default', required=True,
        tracking=True,
        help='Project management methodology: Default, Scrum, or Kanban')
    enable_scrum = fields.Boolean(
        string='Scrum',
        compute='_compute_enable_scrum',
        inverse='_inverse_enable_scrum',
        store=True,
        help='Enable Scrum features: sprints, story points, velocity tracking')
    sprint_ids = fields.One2many(
        'project.sprint', 'project_id', string='Sprints')
    active_sprint_id = fields.Many2one(
        'project.sprint', compute='_compute_active_sprint_id',
        string='Active Sprint')
    sprint_count = fields.Integer(
        compute='_compute_sprint_count',
        groups='project_scrum.group_project_scrum')

    # Phase 3: velocity forecast
    velocity_forecast = fields.Float(
        string='Forecasted Velocity',
        compute='_compute_velocity_forecast',
        groups='project_scrum.group_project_scrum',
        help='Predicted next sprint capacity based on 3-sprint rolling average')

    # Phase 3: standup digest toggle
    enable_standup_digest = fields.Boolean(
        string='Daily Standup Digest',
        help='Send daily email summary of active sprint status to followers')

    @api.depends('methodology')
    def _compute_enable_scrum(self):
        for project in self:
            project.enable_scrum = project.methodology == 'scrum'

    def _inverse_enable_scrum(self):
        for project in self:
            if project.enable_scrum and project.methodology != 'scrum':
                project.methodology = 'scrum'
            elif not project.enable_scrum and project.methodology == 'scrum':
                project.methodology = 'default'

    # H2 fix: batch search instead of N+1 loop
    @api.depends('sprint_ids.state')
    def _compute_active_sprint_id(self):
        active_sprints = self.env['project.sprint'].search([
            ('project_id', 'in', self.ids),
            ('state', '=', 'active'),
        ])
        sprint_map = {s.project_id.id: s for s in active_sprints}
        for project in self:
            project.active_sprint_id = sprint_map.get(project.id, False)

    # M5 fix: use _read_group for efficient counting
    @api.depends('sprint_ids')
    def _compute_sprint_count(self):
        sprint_data = self.env['project.sprint']._read_group(
            [('project_id', 'in', self.ids)],
            ['project_id'], ['__count'],
        )
        count_map = {p.id: c for p, c in sprint_data}
        for project in self:
            project.sprint_count = count_map.get(project.id, 0)

    def _compute_velocity_forecast(self):
        for project in self:
            closed_sprints = self.env['project.sprint'].search([
                ('project_id', '=', project.id),
                ('state', '=', 'closed'),
                ('velocity', '>', 0),
            ], order='end_date desc', limit=3)
            if closed_sprints:
                project.velocity_forecast = round(
                    sum(closed_sprints.mapped('velocity')) / len(closed_sprints), 1)
            else:
                project.velocity_forecast = 0

    # M4 fix: action method filtering sprints by current project
    def action_view_project_sprints(self):
        """Open sprints for this project."""
        self.ensure_one()
        return {
            'name': _('Sprints'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.sprint',
            'view_mode': 'list,kanban,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

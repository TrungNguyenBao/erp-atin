# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProjectProjectScrum(models.Model):
    _inherit = 'project.project'

    enable_scrum = fields.Boolean(
        string='Scrum',
        default=lambda self: self.env.user.has_group(
            'project_scrum.group_project_scrum'),
        help='Enable Scrum features: sprints, story points, velocity tracking')
    sprint_ids = fields.One2many(
        'project.sprint', 'project_id', string='Sprints')
    active_sprint_id = fields.Many2one(
        'project.sprint', compute='_compute_active_sprint_id',
        string='Active Sprint')
    sprint_count = fields.Integer(
        compute='_compute_sprint_count',
        groups='project_scrum.group_project_scrum')

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

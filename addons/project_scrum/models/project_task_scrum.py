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
    # Related field so task form can check scrum without parent context
    enable_scrum = fields.Boolean(
        related='project_id.enable_scrum', readonly=True)

    # Epic assignment (Phase 3)
    epic_id = fields.Many2one(
        'project.epic', string='Epic',
        domain="[('project_id', '=', project_id)]",
        tracking=True, index=True,
        groups='project_scrum.group_project_scrum')

    # Task classification
    task_type = fields.Selection([
        ('story', 'User Story'),
        ('task', 'Task'),
        ('bug', 'Bug'),
        ('improvement', 'Improvement'),
        ('epic', 'Epic'),
    ], string='Task Type', default='task',
        groups='project_scrum.group_project_scrum')

    # Definition of Done
    acceptance_criteria = fields.Text(
        string='Acceptance Criteria',
        help='Conditions that must be met for this task to be considered done',
        groups='project_scrum.group_project_scrum')

    # Impediment tracking (Phase 3)
    is_blocked = fields.Boolean(
        string='Blocked', tracking=True,
        groups='project_scrum.group_project_scrum')
    blocker_description = fields.Text(
        string='Blocker Description',
        groups='project_scrum.group_project_scrum')
    blocker_owner_id = fields.Many2one(
        'res.users', string='Blocker Owner',
        groups='project_scrum.group_project_scrum',
        help='Person responsible for resolving this impediment')

    @api.depends('sprint_id')
    def _compute_is_in_backlog(self):
        for task in self:
            task.is_in_backlog = not task.sprint_id

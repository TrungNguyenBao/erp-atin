# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProjectTaskScrum(models.Model):
    _inherit = 'project.task'

    sprint_id = fields.Many2one(
        'project.sprint', string='Sprint',
        domain="[('project_id', '=', project_id), ('state', 'not in', ['done', 'cancelled'])]",
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

    @api.model
    def get_backlog_page_data(self, project_id):
        """Return backlog data for OWL BacklogPage component."""
        domain = [
            ('project_id', '=', project_id),
            ('sprint_id', '=', False),
            ('child_ids', '=', False),
        ]
        tasks = self.search(domain, order='sequence asc, priority desc, id desc', limit=200)
        tasks.mapped('user_ids')  # prefetch

        task_list = []
        for t in tasks:
            assignee = t.user_ids[:1]
            task_list.append({
                'id': t.id,
                'name': t.name,
                'priority': t.priority,
                'story_points': t.story_points,
                'user_id': assignee.id if assignee else False,
                'user_name': assignee.name if assignee else '',
                'stage_name': t.stage_id.name,
                'task_type': t.task_type or 'task',
                'epic_id': t.epic_id.id if t.epic_id else False,
                'epic_name': t.epic_id.name if t.epic_id else 'No Epic',
            })

        epics = self.env['project.epic'].search_read(
            [('project_id', '=', project_id)],
            ['id', 'name'],
            order='sequence asc',
        )

        return {
            'tasks': task_list,
            'epics': epics,
            'stats': {
                'total': len(task_list),
                'unestimated': sum(1 for t in task_list if not t['story_points']),
                'total_sp': sum(t['story_points'] for t in task_list),
            },
        }

# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from odoo.addons.project.models.project_task import CLOSED_STATES

SPRINT_STATES = [
    ('draft', 'Draft'),
    ('active', 'Active'),
    ('closed', 'Closed'),
]


class ProjectSprint(models.Model):
    _name = 'project.sprint'
    _description = 'Sprint'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc, id desc'
    _check_company_auto = True

    # Core fields
    name = fields.Char(required=True, tracking=True)
    project_id = fields.Many2one(
        'project.project', required=True, ondelete='cascade',
        tracking=True, index=True)
    goal = fields.Text(string='Sprint Goal', tracking=True)
    start_date = fields.Date(required=True, tracking=True)
    end_date = fields.Date(required=True, tracking=True)
    state = fields.Selection(
        SPRINT_STATES, default='draft', required=True,
        tracking=True, index=True, copy=False)
    capacity_points = fields.Integer(
        string='Planned Capacity (Points)', tracking=True,
        help='Total story points the team plans to deliver this sprint')

    # Relationships
    task_ids = fields.One2many('project.task', 'sprint_id', string='Tasks')
    company_id = fields.Many2one(
        related='project_id.company_id', store=True, index=True)

    # Computed task statistics
    task_count = fields.Integer(
        compute='_compute_task_stats', store=True)
    committed_points = fields.Integer(
        compute='_compute_task_stats', store=True,
        help='Sum of story points for all tasks in this sprint')
    completed_points = fields.Integer(
        compute='_compute_task_stats', store=True,
        help='Sum of story points for closed tasks in this sprint')
    remaining_points = fields.Integer(
        compute='_compute_task_stats', store=True)
    completion_percentage = fields.Float(
        compute='_compute_task_stats', store=True)

    # Velocity: snapshot taken at sprint close, not computed live
    velocity = fields.Integer(
        string='Velocity (Closed Points)', readonly=True,
        help='Snapshot of completed story points at sprint closure')

    # Daily log for burndown chart
    daily_log_ids = fields.One2many(
        'project.sprint.daily.log', 'sprint_id', string='Daily Logs')

    # Sprint Review fields
    review_notes = fields.Html(
        string='Sprint Review Notes',
        help='Summary of completed items and stakeholder feedback')
    review_date = fields.Datetime(string='Review Date')

    # Sprint Retrospective fields
    retro_went_well = fields.Html(string='What Went Well')
    retro_went_wrong = fields.Html(string='What Could Improve')
    retro_action_items = fields.Html(string='Action Items')
    retro_date = fields.Datetime(string='Retrospective Date')

    _sql_constraints = [
        ('date_check', 'CHECK(end_date >= start_date)',
         'End date must be after start date.'),
    ]

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------

    @api.depends('task_ids.story_points', 'task_ids.state')
    def _compute_task_stats(self):
        for sprint in self:
            tasks = sprint.task_ids
            committed = sum(tasks.mapped('story_points'))
            completed = sum(
                t.story_points for t in tasks if t.state in CLOSED_STATES)
            sprint.task_count = len(tasks)
            sprint.committed_points = committed
            sprint.completed_points = completed
            sprint.remaining_points = committed - completed
            sprint.completion_percentage = (
                round(completed / committed * 100, 1) if committed else 0)

    # -------------------------------------------------------------------------
    # Constraints
    # -------------------------------------------------------------------------

    @api.constrains('state', 'project_id')
    def _check_single_active_sprint(self):
        """Enforce at most one active sprint per project."""
        for sprint in self:
            if sprint.state == 'active':
                other_active = self.search_count([
                    ('project_id', '=', sprint.project_id.id),
                    ('state', '=', 'active'),
                    ('id', '!=', sprint.id),
                ])
                if other_active:
                    raise ValidationError(_(
                        'Project "%(project)s" already has an active sprint. '
                        'Close it before starting a new one.',
                        project=sprint.project_id.name,
                    ))

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------

    def action_plan_sprint(self):
        """Open the sprint planning wizard."""
        self.ensure_one()
        return {
            'name': _('Sprint Planning'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.sprint.planning.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sprint_id': self.id},
        }

    def action_start_sprint(self):
        """Transition sprint from draft to active."""
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError(_('Only draft sprints can be started.'))
        self.write({'state': 'active'})

    def action_close_sprint(self):
        """Open the sprint close wizard."""
        self.ensure_one()
        return {
            'name': _('Close Sprint'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.sprint.close.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sprint_id': self.id},
        }

    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------

    def action_view_tasks(self):
        """Open tasks for this sprint."""
        self.ensure_one()
        return {
            'name': _('Sprint Tasks'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'kanban,list,form',
            'domain': [('sprint_id', '=', self.id)],
            'context': {
                'default_sprint_id': self.id,
                'default_project_id': self.project_id.id,
            },
        }

    def _compute_display_name(self):
        for sprint in self:
            sprint.display_name = f"[{sprint.project_id.name}] {sprint.name}"

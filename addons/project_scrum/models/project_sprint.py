# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from odoo.addons.project.models.project_task import CLOSED_STATES

SPRINT_STATES = [
    ('draft', 'Draft'),
    ('active', 'Active'),
    ('review', 'In Review'),
    ('done', 'Done'),
    ('cancelled', 'Cancelled'),
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
    scrum_master_id = fields.Many2one(
        'res.users', string='Scrum Master',
        tracking=True,
        groups='project_scrum.group_project_scrum',
        help='Scrum Master responsible for this sprint')
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

    # Ceremonies
    ceremony_ids = fields.One2many(
        'scrum.ceremony', 'sprint_id', string='Ceremonies')
    ceremony_count = fields.Integer(compute='_compute_ceremony_count')

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

    def _compute_ceremony_count(self):
        for sprint in self:
            sprint.ceremony_count = len(sprint.ceremony_ids)

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

    def action_review_sprint(self):
        """Transition sprint from active to review."""
        self.ensure_one()
        if self.state != 'active':
            raise ValidationError(
                _('Only active sprints can be moved to review.'))
        self.write({'state': 'review'})

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

    def action_cancel_sprint(self):
        """Cancel sprint: return all tasks to backlog."""
        self.ensure_one()
        if self.state not in ('draft', 'active'):
            raise ValidationError(
                _('Only draft or active sprints can be cancelled.'))
        self.task_ids.write({'sprint_id': False})
        self.write({'state': 'cancelled'})

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

    def action_print_sprint_report(self):
        """Generate Sprint Summary PDF report."""
        self.ensure_one()
        return self.env.ref(
            'project_scrum.action_report_sprint_summary'
        ).report_action(self)

    def action_view_ceremonies(self):
        """Open ceremonies for this sprint."""
        self.ensure_one()
        return {
            'name': _('Ceremonies'),
            'type': 'ir.actions.act_window',
            'res_model': 'scrum.ceremony',
            'view_mode': 'list,form',
            'domain': [('sprint_id', '=', self.id)],
            'context': {
                'default_sprint_id': self.id,
                'default_project_id': self.project_id.id,
            },
        }

    def _compute_display_name(self):
        for sprint in self:
            sprint.display_name = f"[{sprint.project_id.name}] {sprint.name}"

    # -------------------------------------------------------------------------
    # OWL Sprint Board RPC methods
    # -------------------------------------------------------------------------

    def get_board_data(self):
        """Return sprint board data grouped by stage for OWL Sprint Board."""
        self.ensure_one()
        wip_limit = self.project_id.wip_limit or 0
        stages = self.project_id.type_ids.sorted('sequence')

        # Prefetch all leaf tasks + user_ids in one batch
        all_tasks = self.task_ids.filtered(lambda t: not t.child_ids)
        all_tasks.mapped('user_ids')  # prefetch users in single query

        # Group tasks by stage_id
        task_by_stage = {}
        for t in all_tasks:
            task_by_stage.setdefault(t.stage_id.id, []).append(t)

        result = []
        for stage in stages:
            stage_tasks = task_by_stage.get(stage.id, [])
            task_data = []
            for t in stage_tasks:
                assignee = t.user_ids[:1]
                task_data.append({
                    'id': t.id,
                    'name': t.name,
                    'story_points': t.story_points,
                    'user_id': assignee.id if assignee else False,
                    'user_name': assignee.name if assignee else '',
                    'user_avatar': (
                        f'/web/image/res.users/{assignee.id}/avatar_128'
                        if assignee else ''
                    ),
                    'task_type': t.task_type or 'task',
                    'is_blocked': t.is_blocked,
                    'blocker_description': t.blocker_description or '',
                })
            task_count = len(task_data)
            result.append({
                'stage_id': stage.id,
                'stage_name': stage.name,
                'is_closed': stage.fold,
                'tasks': task_data,
                'task_count': task_count,
                'total_sp': sum(t['story_points'] for t in task_data),
                'wip_exceeded': wip_limit > 0 and task_count > wip_limit,
            })
        return {
            'columns': result,
            'wip_limit': wip_limit,
            'scrum_master': self.scrum_master_id.name or '',
        }

    def get_backlog_tasks(self):
        """Return unassigned backlog tasks for the sprint board sidebar."""
        self.ensure_one()
        domain = [
            ('project_id', '=', self.project_id.id),
            ('sprint_id', '=', False),
            ('child_ids', '=', False),
        ]
        tasks = self.env['project.task'].search(domain, limit=50, order='sequence asc, priority desc, id desc')
        result = []
        for t in tasks:
            assignee = t.user_ids[:1]
            result.append({
                'id': t.id,
                'name': t.name,
                'story_points': t.story_points,
                'user_id': assignee.id if assignee else False,
                'user_name': assignee.name if assignee else '',
                'task_type': t.task_type or 'task',
            })
        return result

    def move_task_to_sprint(self, task_id):
        """Assign a backlog task to this sprint."""
        self.ensure_one()
        task = self.env['project.task'].browse(task_id)
        task.write({'sprint_id': self.id})

    def reorder_backlog_task(self, task_id, new_sequence):
        """Update sequence of a backlog task for priority reorder."""
        task = self.env['project.task'].browse(task_id)
        if task.exists() and not task.sprint_id:
            task.write({'sequence': new_sequence})

    def quick_create_backlog_task(self, values):
        """Create a new backlog task from Sprint Board quick-create form."""
        self.ensure_one()
        defaults = {
            'project_id': self.project_id.id,
            'sprint_id': False,
            'task_type': 'story',
        }
        defaults.update(values)
        task = self.env['project.task'].create(defaults)
        return {
            'id': task.id,
            'name': task.name,
            'story_points': task.story_points or 0,
            'task_type': task.task_type or 'story',
        }

    def get_burndown_data(self):
        """Return burndown chart data for OWL BurndownChart widget."""
        self.ensure_one()
        total_sp = self.committed_points or 0
        if not self.start_date or not self.end_date:
            return {'labels': [], 'actual': [], 'ideal': [], 'total_sp': 0}

        days = (self.end_date - self.start_date).days + 1

        # Build ideal line: day 0 = total_sp, last day = 0
        ideal_labels = [
            (self.start_date + timedelta(days=i)).strftime('%m/%d')
            for i in range(days)
        ]
        ideal_values = [
            round(total_sp - (total_sp / max(days - 1, 1) * i), 1)
            for i in range(days)
        ]

        # Build actual line from daily log; interpolate missing days
        logs = self.env['project.sprint.daily.log'].search(
            [('sprint_id', '=', self.id)], order='date asc'
        )
        log_map = {log.date: log.remaining_points for log in logs}

        actual_labels = []
        actual_values = []
        last_known = total_sp
        for i in range(days):
            day = self.start_date + timedelta(days=i)
            if day > fields.Date.context_today(self):
                break
            val = log_map.get(day, last_known)  # interpolate gap with last known
            last_known = val
            actual_labels.append(day.strftime('%m/%d'))
            actual_values.append(val)

        return {
            'sprint_name': self.name,
            'total_sp': total_sp,
            'ideal_labels': ideal_labels,
            'ideal': ideal_values,
            'labels': actual_labels,
            'actual': actual_values,
            'state': self.state,
        }

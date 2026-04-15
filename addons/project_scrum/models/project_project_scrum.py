# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


METHODOLOGY_SELECTION = [
    ('default', 'Default'),
    ('scrum', 'Scrum'),
    ('kanban', 'Kanban'),
]


class ProjectProjectScrum(models.Model):
    _inherit = 'project.project'

    project_code = fields.Char(
        string='Project Code',
        tracking=True, index=True, copy=False,
        help='Unique project reference code (e.g. 2026_SCB_HH)')

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

    wip_limit = fields.Integer(
        string='WIP Limit', default=0,
        groups='project_scrum.group_project_scrum',
        help='Maximum tasks per stage column on Sprint Board. 0 = no limit.')

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
                ('state', '=', 'done'),
                ('velocity', '>', 0),
            ], order='end_date desc', limit=3)
            if closed_sprints:
                project.velocity_forecast = round(
                    sum(closed_sprints.mapped('velocity')) / len(closed_sprints), 1)
            else:
                project.velocity_forecast = 0

    def get_dashboard_data(self):
        """Return all Agile Dashboard widget data in a single RPC call."""
        self.ensure_one()
        active_sprint = self.active_sprint_id
        sprint_data = False
        if active_sprint:
            days_remaining = (active_sprint.end_date - fields.Date.today()).days
            sprint_data = {
                'id':             active_sprint.id,
                'name':           active_sprint.name,
                'start_date':     active_sprint.start_date.strftime('%b %d') if active_sprint.start_date else '',
                'end_date':       active_sprint.end_date.strftime('%b %d') if active_sprint.end_date else '',
                'committed':      active_sprint.committed_points,
                'completed':      active_sprint.completed_points,
                'remaining':      active_sprint.remaining_points,
                'completion_pct': active_sprint.completion_percentage,
                'days_remaining': max(days_remaining, 0),
                'task_count':     active_sprint.task_count,
                'done_tasks':     len(active_sprint.task_ids.filtered(lambda t: t.stage_id.fold)),
            }
        return {
            'project_id':         self.id,
            'project_name':       self.name,
            'sprint':             sprint_data,
            'team_workload':      self._get_team_workload(active_sprint),
            'backlog_health':     self._get_backlog_health(),
            'recent_activity':    self._get_recent_activity(limit=8),
            'kpi':                self._get_kpi_data(active_sprint, sprint_data),
            'task_distribution':  self._get_task_distribution(active_sprint),
        }

    def _get_team_workload(self, sprint=None):
        """Return SP assigned per team member in the active sprint."""
        if not sprint:
            return []
        workload = {}
        for task in sprint.task_ids:
            sp = task.story_points or 0
            for user in task.user_ids:
                if user.id not in workload:
                    workload[user.id] = {'name': user.name, 'sp': 0, 'task_count': 0}
                workload[user.id]['sp'] += sp
                workload[user.id]['task_count'] += 1
        result = sorted(workload.values(), key=lambda x: x['sp'], reverse=True)
        max_sp = result[0]['sp'] if result else 1
        for item in result:
            item['pct'] = round(item['sp'] / max(max_sp, 1) * 100)
        return result[:8]  # top 8 members

    def _get_backlog_health(self):
        """Return backlog statistics for health widget."""
        domain_base = [
            ('project_id', '=', self.id),
            ('sprint_id', '=', False),
            ('child_ids', '=', False),
        ]
        BacklogTask = self.env['project.task']
        total        = BacklogTask.search_count(domain_base)
        unestimated  = BacklogTask.search_count(domain_base + [('story_points', '=', 0)])
        high_prio    = BacklogTask.search_count(domain_base + [('priority', '=', '1')])
        total_sp     = sum(BacklogTask.search(domain_base).mapped('story_points'))
        return {
            'total':       total,
            'unestimated': unestimated,
            'high_prio':   high_prio,
            'total_sp':    total_sp,
        }

    def _get_kpi_data(self, active_sprint, sprint_data):
        """Return KPI card data for dashboard."""
        from odoo.addons.project.models.project_task import CLOSED_STATES
        overdue_domain = [
            ('project_id', '=', self.id),
            ('date_deadline', '<', fields.Date.today()),
            ('state', 'not in', list(CLOSED_STATES)),
        ]
        if active_sprint:
            overdue_domain.append(('sprint_id', '=', active_sprint.id))
        return {
            'total_projects': self.env['project.project'].search_count(
                [('enable_scrum', '=', True)]),
            'active_sprints': self.env['project.sprint'].search_count(
                [('project_id', '=', self.id), ('state', '=', 'active')]),
            'completion_rate': sprint_data['completion_pct'] if sprint_data else 0,
            'team_velocity': self.velocity_forecast,
            'overdue_tasks': self.env['project.task'].search_count(overdue_domain),
        }

    def _get_task_distribution(self, sprint=None):
        """Return task counts grouped by stage for pie chart."""
        domain = [('project_id', '=', self.id)]
        if sprint:
            domain.append(('sprint_id', '=', sprint.id))
        groups = self.env['project.task']._read_group(
            domain, ['stage_id'], ['__count'])
        return [{'stage': stage.name, 'count': count}
                for stage, count in groups if count > 0]

    def _get_recent_activity(self, limit=8):
        """Return recent task stage changes for the activity feed."""
        # Fetch recent mail messages about stage changes in this project
        domain = [
            ('model', '=', 'project.task'),
            ('message_type', 'in', ['notification', 'comment']),
            ('res_id', 'in', self.task_ids.ids),
        ]
        messages = self.env['mail.message'].search(
            domain, order='date desc', limit=limit
        )
        result = []
        for msg in messages:
            task = self.env['project.task'].browse(msg.res_id)
            if not task.exists():
                continue
            result.append({
                'task_name': task.name,
                'author':    msg.author_id.name if msg.author_id else 'System',
                'body':      msg.body[:80] if msg.body else '',
                'date':      msg.date.strftime('%b %d, %H:%M') if msg.date else '',
            })
        return result

    def get_velocity_data(self, limit=6):
        """Return velocity chart data for OWL VelocityChart widget."""
        self.ensure_one()
        closed_sprints = self.env['project.sprint'].search(
            [('project_id', '=', self.id), ('state', '=', 'done')],
            order='end_date asc',
            limit=limit,
        )
        labels     = [s.name for s in closed_sprints]
        committed  = [s.committed_points for s in closed_sprints]
        completed  = [s.completed_points for s in closed_sprints]
        velocities = [s.velocity or s.completed_points for s in closed_sprints]

        # Rolling 3-sprint average (pad with None for early sprints)
        rolling = []
        window = 3
        for i, _ in enumerate(velocities):
            if i + 1 < window:
                rolling.append(None)
            else:
                avg = sum(velocities[i - window + 1: i + 1]) / window
                rolling.append(round(avg, 1))

        return {
            'labels':       labels,
            'committed':    committed,
            'completed':    completed,
            'rolling_avg':  rolling,
            'sprint_count': len(closed_sprints),
            'avg_velocity': round(sum(velocities) / len(velocities), 1) if velocities else 0,
            'forecast':     rolling[-1] if rolling and rolling[-1] is not None else (
                round(sum(velocities) / len(velocities), 1) if velocities else 0
            ),
        }

    # M4 fix: action method filtering sprints by current project
    def get_cycle_time_data(self, sprint_id=False):
        """Return lead/cycle time data for completed tasks."""
        self.ensure_one()
        from odoo.addons.project.models.project_task import CLOSED_STATES
        domain = [
            ('project_id', '=', self.id),
            ('state', 'in', list(CLOSED_STATES)),
        ]
        if sprint_id:
            domain.append(('sprint_id', '=', sprint_id))
        tasks = self.env['project.task'].search(domain, limit=100, order='write_date desc')

        task_data = []
        total_lead = 0
        total_cycle = 0
        for t in tasks:
            # Lead time: create_date to write_date (last state change)
            lead_days = (t.write_date.date() - t.create_date.date()).days
            # Cycle time approximation: lead time (without tracking history parsing)
            cycle_days = max(lead_days - 1, 0)  # simplified
            task_data.append({
                'id': t.id,
                'name': t.name,
                'lead_time': lead_days,
                'cycle_time': cycle_days,
                'story_points': t.story_points,
                'completed_date': t.write_date.date().isoformat(),
            })
            total_lead += lead_days
            total_cycle += cycle_days

        count = len(task_data) or 1
        return {
            'tasks': task_data,
            'averages': {
                'lead': round(total_lead / count, 1),
                'cycle': round(total_cycle / count, 1),
            },
            'count': len(task_data),
        }

    def action_print_velocity_report(self):
        """Generate Velocity PDF report."""
        self.ensure_one()
        return self.env.ref(
            'project_scrum.action_report_velocity'
        ).report_action(self)

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

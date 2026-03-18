# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

from odoo.addons.project.models.project_task import CLOSED_STATES


class ProjectSprintDailyLog(models.Model):
    _name = 'project.sprint.daily.log'
    _description = 'Sprint Daily Snapshot'
    _order = 'date asc'
    _rec_name = 'date'

    sprint_id = fields.Many2one(
        'project.sprint', required=True,
        ondelete='cascade', index=True)
    project_id = fields.Many2one(
        related='sprint_id.project_id', store=True, index=True)
    date = fields.Date(required=True, index=True)
    remaining_points = fields.Integer(string='Remaining Points')
    completed_points = fields.Integer(string='Completed Points')
    total_tasks = fields.Integer()
    closed_tasks = fields.Integer()

    _sql_constraints = [
        ('unique_sprint_date', 'UNIQUE(sprint_id, date)',
         'One snapshot per sprint per day.'),
    ]

    @api.model
    def _cron_create_daily_snapshots(self):
        """Create daily snapshots for all active sprints."""
        active_sprints = self.env['project.sprint'].search([
            ('state', '=', 'active'),
        ])
        today = fields.Date.context_today(self)
        for sprint in active_sprints:
            tasks = sprint.task_ids
            committed = sum(tasks.mapped('story_points'))
            completed = sum(
                t.story_points for t in tasks if t.state in CLOSED_STATES)
            closed_count = len(
                tasks.filtered(lambda t: t.state in CLOSED_STATES))

            # Create or update today's snapshot
            existing = self.search([
                ('sprint_id', '=', sprint.id),
                ('date', '=', today),
            ], limit=1)
            vals = {
                'remaining_points': committed - completed,
                'completed_points': completed,
                'total_tasks': len(tasks),
                'closed_tasks': closed_count,
            }
            if existing:
                existing.write(vals)
            else:
                self.create({
                    'sprint_id': sprint.id,
                    'date': today,
                    **vals,
                })

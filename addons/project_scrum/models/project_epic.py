# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

from odoo.addons.project.models.project_task import CLOSED_STATES


class ProjectEpic(models.Model):
    _name = 'project.epic'
    _description = 'Epic'
    _inherit = ['mail.thread']
    _order = 'sequence, id'
    _check_company_auto = True

    name = fields.Char(required=True, tracking=True)
    description = fields.Html()
    project_id = fields.Many2one(
        'project.project', required=True,
        ondelete='cascade', index=True)
    sequence = fields.Integer(default=10)
    color = fields.Integer()
    company_id = fields.Many2one(
        related='project_id.company_id', store=True, index=True)

    # Relationships
    task_ids = fields.One2many('project.task', 'epic_id', string='Stories')
    tag_ids = fields.Many2many('project.tags')

    # Computed progress
    task_count = fields.Integer(
        compute='_compute_progress', store=True)
    done_task_count = fields.Integer(
        compute='_compute_progress', store=True)
    total_points = fields.Integer(
        compute='_compute_progress', store=True)
    completed_points = fields.Integer(
        compute='_compute_progress', store=True)
    progress_percentage = fields.Float(
        compute='_compute_progress', store=True)

    @api.depends('task_ids.story_points', 'task_ids.state')
    def _compute_progress(self):
        for epic in self:
            tasks = epic.task_ids
            total = sum(tasks.mapped('story_points'))
            completed = sum(
                t.story_points for t in tasks if t.state in CLOSED_STATES)
            done_count = len(
                tasks.filtered(lambda t: t.state in CLOSED_STATES))
            epic.task_count = len(tasks)
            epic.done_task_count = done_count
            epic.total_points = total
            epic.completed_points = completed
            epic.progress_percentage = (
                round(completed / total * 100, 1) if total else 0)

    @api.model
    def get_roadmap_data(self, project_id):
        """Return timeline data for OWL RoadmapTimeline component."""
        epics = self.search([('project_id', '=', project_id)], order='sequence asc')
        sprints = self.env['project.sprint'].search([
            ('project_id', '=', project_id),
            ('state', 'not in', ['cancelled']),
        ], order='start_date asc')

        epic_data = []
        for epic in epics:
            task_sprints = epic.task_ids.mapped('sprint_id').filtered(
                lambda s: s.start_date and s.end_date)
            start = min(task_sprints.mapped('start_date')) if task_sprints else None
            end = max(task_sprints.mapped('end_date')) if task_sprints else None
            epic_data.append({
                'id': epic.id,
                'name': epic.name,
                'color': epic.color,
                'task_count': epic.task_count,
                'progress': epic.progress_percentage,
                'total_points': epic.total_points,
                'start_date': start.isoformat() if start else '',
                'end_date': end.isoformat() if end else '',
            })

        sprint_data = [{
            'id': s.id, 'name': s.name, 'state': s.state,
            'start_date': s.start_date.isoformat(),
            'end_date': s.end_date.isoformat(),
        } for s in sprints if s.start_date and s.end_date]

        all_dates = ([s.start_date for s in sprints if s.start_date] +
                     [s.end_date for s in sprints if s.end_date])
        return {
            'epics': epic_data,
            'sprints': sprint_data,
            'date_range': {
                'start': min(all_dates).isoformat() if all_dates else '',
                'end': max(all_dates).isoformat() if all_dates else '',
            },
        }

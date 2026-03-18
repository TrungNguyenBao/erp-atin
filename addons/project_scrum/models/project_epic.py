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

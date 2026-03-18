# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SprintPlanningWizard(models.TransientModel):
    _name = 'project.sprint.planning.wizard'
    _description = 'Sprint Planning Wizard'

    sprint_id = fields.Many2one(
        'project.sprint', required=True, string='Sprint',
        domain="[('state', '=', 'draft')]",
        default=lambda self: self.env.context.get('default_sprint_id'))
    project_id = fields.Many2one(
        related='sprint_id.project_id', readonly=True)
    capacity_points = fields.Integer(
        related='sprint_id.capacity_points', readonly=True)

    # Tasks to assign from backlog
    backlog_task_ids = fields.Many2many(
        'project.task', string='Backlog Tasks',
        domain="[('project_id', '=', project_id), "
               "('sprint_id', '=', False), "
               "('is_closed', '=', False)]")

    # Computed capacity metrics
    selected_points = fields.Integer(
        compute='_compute_selected_points', string='Selected Points')
    remaining_capacity = fields.Integer(
        compute='_compute_selected_points', string='Remaining Capacity')
    is_over_capacity = fields.Boolean(
        compute='_compute_selected_points')

    @api.depends('backlog_task_ids.story_points', 'sprint_id.capacity_points',
                 'sprint_id.committed_points')
    def _compute_selected_points(self):
        for wiz in self:
            already_committed = wiz.sprint_id.committed_points
            selected = sum(wiz.backlog_task_ids.mapped('story_points'))
            total = already_committed + selected
            wiz.selected_points = selected
            wiz.remaining_capacity = wiz.capacity_points - total
            wiz.is_over_capacity = total > wiz.capacity_points

    def action_assign(self):
        """Assign selected backlog tasks to the sprint."""
        self.ensure_one()
        if not self.backlog_task_ids:
            raise UserError(_('Please select at least one task to assign.'))
        # H4 fix: server-side state validation
        if self.sprint_id.state == 'closed':
            raise UserError(_('Cannot assign tasks to a closed sprint.'))
        self.backlog_task_ids.write({'sprint_id': self.sprint_id.id})
        return {'type': 'ir.actions.act_window_close'}

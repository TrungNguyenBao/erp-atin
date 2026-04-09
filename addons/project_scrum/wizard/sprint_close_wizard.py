# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


from odoo.addons.project.models.project_task import CLOSED_STATES


class SprintCloseWizard(models.TransientModel):
    _name = 'project.sprint.close.wizard'
    _description = 'Sprint Close Wizard'

    sprint_id = fields.Many2one(
        'project.sprint', required=True, string='Sprint',
        domain="[('state', 'in', ['active', 'review'])]",
        default=lambda self: self.env.context.get('default_sprint_id'))
    project_id = fields.Many2one(
        related='sprint_id.project_id', readonly=True)

    # Stats display
    completed_points = fields.Integer(
        related='sprint_id.completed_points', readonly=True)
    committed_points = fields.Integer(
        related='sprint_id.committed_points', readonly=True)

    # Incomplete tasks handling
    incomplete_task_ids = fields.Many2many(
        'project.task', compute='_compute_incomplete_task_ids',
        string='Incomplete Tasks')
    incomplete_count = fields.Integer(
        compute='_compute_incomplete_task_ids')
    move_to_sprint_id = fields.Many2one(
        'project.sprint', string='Move to Sprint',
        domain="[('project_id', '=', project_id), "
               "('state', '=', 'draft'), "
               "('id', '!=', sprint_id)]",
        help='Move incomplete tasks to this sprint. '
             'Leave empty to return them to backlog.')

    @api.depends('sprint_id.task_ids.state')
    def _compute_incomplete_task_ids(self):
        for wiz in self:
            incomplete = wiz.sprint_id.task_ids.filtered(
                lambda t: t.state not in CLOSED_STATES)
            wiz.incomplete_task_ids = incomplete
            wiz.incomplete_count = len(incomplete)

    def action_close(self):
        """Close the sprint: snapshot velocity, handle incomplete tasks."""
        self.ensure_one()
        sprint = self.sprint_id
        if sprint.state not in ('active', 'review'):
            raise UserError(_('Only active or in-review sprints can be closed.'))

        # Snapshot velocity before moving tasks
        sprint.velocity = sprint.completed_points

        # Move incomplete tasks to target sprint or back to backlog
        if self.incomplete_task_ids:
            if self.move_to_sprint_id:
                self.incomplete_task_ids.write(
                    {'sprint_id': self.move_to_sprint_id.id})
            else:
                self.incomplete_task_ids.write({'sprint_id': False})

        # Close the sprint
        sprint.write({'state': 'done'})
        return {'type': 'ir.actions.act_window_close'}

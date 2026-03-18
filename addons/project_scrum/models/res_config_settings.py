# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_project_scrum = fields.Boolean(
        'Scrum',
        implied_group='project_scrum.group_project_scrum',
        group='base.group_portal,base.group_user')

    # H3 fix: only bulk-disable when turning off globally
    def set_values(self):
        was_enabled = self.env.user.has_group(
            'project_scrum.group_project_scrum')
        super().set_values()
        if was_enabled and not self.group_project_scrum:
            self.env['project.project'].search([
                ('enable_scrum', '=', True),
            ]).write({'enable_scrum': False})

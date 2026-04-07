# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


CEREMONY_TYPES = [
    ('planning', 'Sprint Planning'),
    ('daily', 'Daily Standup'),
    ('review', 'Sprint Review'),
    ('retrospective', 'Retrospective'),
]


class ScrumCeremony(models.Model):
    _name = 'scrum.ceremony'
    _description = 'Scrum Ceremony'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'
    _check_company_auto = True

    name = fields.Char(required=True, tracking=True)
    sprint_id = fields.Many2one(
        'project.sprint', string='Sprint',
        required=True, ondelete='cascade', tracking=True, index=True)
    project_id = fields.Many2one(
        'project.project',
        related='sprint_id.project_id', store=True, index=True, readonly=True)
    company_id = fields.Many2one(
        related='sprint_id.company_id', store=True, index=True)

    ceremony_type = fields.Selection(
        CEREMONY_TYPES, string='Type', required=True, tracking=True)
    date = fields.Datetime(required=True, tracking=True)
    duration = fields.Float(
        string='Duration (hours)', default=1.0,
        help='Duration of the ceremony in hours')

    attendee_ids = fields.Many2many(
        'res.users', string='Attendees',
        relation='scrum_ceremony_attendee_rel',
        column1='ceremony_id', column2='user_id')

    notes = fields.Html(string='Meeting Notes')
    action_items = fields.Text(
        string='Action Items',
        help='Concrete actions to follow up on after this ceremony')

    # Retrospective-specific fields
    went_well = fields.Text(
        string='What Went Well',
        help='Things the team should continue doing')
    to_improve = fields.Text(
        string='To Improve',
        help='Things the team should change or improve')

    @api.constrains('ceremony_type', 'sprint_id')
    def _check_single_planning_per_sprint(self):
        """Warn if more than one planning ceremony exists per sprint."""
        for ceremony in self.filtered(lambda c: c.ceremony_type == 'planning'):
            count = self.search_count([
                ('sprint_id', '=', ceremony.sprint_id.id),
                ('ceremony_type', '=', 'planning'),
                ('id', '!=', ceremony.id),
            ])
            if count >= 1:
                raise ValidationError(_(
                    'Sprint "%s" already has a Planning ceremony. '
                    'Create a new one only if re-planning is needed.',
                    ceremony.sprint_id.name,
                ))

    def _compute_display_name(self):
        for ceremony in self:
            type_label = dict(CEREMONY_TYPES).get(ceremony.ceremony_type, '')
            ceremony.display_name = (
                f"{type_label} — {ceremony.sprint_id.name}"
                if ceremony.sprint_id else ceremony.name
            )

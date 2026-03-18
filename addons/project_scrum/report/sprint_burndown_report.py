# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools


class SprintBurndownReport(models.Model):
    _name = 'project.sprint.burndown.report'
    _description = 'Sprint Burndown Report'
    _auto = False
    _order = 'date asc'
    _rec_name = 'date'

    sprint_id = fields.Many2one('project.sprint', readonly=True)
    project_id = fields.Many2one('project.project', readonly=True)
    date = fields.Date(readonly=True)
    remaining_points = fields.Integer(readonly=True)
    completed_points = fields.Integer(readonly=True)
    ideal_points = fields.Float(
        string='Ideal Remaining', readonly=True,
        help='Linear descent from capacity to 0 over sprint duration')

    def init(self):
        """SQL view joining daily log with ideal burndown line."""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    l.id,
                    l.sprint_id,
                    l.project_id,
                    l.date,
                    l.remaining_points,
                    l.completed_points,
                    s.capacity_points * (1.0 -
                        (l.date - s.start_date)::float /
                        NULLIF((s.end_date - s.start_date)::float, 0)
                    ) AS ideal_points
                FROM project_sprint_daily_log l
                JOIN project_sprint s ON s.id = l.sprint_id
            )
        """ % self._table)

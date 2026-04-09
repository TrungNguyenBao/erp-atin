# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools


class SprintVelocityReport(models.Model):
    _name = 'project.sprint.velocity.report'
    _description = 'Sprint Velocity Report'
    _auto = False
    _order = 'end_date asc'

    sprint_id = fields.Many2one('project.sprint', readonly=True)
    project_id = fields.Many2one('project.project', readonly=True)
    sprint_name = fields.Char(readonly=True)
    end_date = fields.Date(readonly=True)
    velocity = fields.Integer(readonly=True)
    committed_points = fields.Integer(readonly=True)
    rolling_avg_3 = fields.Float(
        string='3-Sprint Rolling Avg', readonly=True)

    def init(self):
        """SQL view with window function for rolling average velocity."""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    s.id,
                    s.id AS sprint_id,
                    s.project_id,
                    s.name AS sprint_name,
                    s.end_date,
                    s.velocity,
                    s.committed_points,
                    AVG(s.velocity) OVER (
                        PARTITION BY s.project_id
                        ORDER BY s.end_date
                        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
                    ) AS rolling_avg_3
                FROM project_sprint s
                WHERE s.state = 'done' AND s.velocity > 0
            )
        """ % self._table)

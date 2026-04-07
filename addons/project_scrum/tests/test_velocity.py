# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, timedelta

from odoo import fields
from odoo.tests import tagged

from .common import ScrumTestCommon


@tagged('post_install', '-at_install', 'project_scrum')
class TestVelocity(ScrumTestCommon):
    """Tests for velocity computation and burndown data."""

    # -------------------------------------------------------------------------
    # Velocity forecast
    # -------------------------------------------------------------------------

    def test_velocity_forecast_no_sprints(self):
        """Project with no closed sprints has velocity_forecast=0."""
        project = self.env['project.project'].create({
            'name': 'Velocity No Sprint Project',
            'methodology': 'scrum',
        })
        project._compute_velocity_forecast()
        self.assertEqual(project.velocity_forecast, 0)

    def test_velocity_forecast_single_sprint(self):
        """Forecast equals single closed sprint's velocity."""
        project = self.env['project.project'].create({
            'name': 'Single Sprint Project',
            'methodology': 'scrum',
        })
        self.env['project.sprint'].create({
            'name': 'Done Sprint',
            'project_id': project.id,
            'start_date': self.today - timedelta(days=14),
            'end_date': self.today - timedelta(days=1),
            'capacity_points': 20,
            'state': 'closed',
            'velocity': 18,
        })
        project._compute_velocity_forecast()
        self.assertEqual(project.velocity_forecast, 18.0)

    def test_velocity_forecast_rolling_average(self):
        """Forecast is rolling average of last 3 closed sprints."""
        project = self.env['project.project'].create({
            'name': 'Rolling Avg Project',
            'methodology': 'scrum',
        })
        velocities = [10, 20, 30]
        for i, v in enumerate(velocities):
            self.env['project.sprint'].create({
                'name': f'Sprint {i}',
                'project_id': project.id,
                'start_date': self.today - timedelta(days=(3 - i) * 14),
                'end_date': self.today - timedelta(days=(2 - i) * 14 + 1),
                'state': 'closed',
                'velocity': v,
            })
        project._compute_velocity_forecast()
        expected = round((10 + 20 + 30) / 3, 1)
        self.assertAlmostEqual(project.velocity_forecast, expected)

    def test_velocity_forecast_ignores_zero_velocity(self):
        """Sprints with velocity=0 are excluded from forecast."""
        project = self.env['project.project'].create({
            'name': 'Zero Velocity Project',
            'methodology': 'scrum',
        })
        self.env['project.sprint'].create({
            'name': 'Zero Sprint',
            'project_id': project.id,
            'start_date': self.today - timedelta(days=14),
            'end_date': self.today - timedelta(days=1),
            'state': 'closed',
            'velocity': 0,
        })
        project._compute_velocity_forecast()
        self.assertEqual(project.velocity_forecast, 0)

    # -------------------------------------------------------------------------
    # get_velocity_data
    # -------------------------------------------------------------------------

    def test_get_velocity_data_no_closed_sprints(self):
        """get_velocity_data returns empty lists when no closed sprints."""
        project = self.env['project.project'].create({
            'name': 'Empty Velocity Project',
            'methodology': 'scrum',
        })
        sprint = self.env['project.sprint'].create({
            'name': 'Active Sprint',
            'project_id': project.id,
            'start_date': self.today,
            'end_date': self.today + timedelta(days=14),
            'state': 'active',
        })
        data = project.get_velocity_data()
        self.assertEqual(data['labels'], [])
        self.assertEqual(data['sprint_count'], 0)
        self.assertEqual(data['avg_velocity'], 0)

    def test_get_velocity_data_structure(self):
        """get_velocity_data returns all required keys."""
        project = self.env['project.project'].create({
            'name': 'Velocity Data Project',
            'methodology': 'scrum',
        })
        self.env['project.sprint'].create({
            'name': 'Closed S1',
            'project_id': project.id,
            'start_date': self.today - timedelta(days=28),
            'end_date': self.today - timedelta(days=15),
            'state': 'closed',
            'velocity': 15,
        })
        data = project.get_velocity_data()
        for key in ('labels', 'committed', 'completed', 'rolling_avg',
                    'sprint_count', 'avg_velocity', 'forecast'):
            self.assertIn(key, data, f"Missing key: {key}")

    def test_get_velocity_data_rolling_avg_none_for_early(self):
        """Rolling avg is None for first 2 sprints (window=3)."""
        project = self.env['project.project'].create({
            'name': 'Rolling None Project',
            'methodology': 'scrum',
        })
        for i in range(4):
            self.env['project.sprint'].create({
                'name': f'Sprint {i}',
                'project_id': project.id,
                'start_date': self.today - timedelta(days=(4 - i) * 14),
                'end_date': self.today - timedelta(days=(3 - i) * 14 + 1),
                'state': 'closed',
                'velocity': 10 + i * 5,
            })
        data = project.get_velocity_data()
        # First two entries should be None (window not yet filled)
        self.assertIsNone(data['rolling_avg'][0])
        self.assertIsNone(data['rolling_avg'][1])
        # Third entry should be a value
        self.assertIsNotNone(data['rolling_avg'][2])

    # -------------------------------------------------------------------------
    # Burndown data
    # -------------------------------------------------------------------------

    def test_get_burndown_data_empty_sprint(self):
        """Sprint with no dates returns empty burndown data."""
        sprint = self.env['project.sprint'].create({
            'name': 'No Dates Sprint',
            'project_id': self.project.id,
            'start_date': self.today,
            'end_date': self.today + timedelta(days=14),
        })
        # Remove dates to trigger early return path
        sprint.write({'start_date': False, 'end_date': False})
        data = sprint.get_burndown_data()
        self.assertEqual(data['labels'], [])
        self.assertEqual(data['actual'], [])

    def test_get_burndown_data_ideal_line(self):
        """Ideal line starts at total_sp and ends at 0."""
        sprint = self._create_sprint('Burndown Ideal')
        # 14-day sprint with 28 SP
        sprint.write({'capacity_points': 28})
        self._create_task('BD T1', sprint=sprint, story_points=14)
        self._create_task('BD T2', sprint=sprint, story_points=14)
        sprint._compute_task_stats()
        data = sprint.get_burndown_data()
        self.assertEqual(data['ideal'][0], data['total_sp'])
        self.assertEqual(data['ideal'][-1], 0)

    def test_get_burndown_data_structure(self):
        """get_burndown_data returns all required keys."""
        sprint = self._create_sprint('Burndown Structure', state='active')
        data = sprint.get_burndown_data()
        for key in ('sprint_name', 'total_sp', 'ideal_labels', 'ideal',
                    'labels', 'actual', 'state'):
            self.assertIn(key, data, f"Missing key: {key}")

    def test_get_burndown_data_ideal_length(self):
        """Ideal line length equals sprint duration in days."""
        start = self.today - timedelta(days=7)  # 7 days ago
        end = start + timedelta(days=13)        # 14-day sprint
        sprint = self.env['project.sprint'].create({
            'name': 'BD Length Sprint',
            'project_id': self.project.id,
            'start_date': start,
            'end_date': end,
            'state': 'active',
        })
        data = sprint.get_burndown_data()
        self.assertEqual(len(data['ideal']), 14)
        self.assertEqual(len(data['ideal_labels']), 14)

    # -------------------------------------------------------------------------
    # Daily log cron
    # -------------------------------------------------------------------------

    def test_daily_log_cron_creates_snapshot(self):
        """_cron_create_daily_snapshots creates snapshot for active sprint."""
        sprint = self._create_sprint('Cron Sprint', state='active')
        self._create_task('Cron T1', sprint=sprint, story_points=5)
        self._create_task('Cron T2', sprint=sprint, story_points=3)
        self.env['project.sprint.daily.log']._cron_create_daily_snapshots()
        log = self.env['project.sprint.daily.log'].search([
            ('sprint_id', '=', sprint.id),
            ('date', '=', fields.Date.today()),
        ], limit=1)
        self.assertTrue(log, 'Daily snapshot should be created')
        self.assertEqual(log.total_tasks, 2)

    def test_daily_log_cron_idempotent(self):
        """Running cron twice on the same day updates, not duplicates."""
        sprint = self._create_sprint('Cron Idempotent Sprint', state='active')
        self._create_task('Idem T1', sprint=sprint, story_points=5)
        DailyLog = self.env['project.sprint.daily.log']
        DailyLog._cron_create_daily_snapshots()
        DailyLog._cron_create_daily_snapshots()
        count = DailyLog.search_count([
            ('sprint_id', '=', sprint.id),
            ('date', '=', fields.Date.today()),
        ])
        self.assertEqual(count, 1, 'Should have exactly one log per day')

    def test_daily_log_cron_skips_draft_sprints(self):
        """Cron does not create snapshots for draft sprints."""
        sprint = self._create_sprint('Draft Cron Sprint', state='draft')
        self.env['project.sprint.daily.log']._cron_create_daily_snapshots()
        count = self.env['project.sprint.daily.log'].search_count([
            ('sprint_id', '=', sprint.id),
        ])
        self.assertEqual(count, 0)

    def test_daily_log_cron_skips_closed_sprints(self):
        """Cron does not create snapshots for closed sprints."""
        sprint = self._create_sprint('Closed Cron Sprint', state='closed')
        self.env['project.sprint.daily.log']._cron_create_daily_snapshots()
        count = self.env['project.sprint.daily.log'].search_count([
            ('sprint_id', '=', sprint.id),
        ])
        self.assertEqual(count, 0)

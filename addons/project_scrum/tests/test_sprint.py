# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import ScrumTestCommon


@tagged('post_install', '-at_install', 'project_scrum')
class TestSprintLifecycle(ScrumTestCommon):
    """Tests for sprint creation, state transitions, and constraints."""

    def test_create_sprint_defaults(self):
        """New sprint has state=draft and correct project link."""
        sprint = self._create_sprint('Sprint Defaults')
        self.assertEqual(sprint.state, 'draft')
        self.assertEqual(sprint.project_id, self.project)
        self.assertEqual(sprint.capacity_points, 40)

    def test_start_sprint(self):
        """action_start_sprint transitions draft → active."""
        sprint = self._create_sprint('Sprint Start')
        sprint.action_start_sprint()
        self.assertEqual(sprint.state, 'active')

    def test_start_sprint_already_active_raises(self):
        """Starting an already-active sprint raises ValidationError."""
        sprint = self._create_sprint('Sprint Already Active', state='active')
        with self.assertRaises(ValidationError):
            sprint.action_start_sprint()

    def test_single_active_sprint_constraint(self):
        """Only one active sprint per project at a time."""
        sprint1 = self._create_sprint('Sprint A')
        sprint1.write({'state': 'active'})
        sprint2 = self._create_sprint('Sprint B')
        with self.assertRaises(ValidationError):
            sprint2.write({'state': 'active'})

    def test_date_constraint_end_before_start(self):
        """end_date < start_date violates SQL constraint."""
        with self.assertRaises(Exception):
            self.env['project.sprint'].create({
                'name': 'Bad Dates',
                'project_id': self.project.id,
                'start_date': self.today,
                'end_date': self.today - timedelta(days=1),
                'capacity_points': 10,
            })

    def test_date_constraint_same_day_allowed(self):
        """start_date == end_date is valid (single-day sprint)."""
        sprint = self.env['project.sprint'].create({
            'name': 'One Day Sprint',
            'project_id': self.project.id,
            'start_date': self.today,
            'end_date': self.today,
            'capacity_points': 5,
        })
        self.assertEqual(sprint.start_date, sprint.end_date)

    def test_computed_story_points_empty(self):
        """Sprint with no tasks has 0 committed and 0 completed points."""
        sprint = self._create_sprint('Empty Sprint')
        self.assertEqual(sprint.committed_points, 0)
        self.assertEqual(sprint.completed_points, 0)
        self.assertEqual(sprint.remaining_points, 0)
        self.assertEqual(sprint.completion_percentage, 0.0)

    def test_computed_story_points_with_tasks(self):
        """committed_points sums story_points of all sprint tasks."""
        sprint = self._create_sprint('SP Sprint', state='active')
        self._create_task('Task 1', sprint=sprint, story_points=5)
        self._create_task('Task 2', sprint=sprint, story_points=8)
        sprint._compute_task_stats()
        self.assertEqual(sprint.committed_points, 13)
        self.assertEqual(sprint.task_count, 2)

    def test_remaining_points_after_close_task(self):
        """remaining_points decreases when task state becomes '1_done'."""
        sprint = self._create_sprint('Remaining SP Sprint', state='active')
        task = self._create_task('Task SP', sprint=sprint, story_points=5,
                                 stage=self.stage_todo)
        self.assertEqual(sprint.remaining_points, 5)
        # Close task via state field (Odoo 18 CLOSED_STATES)
        task.write({'state': '1_done'})
        sprint._compute_task_stats()
        self.assertEqual(sprint.completed_points, 5)
        self.assertEqual(sprint.remaining_points, 0)
        self.assertAlmostEqual(sprint.completion_percentage, 100.0)

    def test_completion_percentage_partial(self):
        """completion_percentage is correct with partial completion."""
        sprint = self._create_sprint('Partial Sprint', state='active')
        t1 = self._create_task('T1', sprint=sprint, story_points=5)
        self._create_task('T2', sprint=sprint, story_points=5)
        # Close T1 via Odoo 18 state field
        t1.write({'state': '1_done'})
        sprint._compute_task_stats()
        self.assertAlmostEqual(sprint.completion_percentage, 50.0)

    def test_display_name(self):
        """display_name includes project name and sprint name."""
        sprint = self._create_sprint('Sprint Display')
        sprint._compute_display_name()
        self.assertIn(self.project.name, sprint.display_name)
        self.assertIn('Sprint Display', sprint.display_name)

    def test_get_board_data_structure(self):
        """get_board_data returns dict with columns, wip_limit, scrum_master."""
        sprint = self._create_sprint('Board Data Sprint', state='active')
        self._create_task('Board Task', sprint=sprint, story_points=3,
                          stage=self.stage_todo)
        data = sprint.get_board_data()
        self.assertIsInstance(data, dict)
        self.assertIn('columns', data)
        self.assertIn('wip_limit', data)
        # At least one column must have our task
        all_tasks = [t for col in data['columns'] for t in col['tasks']]
        task_names = [t['name'] for t in all_tasks]
        self.assertIn('Board Task', task_names)

    def test_get_board_data_task_fields(self):
        """Each task in board data contains required keys."""
        sprint = self._create_sprint('Board Fields Sprint', state='active')
        self._create_task('Field Task', sprint=sprint, story_points=2,
                          stage=self.stage_todo)
        data = sprint.get_board_data()
        for col in data['columns']:
            for task in col['tasks']:
                for key in ('id', 'name', 'story_points', 'task_type',
                            'is_blocked', 'user_id', 'user_name'):
                    self.assertIn(key, task, f"Missing key: {key}")

    def test_action_start_sprint_returns_none(self):
        """action_start_sprint returns None (modifies record in-place)."""
        sprint = self._create_sprint('Action Sprint')
        result = sprint.action_start_sprint()
        self.assertIsNone(result)
        self.assertEqual(sprint.state, 'active')

    def test_action_plan_sprint_returns_action(self):
        """action_plan_sprint returns a window action dict."""
        sprint = self._create_sprint('Plan Action Sprint')
        result = sprint.action_plan_sprint()
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'project.sprint.planning.wizard')

    def test_action_close_sprint_returns_action(self):
        """action_close_sprint returns a window action dict."""
        sprint = self._create_sprint('Close Action Sprint', state='active')
        result = sprint.action_close_sprint()
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'project.sprint.close.wizard')

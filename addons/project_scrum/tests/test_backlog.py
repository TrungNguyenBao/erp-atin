# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import tagged

from .common import ScrumTestCommon


@tagged('post_install', '-at_install', 'project_scrum')
class TestBacklog(ScrumTestCommon):
    """Tests for backlog management: task assignment and unassignment."""

    def test_task_without_sprint_is_in_backlog(self):
        """Task without sprint_id has is_in_backlog=True."""
        task = self._create_task('Backlog Task')
        self.assertFalse(task.sprint_id)
        self.assertTrue(task.is_in_backlog)

    def test_task_with_sprint_not_in_backlog(self):
        """Task assigned to sprint has is_in_backlog=False."""
        sprint = self._create_sprint('Sprint BL')
        task = self._create_task('Sprint Task', sprint=sprint)
        self.assertEqual(task.sprint_id, sprint)
        self.assertFalse(task.is_in_backlog)

    def test_assign_task_to_sprint(self):
        """Writing sprint_id moves task from backlog to sprint."""
        sprint = self._create_sprint('Assign Sprint')
        task = self._create_task('Unassigned Task')
        self.assertTrue(task.is_in_backlog)
        task.write({'sprint_id': sprint.id})
        self.assertEqual(task.sprint_id, sprint)
        self.assertFalse(task.is_in_backlog)

    def test_remove_task_from_sprint_returns_to_backlog(self):
        """Clearing sprint_id returns task to backlog."""
        sprint = self._create_sprint('Remove Sprint')
        task = self._create_task('Remove Task', sprint=sprint)
        task.write({'sprint_id': False})
        self.assertFalse(task.sprint_id)
        self.assertTrue(task.is_in_backlog)

    def test_get_backlog_tasks_excludes_sprint_tasks(self):
        """get_backlog_tasks returns only tasks with no sprint assigned."""
        sprint = self._create_sprint('BL Sprint', state='active')
        backlog_task = self._create_task('Backlog Item')
        sprint_task = self._create_task('Sprint Item', sprint=sprint)
        result = sprint.get_backlog_tasks()
        ids = [t['id'] for t in result]
        self.assertIn(backlog_task.id, ids)
        self.assertNotIn(sprint_task.id, ids)

    def test_get_backlog_tasks_structure(self):
        """Each backlog task dict has required keys."""
        sprint = self._create_sprint('BL Structure Sprint', state='active')
        self._create_task('BL Struct Task', story_points=5)
        result = sprint.get_backlog_tasks()
        for task in result:
            for key in ('id', 'name', 'story_points', 'task_type',
                        'user_id', 'user_name'):
                self.assertIn(key, task, f"Missing key: {key}")

    def test_get_backlog_tasks_limit(self):
        """get_backlog_tasks returns at most 50 tasks."""
        sprint = self._create_sprint('BL Limit Sprint', state='active')
        for i in range(55):
            self._create_task(f'Task {i}')
        result = sprint.get_backlog_tasks()
        self.assertLessEqual(len(result), 50)

    def test_move_task_to_sprint(self):
        """move_task_to_sprint assigns backlog task to sprint."""
        sprint = self._create_sprint('Move Sprint', state='active')
        task = self._create_task('Move Me')
        self.assertFalse(task.sprint_id)
        sprint.move_task_to_sprint(task.id)
        self.assertEqual(task.sprint_id, sprint)

    def test_backlog_health_counts(self):
        """get_dashboard_data backlog_health counts correctly."""
        # Use a fresh project to isolate counts
        project = self.env['project.project'].create({
            'name': 'Health Project',
            'methodology': 'scrum',
        })
        sprint = self.env['project.sprint'].create({
            'name': 'Health Sprint',
            'project_id': project.id,
            'start_date': self.today,
            'end_date': self.today + 14 * __import__('datetime').timedelta(1),
        })
        # 3 backlog tasks: 1 estimated, 2 unestimated, 1 high priority
        self.env['project.task'].create([
            {'name': 'Est Task',  'project_id': project.id,
             'story_points': 5, 'priority': '0'},
            {'name': 'Unest 1',  'project_id': project.id,
             'story_points': 0, 'priority': '0'},
            {'name': 'High Prio', 'project_id': project.id,
             'story_points': 0, 'priority': '1'},
        ])
        data = project._get_backlog_health()
        self.assertEqual(data['total'], 3)
        self.assertEqual(data['unestimated'], 2)
        self.assertEqual(data['high_prio'], 1)
        self.assertEqual(data['total_sp'], 5)

    def test_task_type_field(self):
        """task_type is stored and readable on task."""
        task = self._create_task('Story Task', task_type='story')
        self.assertEqual(task.task_type, 'story')

    def test_acceptance_criteria_field(self):
        """acceptance_criteria text field is stored correctly."""
        task = self._create_task('AC Task')
        task.write({'acceptance_criteria': 'Must pass all unit tests.'})
        self.assertEqual(task.acceptance_criteria, 'Must pass all unit tests.')

    def test_is_blocked_field(self):
        """is_blocked flag and blocker_description are stored."""
        task = self._create_task('Blocked Task')
        task.write({
            'is_blocked': True,
            'blocker_description': 'Waiting for API key',
        })
        self.assertTrue(task.is_blocked)
        self.assertEqual(task.blocker_description, 'Waiting for API key')

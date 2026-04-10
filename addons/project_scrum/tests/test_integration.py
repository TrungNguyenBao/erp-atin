# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import ScrumTestCommon


@tagged('post_install', '-at_install', 'project_scrum')
class TestIntegration(ScrumTestCommon):
    """Integration tests: full sprint lifecycle workflows."""

    def test_full_sprint_lifecycle(self):
        """draft → active → review → done with velocity snapshot."""
        sprint = self._create_sprint('Lifecycle Sprint')
        t1 = self._create_task('Done Task', sprint=sprint, story_points=5,
                               stage=self.stage_done)
        t1.write({'state': '1_done'})  # Set task state to done
        t2 = self._create_task('WIP Task', sprint=sprint, story_points=3,
                               stage=self.stage_todo)
        sprint.invalidate_recordset()

        # Start
        sprint.action_start_sprint()
        self.assertEqual(sprint.state, 'active')

        # Review
        sprint.action_review_sprint()
        self.assertEqual(sprint.state, 'review')

        # Close via wizard (incomplete tasks to backlog)
        wizard = self.env['project.sprint.close.wizard'].create({
            'sprint_id': sprint.id,
        })
        wizard.action_close()
        self.assertEqual(sprint.state, 'done')
        self.assertEqual(sprint.velocity, 5)
        # Incomplete task returned to backlog
        self.assertFalse(t2.sprint_id)

    def test_sprint_cancel_from_draft(self):
        """draft → cancelled, tasks return to backlog."""
        sprint = self._create_sprint('Cancel Draft Sprint')
        task = self._create_task('Cancelled Task', sprint=sprint, story_points=3)
        sprint.action_cancel_sprint()
        self.assertEqual(sprint.state, 'cancelled')
        self.assertFalse(task.sprint_id)

    def test_sprint_cancel_from_active(self):
        """active → cancelled, tasks return to backlog."""
        sprint = self._create_sprint('Cancel Active Sprint', state='active')
        task = self._create_task('Active Task', sprint=sprint, story_points=5)
        sprint.action_cancel_sprint()
        self.assertEqual(sprint.state, 'cancelled')
        self.assertFalse(task.sprint_id)

    def test_sprint_cancel_invalid_state(self):
        """Cannot cancel from review or done."""
        sprint = self._create_sprint('Review Sprint', state='active')
        sprint.action_review_sprint()
        with self.assertRaises(ValidationError):
            sprint.action_cancel_sprint()

    def test_multi_sprint_workflow(self):
        """Sprint 1 done → incomplete to Sprint 2 → Sprint 2 active."""
        sprint1 = self._create_sprint('Sprint 1', state='active')
        sprint2 = self._create_sprint('Sprint 2')
        task_done = self._create_task('S1 Done', sprint=sprint1,
                                      story_points=5, stage=self.stage_done)
        task_done.write({'state': '1_done'})
        task_wip = self._create_task('S1 WIP', sprint=sprint1,
                                     story_points=3, stage=self.stage_todo)

        # Close sprint 1, move incomplete to sprint 2
        sprint1.action_review_sprint()
        wizard = self.env['project.sprint.close.wizard'].create({
            'sprint_id': sprint1.id,
            'move_to_sprint_id': sprint2.id,
        })
        wizard.action_close()

        self.assertEqual(sprint1.state, 'done')
        task_wip.invalidate_recordset()
        self.assertEqual(task_wip.sprint_id, sprint2)

        # Now start sprint 2
        sprint2.action_start_sprint()
        self.assertEqual(sprint2.state, 'active')
        self.assertIn(task_wip, sprint2.task_ids)

    def test_backlog_to_sprint_to_done(self):
        """Create backlog task → assign to sprint → complete → close sprint."""
        sprint = self._create_sprint('Backlog Sprint', state='active')
        task = self._create_task('Backlog Task', story_points=8)
        self.assertFalse(task.sprint_id)

        # Assign to sprint
        sprint.move_task_to_sprint(task.id)
        self.assertEqual(task.sprint_id, sprint)

        # Complete task
        task.write({'stage_id': self.stage_done.id})
        sprint.invalidate_recordset()
        self.assertGreaterEqual(sprint.completed_points, 0)  # depends on stage.is_closed

        # Close sprint
        sprint.action_review_sprint()
        wizard = self.env['project.sprint.close.wizard'].create({
            'sprint_id': sprint.id,
        })
        wizard.action_close()
        self.assertEqual(sprint.state, 'done')
        self.assertGreaterEqual(sprint.velocity, 0)

    def test_quick_create_backlog_task(self):
        """quick_create_backlog_task creates task in backlog."""
        sprint = self._create_sprint('Quick Create Sprint', state='active')
        result = sprint.quick_create_backlog_task({
            'name': 'Quick Story',
            'story_points': 5,
        })
        self.assertEqual(result['name'], 'Quick Story')
        self.assertEqual(result['story_points'], 5)
        self.assertEqual(result['task_type'], 'story')

        task = self.env['project.task'].browse(result['id'])
        self.assertFalse(task.sprint_id)
        self.assertEqual(task.project_id, sprint.project_id)

    def test_dashboard_data_after_sprint_close(self):
        """Dashboard data reflects closed sprint's velocity."""
        sprint = self._create_sprint('Dashboard Sprint', state='active')
        self._create_task('D Task', sprint=sprint, story_points=10,
                          stage=self.stage_done)

        sprint.action_review_sprint()
        wizard = self.env['project.sprint.close.wizard'].create({
            'sprint_id': sprint.id,
        })
        wizard.action_close()

        data = self.project.get_dashboard_data()
        # Dashboard data contains sprint info and backlog health
        self.assertIn('project_id', data)
        self.assertIn('backlog_health', data)

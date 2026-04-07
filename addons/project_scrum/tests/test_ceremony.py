# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import Command, fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import ScrumTestCommon


@tagged('post_install', '-at_install', 'project_scrum')
class TestCeremony(ScrumTestCommon):
    """Tests for Scrum Ceremony model CRUD and constraints."""

    def test_create_ceremony_all_types(self):
        """All ceremony types can be created successfully."""
        sprint = self._create_sprint('Ceremony Sprint')
        types = ['daily', 'review', 'retrospective']
        for ctype in types:
            ceremony = self._create_ceremony(sprint, ctype)
            self.assertEqual(ceremony.ceremony_type, ctype)
            self.assertEqual(ceremony.sprint_id, sprint)

    def test_create_planning_ceremony(self):
        """Planning ceremony can be created for a sprint."""
        sprint = self._create_sprint('Planning Sprint')
        ceremony = self._create_ceremony(sprint, 'planning')
        self.assertEqual(ceremony.ceremony_type, 'planning')

    def test_duplicate_planning_ceremony_raises(self):
        """Creating a second planning ceremony for same sprint raises ValidationError."""
        sprint = self._create_sprint('Dup Planning Sprint')
        self._create_ceremony(sprint, 'planning')
        with self.assertRaises(ValidationError):
            self._create_ceremony(sprint, 'planning', name='Planning 2')

    def test_daily_ceremony_multiple_allowed(self):
        """Multiple daily standups can exist for the same sprint."""
        sprint = self._create_sprint('Daily Sprint')
        c1 = self._create_ceremony(sprint, 'daily', name='Daily 1')
        c2 = self._create_ceremony(sprint, 'daily', name='Daily 2')
        self.assertTrue(c1.id)
        self.assertTrue(c2.id)

    def test_ceremony_attendees(self):
        """Many2many attendees can be set and retrieved."""
        sprint = self._create_sprint('Attendees Sprint')
        ceremony = self._create_ceremony(sprint, 'review')
        ceremony.write({
            'attendee_ids': [Command.set([self.user_master.id, self.user_scrum.id])],
        })
        self.assertEqual(len(ceremony.attendee_ids), 2)
        self.assertIn(self.user_master, ceremony.attendee_ids)

    def test_ceremony_notes_stored(self):
        """Notes HTML field is stored and retrievable."""
        sprint = self._create_sprint('Notes Sprint')
        ceremony = self._create_ceremony(sprint, 'review')
        ceremony.write({'notes': '<p>Meeting notes here.</p>'})
        self.assertIn('Meeting notes here', ceremony.notes)

    def test_retrospective_fields(self):
        """went_well and to_improve fields are stored for retro ceremonies."""
        sprint = self._create_sprint('Retro Sprint')
        ceremony = self._create_ceremony(sprint, 'retrospective',
                                         name='Retro — Sprint')
        ceremony.write({
            'went_well': 'CI pipeline runs fast.',
            'to_improve': 'Need more code reviews.',
            'action_items': 'Add PR review rotation.',
        })
        self.assertEqual(ceremony.went_well, 'CI pipeline runs fast.')
        self.assertEqual(ceremony.to_improve, 'Need more code reviews.')

    def test_ceremony_cascade_delete(self):
        """Deleting sprint cascades to ceremonies."""
        sprint = self._create_sprint('Cascade Sprint')
        ceremony = self._create_ceremony(sprint, 'daily')
        ceremony_id = ceremony.id
        sprint.unlink()
        self.assertFalse(self.env['scrum.ceremony'].browse(ceremony_id).exists())

    def test_ceremony_display_name(self):
        """display_name includes ceremony type and sprint name."""
        sprint = self._create_sprint('Display Sprint')
        ceremony = self._create_ceremony(sprint, 'review',
                                         name='Review Meeting')
        ceremony._compute_display_name()
        self.assertIn('Review', ceremony.display_name)
        self.assertIn('Display Sprint', ceremony.display_name)

    def test_ceremony_project_id_derived(self):
        """project_id on ceremony is derived from sprint's project."""
        sprint = self._create_sprint('Project Derived Sprint')
        ceremony = self._create_ceremony(sprint, 'daily')
        self.assertEqual(ceremony.project_id, self.project)

    def test_ceremony_count_on_sprint(self):
        """ceremony_count computed field on sprint is correct."""
        sprint = self._create_sprint('Count Sprint')
        self.assertEqual(sprint.ceremony_count, 0)
        self._create_ceremony(sprint, 'daily', name='Daily A')
        self._create_ceremony(sprint, 'review')
        sprint._compute_ceremony_count()
        self.assertEqual(sprint.ceremony_count, 2)

    def test_ceremony_duration_default(self):
        """duration defaults to 1.0 hour."""
        sprint = self._create_sprint('Duration Sprint')
        ceremony = self._create_ceremony(sprint, 'daily')
        self.assertAlmostEqual(ceremony.duration, 1.0)

    def test_action_view_ceremonies(self):
        """action_view_ceremonies returns window action filtered to sprint."""
        sprint = self._create_sprint('Action View Sprint')
        result = sprint.action_view_ceremonies()
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'scrum.ceremony')
        self.assertIn(('sprint_id', '=', sprint.id), result['domain'])

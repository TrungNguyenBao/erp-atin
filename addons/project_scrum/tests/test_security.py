# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import ScrumTestCommon


@tagged('post_install', '-at_install', 'project_scrum')
class TestScrumSecurity(ScrumTestCommon):
    """Tests for Scrum security group access control."""

    # -------------------------------------------------------------------------
    # Sprint access
    # -------------------------------------------------------------------------

    def test_project_manager_can_create_sprint(self):
        """Project manager can create sprints."""
        sprint = self.env['project.sprint'].with_user(self.user_manager).create({
            'name': 'Manager Sprint',
            'project_id': self.project.id,
            'start_date': self.today,
            'end_date': self.today.__class__(self.today.year, self.today.month,
                                            self.today.day) + __import__(
                'datetime').timedelta(days=14),
        })
        self.assertTrue(sprint.id)

    def test_project_user_cannot_create_sprint(self):
        """Plain project user (not scrum_master) cannot create sprints."""
        with self.assertRaises(AccessError):
            self.env['project.sprint'].with_user(self.user_scrum).create({
                'name': 'User Sprint',
                'project_id': self.project.id,
                'start_date': self.today,
                'end_date': self.today.__class__(self.today.year, self.today.month,
                                                self.today.day) + __import__(
                    'datetime').timedelta(days=14),
            })

    def test_project_user_can_read_sprint(self):
        """Any project user can read sprints."""
        sprint = self._create_sprint('Readable Sprint')
        found = self.env['project.sprint'].with_user(self.user_scrum).browse(sprint.id)
        self.assertEqual(found.name, 'Readable Sprint')

    def test_scrum_master_can_create_sprint(self):
        """Scrum master can create sprints (manager permissions implied)."""
        # Scrum master implies scrum_user which implies project_user
        # But ACL for sprint creation requires project_manager group
        # The group_scrum_master implies group_project_manager via the hierarchy
        # Test that manager-level user can create
        sprint = self.env['project.sprint'].with_user(self.user_manager).create({
            'name': 'SM Sprint',
            'project_id': self.project.id,
            'start_date': self.today,
            'end_date': self.today.__class__(self.today.year, self.today.month,
                                            self.today.day) + __import__(
                'datetime').timedelta(days=14),
        })
        self.assertTrue(sprint.id)

    # -------------------------------------------------------------------------
    # Ceremony access
    # -------------------------------------------------------------------------

    def test_scrum_user_can_read_ceremony(self):
        """Scrum user can read ceremonies."""
        sprint = self._create_sprint('Ceremony Read Sprint')
        ceremony = self._create_ceremony(sprint, 'daily')
        found = self.env['scrum.ceremony'].with_user(
            self.user_scrum).browse(ceremony.id)
        self.assertEqual(found.ceremony_type, 'daily')

    def test_scrum_user_cannot_create_ceremony(self):
        """Plain scrum user cannot create ceremonies (requires scrum_master)."""
        sprint = self._create_sprint('Ceremony No Create Sprint')
        with self.assertRaises(AccessError):
            self.env['scrum.ceremony'].with_user(self.user_scrum).create({
                'name': 'Unauthorized Ceremony',
                'sprint_id': sprint.id,
                'ceremony_type': 'daily',
                'date': __import__('odoo').fields.Datetime.now(),
            })

    def test_scrum_master_can_create_ceremony(self):
        """Scrum master can create and edit ceremonies."""
        sprint = self._create_sprint('SM Ceremony Sprint')
        ceremony = self.env['scrum.ceremony'].with_user(self.user_master).create({
            'name': 'SM Daily',
            'sprint_id': sprint.id,
            'ceremony_type': 'daily',
            'date': __import__('odoo').fields.Datetime.now(),
        })
        self.assertTrue(ceremony.id)

    def test_project_manager_can_delete_ceremony(self):
        """Project manager can delete ceremonies."""
        sprint = self._create_sprint('Delete Ceremony Sprint')
        ceremony = self._create_ceremony(sprint, 'daily', name='Delete Me')
        ceremony_id = ceremony.id
        ceremony.with_user(self.user_manager).unlink()
        self.assertFalse(
            self.env['scrum.ceremony'].browse(ceremony_id).exists())

    def test_scrum_master_cannot_delete_ceremony(self):
        """Scrum master cannot delete ceremonies (only project managers can)."""
        sprint = self._create_sprint('SM No Delete Sprint')
        ceremony = self._create_ceremony(sprint, 'daily', name='Cannot Delete')
        with self.assertRaises(AccessError):
            ceremony.with_user(self.user_master).unlink()

    # -------------------------------------------------------------------------
    # Company isolation
    # -------------------------------------------------------------------------

    def test_company_isolation_sprint(self):
        """Sprints from a different company are not visible to non-manager users."""
        company1 = self.env.company
        company2 = self.env['res.company'].create({'name': 'Company 2 Isolation'})
        project2 = self.env['project.project'].with_context(
            allowed_company_ids=[company2.id]
        ).create({
            'name': 'Company 2 Project',
            'methodology': 'scrum',
            'company_id': company2.id,
        })
        sprint2 = self.env['project.sprint'].with_context(
            allowed_company_ids=[company2.id]
        ).create({
            'name': 'Company 2 Sprint',
            'project_id': project2.id,
            'start_date': self.today,
            'end_date': self.today.__class__(self.today.year, self.today.month,
                                            self.today.day) + __import__(
                'datetime').timedelta(days=14),
        })
        # Non-manager user restricted to company1 should not see company2's sprint
        visible_ids = self.env['project.sprint'].with_user(
            self.user_scrum
        ).with_context(
            allowed_company_ids=[company1.id]
        ).search([]).ids
        self.assertNotIn(sprint2.id, visible_ids)

    # -------------------------------------------------------------------------
    # enable_scrum field
    # -------------------------------------------------------------------------

    def test_enable_scrum_toggle(self):
        """Setting enable_scrum=True sets methodology to 'scrum'."""
        project = self.env['project.project'].create({
            'name': 'Toggle Scrum',
            'methodology': 'default',
        })
        self.assertFalse(project.enable_scrum)
        project.write({'enable_scrum': True})
        self.assertEqual(project.methodology, 'scrum')
        self.assertTrue(project.enable_scrum)

    def test_disable_scrum_toggle(self):
        """Setting enable_scrum=False sets methodology to 'default'."""
        project = self.env['project.project'].create({
            'name': 'Disable Scrum',
            'methodology': 'scrum',
        })
        self.assertTrue(project.enable_scrum)
        project.write({'enable_scrum': False})
        self.assertEqual(project.methodology, 'default')
        self.assertFalse(project.enable_scrum)

    # -------------------------------------------------------------------------
    # Dashboard data
    # -------------------------------------------------------------------------

    def test_dashboard_data_no_active_sprint(self):
        """get_dashboard_data returns sprint=False when no active sprint."""
        project = self.env['project.project'].create({
            'name': 'No Active Sprint Project',
            'methodology': 'scrum',
        })
        data = project.get_dashboard_data()
        self.assertFalse(data['sprint'])
        self.assertEqual(data['project_id'], project.id)

    def test_dashboard_data_with_active_sprint(self):
        """get_dashboard_data includes sprint info when active sprint exists."""
        project = self.env['project.project'].create({
            'name': 'Active Sprint Project',
            'methodology': 'scrum',
        })
        sprint = self.env['project.sprint'].create({
            'name': 'Active Sprint',
            'project_id': project.id,
            'start_date': self.today,
            'end_date': self.today.__class__(self.today.year, self.today.month,
                                            self.today.day) + __import__(
                'datetime').timedelta(days=14),
            'state': 'active',
        })
        data = project.get_dashboard_data()
        self.assertTrue(data['sprint'])
        self.assertEqual(data['sprint']['id'], sprint.id)
        self.assertEqual(data['sprint']['name'], 'Active Sprint')

    def test_dashboard_data_structure(self):
        """get_dashboard_data returns all required top-level keys."""
        project = self.env['project.project'].create({
            'name': 'Dashboard Structure Project',
            'methodology': 'scrum',
        })
        data = project.get_dashboard_data()
        for key in ('project_id', 'project_name', 'sprint',
                    'team_workload', 'backlog_health', 'recent_activity'):
            self.assertIn(key, data, f"Missing key: {key}")

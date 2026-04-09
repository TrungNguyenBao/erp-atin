# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, timedelta

from odoo import Command, fields
from odoo.tests.common import TransactionCase


class ScrumTestCommon(TransactionCase):
    """Shared fixtures for all project_scrum tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        Users = cls.env['res.users'].with_context(no_reset_password=True)
        grp_project_user = cls.env.ref('project.group_project_user')
        grp_project_mgr  = cls.env.ref('project.group_project_manager')
        grp_scrum_master = cls.env.ref('project_scrum.group_scrum_master')
        grp_product_owner = cls.env.ref('project_scrum.group_product_owner')
        grp_employee     = cls.env.ref('base.group_user')

        cls.user_scrum = Users.create({
            'name': 'Scrum User',
            'login': 'scrum_user_test',
            'email': 'scrum.user@test.com',
            'groups_id': [Command.set([grp_employee.id, grp_project_user.id])],
        })
        cls.user_master = Users.create({
            'name': 'Scrum Master',
            'login': 'scrum_master_test',
            'email': 'scrum.master@test.com',
            'groups_id': [Command.set([grp_employee.id, grp_scrum_master.id])],
        })
        cls.user_po = Users.create({
            'name': 'Product Owner',
            'login': 'product_owner_test',
            'email': 'product.owner@test.com',
            'groups_id': [Command.set([grp_employee.id, grp_product_owner.id])],
        })
        cls.user_manager = Users.create({
            'name': 'Project Manager',
            'login': 'proj_manager_test',
            'email': 'proj.manager@test.com',
            'groups_id': [Command.set([grp_employee.id, grp_project_mgr.id])],
        })

        cls.project = cls.env['project.project'].with_context(
            mail_create_nolog=True
        ).create({
            'name': 'Test Scrum Project',
            'methodology': 'scrum',
        })

        # Ensure project has kanban stages
        cls.stage_todo = cls.env['project.task.type'].create({
            'name': 'To Do',
            'sequence': 1,
            'project_ids': [Command.link(cls.project.id)],
        })
        cls.stage_in_progress = cls.env['project.task.type'].create({
            'name': 'In Progress',
            'sequence': 2,
            'project_ids': [Command.link(cls.project.id)],
        })
        cls.stage_done = cls.env['project.task.type'].create({
            'name': 'Done',
            'sequence': 10,
            'fold': True,
            'project_ids': [Command.link(cls.project.id)],
        })

        cls.today = date.today()
        cls.sprint = cls._create_sprint('Sprint 1')

    @classmethod
    def _create_sprint(cls, name, start_offset=0, duration=14, state='draft'):
        start = cls.today + timedelta(days=start_offset)
        sprint = cls.env['project.sprint'].create({
            'name': name,
            'project_id': cls.project.id,
            'start_date': start,
            'end_date': start + timedelta(days=duration),
            'capacity_points': 40,
        })
        if state == 'active':
            sprint.write({'state': 'active'})
        elif state == 'done':
            sprint.write({'state': 'done'})
        return sprint

    @classmethod
    def _create_task(cls, name, sprint=None, story_points=3,
                     task_type='task', stage=None):
        vals = {
            'name': name,
            'project_id': cls.project.id,
            'story_points': story_points,
            'task_type': task_type,
        }
        if sprint:
            vals['sprint_id'] = sprint.id
        if stage:
            vals['stage_id'] = stage.id
        return cls.env['project.task'].create(vals)

    @classmethod
    def _create_ceremony(cls, sprint, ceremony_type='planning', name=None):
        return cls.env['scrum.ceremony'].create({
            'name': name or f'{ceremony_type.title()} — {sprint.name}',
            'sprint_id': sprint.id,
            'ceremony_type': ceremony_type,
            'date': fields.Datetime.now(),
        })

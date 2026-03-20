# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import fields, models, _

from odoo.addons.project_scrum.models.project_project_scrum import (
    METHODOLOGY_SELECTION,
)

# Default task stages per methodology
SCRUM_STAGES = ['Backlog', 'To Do', 'In Progress', 'Review', 'Done']
KANBAN_STAGES = ['To Do', 'In Progress', 'Review', 'Done']

# Sprint duration in days
DEFAULT_SPRINT_DURATION = 14


class ProjectCreateWizard(models.TransientModel):
    _name = 'project.create.wizard'
    _description = 'Create Project Wizard'

    name = fields.Char(
        string='Project Name', required=True)
    methodology = fields.Selection(
        METHODOLOGY_SELECTION, default='scrum', required=True,
        help='Choose project management methodology')
    user_id = fields.Many2one(
        'res.users', string='Project Manager',
        default=lambda self: self.env.user)

    def action_create_project(self):
        """Create project with methodology-specific auto-configuration."""
        self.ensure_one()
        project = self.env['project.project'].create({
            'name': self.name,
            'user_id': self.user_id.id,
            'methodology': self.methodology,
        })
        if self.methodology == 'scrum':
            self._setup_scrum_project(project)
        elif self.methodology == 'kanban':
            self._setup_kanban_project(project)
        return project.action_view_tasks()

    def _setup_scrum_project(self, project):
        """Create scrum stages and first draft sprint."""
        self._create_task_stages(project, SCRUM_STAGES, fold_last=True)
        today = fields.Date.context_today(self)
        self.env['project.sprint'].create({
            'name': _('Sprint 1'),
            'project_id': project.id,
            'start_date': today,
            'end_date': today + timedelta(days=DEFAULT_SPRINT_DURATION),
            'state': 'draft',
        })

    def _setup_kanban_project(self, project):
        """Create kanban-optimized stages."""
        self._create_task_stages(project, KANBAN_STAGES, fold_last=True)

    def _create_task_stages(self, project, stage_names, fold_last=False):
        """Create task stages linked to the project."""
        TaskType = self.env['project.task.type']
        for seq, name in enumerate(stage_names, start=1):
            is_last = seq == len(stage_names)
            TaskType.create({
                'name': name,
                'sequence': seq,
                'project_ids': [(4, project.id)],
                'fold': fold_last and is_last,
            })

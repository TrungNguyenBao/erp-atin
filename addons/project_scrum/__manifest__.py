# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Scrum',
    'version': '18.0.3.0.0',
    'category': 'Services/Project',
    'summary': 'Scrum/Agile workflow: sprints, story points, velocity tracking',
    'description': """
        Adds Scrum/Agile project management to Odoo Project:
        - Per-project sprints with goal, capacity, and velocity tracking
        - Story points estimation on tasks (Fibonacci scale)
        - Sprint board (kanban filtered by active sprint)
        - Product backlog view for unassigned tasks
        - Sprint planning wizard for bulk task assignment
        - Sprint close wizard with velocity snapshot
        - Sprint burndown chart and velocity tracking
        - Sprint review and retrospective forms
        - Daily standup view
        - Feature flag: enable/disable Scrum per project
    """,
    'depends': ['project', 'mail'],
    'data': [
        # Security (load first)
        'security/project-scrum-security.xml',
        'security/ir.model.access.csv',
        # Data
        'data/project-scrum-data.xml',
        # Reports
        'report/sprint-burndown-report-views.xml',
        'report/sprint-velocity-report-views.xml',
        # Views
        'views/project-sprint-views.xml',
        'views/project-sprint-board-views.xml',
        'views/project-backlog-views.xml',
        'views/project-epic-views.xml',
        'views/project-release-views.xml',
        'views/project-task-views-inherit.xml',
        'views/project-project-views-inherit.xml',
        # Wizards
        'wizard/sprint-planning-wizard-views.xml',
        'wizard/sprint-close-wizard-views.xml',
        # Menus (load last)
        'views/project-scrum-menus.xml',
    ],
    'demo': [
        'data/project-scrum-demo.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Scrum',
    'version': '18.0.7.0.0',
    'category': 'Services/Project',
    'summary': 'Scrum/Agile workflow: sprints, story points, velocity tracking',
    'description': """
        Adds Scrum/Agile project management to Odoo Project:
        - Project creation wizard with methodology selection (Default/Scrum/Kanban)
        - Per-project sprints with goal, capacity, and velocity tracking
        - Story points estimation on tasks (Fibonacci scale)
        - Sprint board (kanban filtered by active sprint)
        - Product backlog view for unassigned tasks
        - Sprint planning wizard for bulk task assignment
        - Sprint close wizard with velocity snapshot
        - Sprint burndown chart and velocity tracking
        - Sprint review and retrospective forms
        - Daily standup view
        - Scrum ceremonies (Planning, Daily, Review, Retrospective)
        - Scrum role groups (Scrum User, Scrum Master, Product Owner)
        - Task acceptance criteria and task type classification
        - Sprint Summary PDF report
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
        'report/sprint-report-template.xml',
        'report/velocity-report-template.xml',
        # Views
        'views/project-sprint-views.xml',
        'views/project-sprint-board-views.xml',
        'views/project-backlog-views.xml',
        'views/project-epic-views.xml',
        'views/project-release-views.xml',
        'views/project-task-views-inherit.xml',
        'views/project-project-views-inherit.xml',
        'views/project-kanban-views-inherit.xml',
        'views/scrum-ceremony-views.xml',
        # Wizards
        'wizard/sprint-planning-wizard-views.xml',
        'wizard/sprint-close-wizard-views.xml',
        'wizard/project-create-wizard-views.xml',
        # Menus (load last)
        'views/project-scrum-menus.xml',
    ],
    'demo': [
        'data/project-scrum-demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'project_scrum/static/src/scss/project-create-wizard-styles.scss',
            # Sprint Board OWL component (Phase 3)
            'project_scrum/static/src/scss/scrum-design-tokens.scss',
            'project_scrum/static/src/scss/sprint-board.scss',
            'project_scrum/static/src/xml/sprint-board.xml',
            'project_scrum/static/src/js/sprint-board-quick-edit.js',
            'project_scrum/static/src/xml/sprint-board-quick-edit.xml',
            'project_scrum/static/src/js/sprint-board.js',
            # Burndown + Velocity Charts (Phase 4)
            'project_scrum/static/src/scss/charts.scss',
            'project_scrum/static/src/xml/burndown-chart.xml',
            'project_scrum/static/src/xml/velocity-chart.xml',
            'project_scrum/static/src/js/burndown-chart.js',
            'project_scrum/static/src/js/velocity-chart.js',
            'project_scrum/static/src/js/charts-registry.js',
            # Agile Dashboard (Phase 5)
            'project_scrum/static/src/scss/agile-dashboard.scss',
            'project_scrum/static/src/xml/agile-dashboard.xml',
            'project_scrum/static/src/js/agile-dashboard.js',
            # Roadmap Timeline OWL component
            'project_scrum/static/src/scss/roadmap-timeline.scss',
            'project_scrum/static/src/xml/roadmap-timeline.xml',
            'project_scrum/static/src/js/roadmap-timeline.js',
            # Advanced Reports OWL components
            'project_scrum/static/src/scss/advanced-reports.scss',
            'project_scrum/static/src/xml/cfd-chart.xml',
            'project_scrum/static/src/js/cfd-chart.js',
            'project_scrum/static/src/xml/lead-cycle-time-chart.xml',
            'project_scrum/static/src/js/lead-cycle-time-chart.js',
            # Backlog Page OWL component
            'project_scrum/static/src/scss/backlog-page.scss',
            'project_scrum/static/src/xml/backlog-page.xml',
            'project_scrum/static/src/js/backlog-page.js',
        ],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

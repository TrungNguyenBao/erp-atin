{
    'name': 'Project Finance Report',
    'version': '18.0.2.0.0',
    'category': 'Accounting/Reporting',
    'summary': 'Financial reports per project: revenue, receivable, payable, dashboard',
    'description': """
        Project-based financial reporting for VisionAI/ATIN:
        - Revenue report by project (SO-based: revenue, cost, gross profit)
        - Accounts receivable aging by project/customer
        - Accounts payable by project/supplier
        - Financial health dashboard with charts
    """,
    'depends': ['account', 'project', 'analytic', 'sale', 'purchase', 'sales_team'],
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/project-finance-security-rules.xml',
        # Wizards
        'wizard/project-finance-wizard-views.xml',
        # Views
        'views/project-revenue-report-views.xml',
        'views/project-receivable-report-views.xml',
        'views/project-payable-report-views.xml',
        'views/partner-balance-report-views.xml',
        'views/project-finance-dashboard-action.xml',
        'views/project-finance-menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'project_finance_report/static/src/scss/finance-dashboard.scss',
            'project_finance_report/static/src/xml/finance-dashboard.xml',
            'project_finance_report/static/src/js/finance-dashboard.js',
        ],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

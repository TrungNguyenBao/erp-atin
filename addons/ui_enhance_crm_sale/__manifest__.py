# -*- coding: utf-8 -*-
{
    'name': 'CRM & Sale UI Enhancement',
    'version': '18.0.3.0.0',
    'category': 'Sales',
    'summary': 'Tableau-style UI/UX with vertical sidebar for CRM and Sale modules',
    'description': """
        Enhances CRM and Sale modules with Tableau/Salesforce-style UI:
        - Dark navy vertical sidebar with app icons
        - White top navbar with clean layout
        - Flat, corporate SaaS design language
        - Enhanced kanban, form, and list views
    """,
    'depends': ['crm', 'sale', 'web'],
    'data': [
        'views/crm-lead-views-inherit.xml',
        'views/sale-order-views-inherit.xml',
    ],
    'assets': {
        # Override Odoo brand colors BEFORE core variables compile
        'web._assets_primary_variables': [
            ('before', 'web/static/src/scss/primary_variables.scss',
             'ui_enhance_crm_sale/static/src/scss/_odoo-brand-override.scss'),
        ],
        'web.assets_backend': [
            # SCSS: custom variables and mixins
            'ui_enhance_crm_sale/static/src/scss/_variables.scss',
            'ui_enhance_crm_sale/static/src/scss/_mixins.scss',
            # SCSS: sidebar layout (before component styles)
            'ui_enhance_crm_sale/static/src/scss/vertical-sidebar-enhance.scss',
            # SCSS: component-specific styles
            'ui_enhance_crm_sale/static/src/scss/common-enhance.scss',
            'ui_enhance_crm_sale/static/src/scss/crm-form-enhance.scss',
            'ui_enhance_crm_sale/static/src/scss/crm-kanban-enhance.scss',
            'ui_enhance_crm_sale/static/src/scss/sale-form-enhance.scss',
            'ui_enhance_crm_sale/static/src/scss/sale-kanban-enhance.scss',
            # JS patches
            'ui_enhance_crm_sale/static/src/js/*.js',
            # OWL XML templates
            'ui_enhance_crm_sale/static/src/xml/*.xml',
        ],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

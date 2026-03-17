# -*- coding: utf-8 -*-
{
    'name': 'CRM & Sale UI Enhancement',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Modern UI/UX overhaul for CRM and Sale modules',
    'description': """
        Enhances the CRM and Sale modules with modern UI/UX improvements:
        - Modern neutral color palette (slate/gray tones)
        - Improved form layouts with better visual hierarchy
        - Polished kanban cards with hover effects and shadows
        - Enhanced list views with zebra striping and sticky headers
        - Better button organization in form headers
        - Improved typography and spacing throughout
    """,
    'depends': ['crm', 'sale'],
    'data': [
        'views/crm-lead-views-inherit.xml',
        'views/sale-order-views-inherit.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ui_enhance_crm_sale/static/src/scss/_variables.scss',
            'ui_enhance_crm_sale/static/src/scss/_mixins.scss',
            'ui_enhance_crm_sale/static/src/scss/common-enhance.scss',
            'ui_enhance_crm_sale/static/src/scss/crm-form-enhance.scss',
            'ui_enhance_crm_sale/static/src/scss/crm-kanban-enhance.scss',
            'ui_enhance_crm_sale/static/src/scss/sale-form-enhance.scss',
            'ui_enhance_crm_sale/static/src/scss/sale-kanban-enhance.scss',
            'ui_enhance_crm_sale/static/src/js/*.js',
        ],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

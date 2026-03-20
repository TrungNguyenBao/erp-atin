# -*- coding: utf-8 -*-
{
    'name': 'Theme Flavor - Backend Theme',
    'version': '18.0.1.0.0',
    'category': 'Theme',
    'summary': 'Customizable backend theme with style presets, layouts, and color picker',
    'description': """
        Full backend theming for Odoo 18:
        - Flat Design and Aurora UI style presets
        - Horizontal and Vertical sidebar menu layouts
        - Color customization with preset palettes
        - Module icon overrides (FontAwesome or custom images)
    """,
    'author': 'Theme Flavor',
    'website': 'https://github.com/theme-flavor',
    'depends': ['base', 'web', 'bus'],
    'data': [
        'security/ir.model.access.csv',
        'data/theme-flavor-defaults.xml',
        'views/theme-flavor-icon-views.xml',
        'views/res-config-settings-views.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            ('before', 'web/static/src/scss/primary_variables.scss',
             'theme_flavor/static/src/scss/_brand-override.scss'),
        ],
        'web.assets_backend': [
            'theme_flavor/static/src/scss/_variables.scss',
            'theme_flavor/static/src/scss/_mixins.scss',
            'theme_flavor/static/src/scss/theme-flat.scss',
            'theme_flavor/static/src/scss/theme-aurora.scss',
            'theme_flavor/static/src/scss/layout-vertical.scss',
            'theme_flavor/static/src/scss/layout-horizontal.scss',
            'theme_flavor/static/src/scss/color-customization.scss',
            'theme_flavor/static/src/scss/icon-customizer.scss',
            'theme_flavor/static/src/js/settings-color-preview.js',
            'theme_flavor/static/src/xml/settings-color-picker-template.xml',
        ],
        'web.assets_web': [
            'theme_flavor/static/src/js/theme-flavor-service.js',
            'theme_flavor/static/src/js/webclient-layout-patch.js',
            'theme_flavor/static/src/xml/webclient-sidebar-template.xml',
        ],
    },
    'images': ['static/description/banner.png'],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'uninstall_hook': 'uninstall_hook',
}

# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class ThemeFlavorController(http.Controller):

    @http.route('/theme_flavor/settings', type='json', auth='user')
    def get_settings(self):
        """Return all theme settings for the frontend service."""
        ICP = request.env['ir.config_parameter'].sudo()
        return {
            'themeStyle': ICP.get_param('theme_flavor.theme_style', 'flat'),
            'menuLayout': ICP.get_param('theme_flavor.menu_layout', 'horizontal'),
            'colors': {
                'brand': ICP.get_param('theme_flavor.brand_color', '#714B67'),
                'nav': ICP.get_param('theme_flavor.nav_color', '#714B67'),
                'accent': ICP.get_param('theme_flavor.accent_color', '#714B67'),
                'btnPrimary': ICP.get_param('theme_flavor.btn_primary_color', '#714B67'),
                'btnSecondary': ICP.get_param('theme_flavor.btn_secondary_color', '#6C757D'),
                'btnSuccess': ICP.get_param('theme_flavor.btn_success_color', '#28A745'),
                'btnDanger': ICP.get_param('theme_flavor.btn_danger_color', '#DC3545'),
            },
        }

    @http.route('/theme_flavor/icon_overrides', type='json', auth='user')
    def get_icon_overrides(self):
        """Return all active icon overrides for frontend rendering."""
        overrides = request.env['theme.flavor.icon'].sudo().search([
            ('active', '=', True)
        ])
        result = {}
        for ov in overrides:
            data = {'type': ov.icon_type}
            if ov.icon_type == 'fa':
                data['faIcon'] = ov.fa_icon
                data['faColor'] = ov.fa_color
                data['faBgColor'] = ov.fa_bg_color
            else:
                data['imageUrl'] = (
                    f'/web/image/theme.flavor.icon/{ov.id}/custom_icon'
                )
            result[ov.menu_id.id] = data
        return result

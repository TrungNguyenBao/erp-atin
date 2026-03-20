# -*- coding: utf-8 -*-
from odoo import api, fields, models

# Color preset definitions
COLOR_PRESETS = {
    'default': {
        'brand': '#714B67', 'nav': '#714B67', 'accent': '#714B67',
        'btn_primary': '#714B67', 'btn_secondary': '#6C757D',
        'btn_success': '#28A745', 'btn_danger': '#DC3545',
    },
    'ocean': {
        'brand': '#0077B6', 'nav': '#023E8A', 'accent': '#0096C7',
        'btn_primary': '#0077B6', 'btn_secondary': '#6C757D',
        'btn_success': '#2EC4B6', 'btn_danger': '#E63946',
    },
    'forest': {
        'brand': '#2D6A4F', 'nav': '#1B4332', 'accent': '#40916C',
        'btn_primary': '#2D6A4F', 'btn_secondary': '#6C757D',
        'btn_success': '#52B788', 'btn_danger': '#D62828',
    },
    'sunset': {
        'brand': '#E76F51', 'nav': '#264653', 'accent': '#F4A261',
        'btn_primary': '#E76F51', 'btn_secondary': '#6C757D',
        'btn_success': '#2A9D8F', 'btn_danger': '#E63946',
    },
    'royal': {
        'brand': '#7209B7', 'nav': '#3A0CA3', 'accent': '#4361EE',
        'btn_primary': '#7209B7', 'btn_secondary': '#6C757D',
        'btn_success': '#4CC9F0', 'btn_danger': '#F72585',
    },
}


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # -- Theme Style --
    tf_theme_style = fields.Selection([
        ('flat', 'Flat Design'),
        ('aurora', 'Aurora UI'),
    ], string='Theme Style', default='flat',
       config_parameter='theme_flavor.theme_style')

    # -- Menu Layout --
    tf_menu_layout = fields.Selection([
        ('horizontal', 'Horizontal Menu'),
        ('vertical', 'Vertical Sidebar'),
    ], string='Menu Layout', default='horizontal',
       config_parameter='theme_flavor.menu_layout')

    # -- Color Preset --
    tf_color_preset = fields.Selection([
        ('default', 'Odoo Default'),
        ('ocean', 'Ocean Blue'),
        ('forest', 'Forest Green'),
        ('sunset', 'Sunset Orange'),
        ('royal', 'Royal Purple'),
        ('custom', 'Custom'),
    ], string='Color Preset', default='default',
       config_parameter='theme_flavor.color_preset')

    # -- Colors --
    tf_brand_color = fields.Char(
        string='Brand Color', default='#714B67',
        config_parameter='theme_flavor.brand_color')
    tf_nav_color = fields.Char(
        string='Navigation Color', default='#714B67',
        config_parameter='theme_flavor.nav_color')
    tf_accent_color = fields.Char(
        string='Form Accent', default='#714B67',
        config_parameter='theme_flavor.accent_color')
    tf_btn_primary_color = fields.Char(
        string='Button Primary', default='#714B67',
        config_parameter='theme_flavor.btn_primary_color')
    tf_btn_secondary_color = fields.Char(
        string='Button Secondary', default='#6C757D',
        config_parameter='theme_flavor.btn_secondary_color')
    tf_btn_success_color = fields.Char(
        string='Button Success', default='#28A745',
        config_parameter='theme_flavor.btn_success_color')
    tf_btn_danger_color = fields.Char(
        string='Button Danger', default='#DC3545',
        config_parameter='theme_flavor.btn_danger_color')

    @api.onchange('tf_color_preset')
    def _onchange_color_preset(self):
        """Auto-fill color fields when a preset is selected."""
        if self.tf_color_preset and self.tf_color_preset != 'custom':
            preset = COLOR_PRESETS.get(self.tf_color_preset, {})
            if preset:
                self.tf_brand_color = preset['brand']
                self.tf_nav_color = preset['nav']
                self.tf_accent_color = preset['accent']
                self.tf_btn_primary_color = preset['btn_primary']
                self.tf_btn_secondary_color = preset['btn_secondary']
                self.tf_btn_success_color = preset['btn_success']
                self.tf_btn_danger_color = preset['btn_danger']

    def set_values(self):
        """Override to notify frontend of theme changes via bus."""
        super().set_values()
        # Notify all sessions that theme settings changed
        self.env['bus.bus']._sendone(
            self.env.user.partner_id,
            'theme_flavor/settings_changed',
            {}
        )

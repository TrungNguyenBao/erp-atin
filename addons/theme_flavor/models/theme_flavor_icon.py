# -*- coding: utf-8 -*-
from odoo import fields, models


class ThemeFlavorIcon(models.Model):
    _name = 'theme.flavor.icon'
    _description = 'Module Icon Override'
    _rec_name = 'menu_id'

    menu_id = fields.Many2one(
        'ir.ui.menu', string='Module', required=True,
        ondelete='cascade', domain=[('parent_id', '=', False)])
    icon_type = fields.Selection([
        ('fa', 'FontAwesome Icon'),
        ('custom', 'Custom Image'),
    ], string='Icon Type', default='fa', required=True)
    fa_icon = fields.Char(
        string='FA Class', default='fa-cube',
        help='FontAwesome 4.7 class name, e.g. fa-shopping-cart')
    fa_color = fields.Char(string='Icon Color', default='#FFFFFF')
    fa_bg_color = fields.Char(string='Background Color', default='#714B67')
    custom_icon = fields.Binary(string='Custom Icon', attachment=True)
    custom_icon_filename = fields.Char(string='Filename')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('menu_unique', 'UNIQUE(menu_id)',
         'Only one icon override per module is allowed.'),
    ]

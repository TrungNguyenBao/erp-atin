# -*- coding: utf-8 -*-
from . import models
from . import controllers


def uninstall_hook(env):
    """Clean up ir.config_parameter entries on uninstall."""
    env['ir.config_parameter'].sudo().search([
        ('key', 'like', 'theme_flavor.%')
    ]).unlink()

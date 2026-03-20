---
phase: 1
title: "Module Scaffold"
status: pending
effort: 2h
---

# Phase 1: Module Scaffold

## Context
- [plan.md](plan.md) | [Odoo module structure docs](https://www.odoo.com/documentation/18.0/developer/reference/backend/module.html)
- Reference: `addons/ui_enhance_crm_sale/__manifest__.py`

## Overview
Create the `theme_flavor` addon directory with all boilerplate files, manifest, security, and default data. Must be installable and pass `--init` without errors.

## Key Insights
- App Store requires: icon (128x128 PNG), `description/index.html`, `license` field, proper `category`
- Use `category: 'Theme'` for backend themes
- Only depend on `base`, `web` -- keep standalone

## Requirements
- Installable standalone module
- App Store metadata (icon, description, screenshots placeholder)
- Security CSV for custom models
- Default `ir.config_parameter` values via data XML
- Translation-ready (`_()` on all user strings)

## Files to Create

```
addons/theme_flavor/
  __init__.py                          # import models
  __manifest__.py                      # full manifest
  models/__init__.py                   # import model files
  models/res_config_settings.py        # stub (Phase 2 fills it)
  models/theme_flavor_icon.py          # stub (Phase 6 fills it)
  security/ir.model.access.csv         # access rules
  static/description/icon.png          # 128x128 module icon
  static/description/index.html        # App Store description page
  i18n/theme_flavor.pot                # empty pot file
  data/theme-flavor-defaults.xml       # default ir.config_parameter values
```

## Implementation Steps

### 1. Create `__manifest__.py`
```python
{
    'name': 'Theme Flavor - Backend Theme',
    'version': '18.0.1.0.0',
    'category': 'Theme',
    'summary': 'Customizable backend theme with style presets, layouts, and color picker',
    'description': 'Full backend theming: Flat/Aurora styles, horizontal/vertical menu, color customization, module icon overrides.',
    'author': 'Your Company',
    'website': 'https://github.com/user/theme-flavor',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'data/theme-flavor-defaults.xml',
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
            'theme_flavor/static/src/js/*.js',
            'theme_flavor/static/src/xml/*.xml',
        ],
    },
    'images': ['static/description/banner.png'],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'uninstall_hook': 'uninstall_hook',
}
```

### 2. Create `__init__.py` files
```python
# addons/theme_flavor/__init__.py
from . import models

def uninstall_hook(env):
    """Clean up ir.config_parameter on uninstall."""
    env['ir.config_parameter'].sudo().search([
        ('key', 'like', 'theme_flavor.%')
    ]).unlink()
```

### 3. Create `security/ir.model.access.csv`
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_theme_flavor_icon_user,theme.flavor.icon.user,model_theme_flavor_icon,base.group_user,1,0,0,0
access_theme_flavor_icon_admin,theme.flavor.icon.admin,model_theme_flavor_icon,base.group_system,1,1,1,1
```

### 4. Create `data/theme-flavor-defaults.xml`
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo noupdate="1">
    <record model="ir.config_parameter" id="default_theme_style">
        <field name="key">theme_flavor.theme_style</field>
        <field name="value">flat</field>
    </record>
    <record model="ir.config_parameter" id="default_menu_layout">
        <field name="key">theme_flavor.menu_layout</field>
        <field name="value">horizontal</field>
    </record>
    <record model="ir.config_parameter" id="default_brand_color">
        <field name="key">theme_flavor.brand_color</field>
        <field name="value">#714B67</field>
    </record>
    <!-- More defaults in Phase 5 -->
</odoo>
```

### 5. Create App Store description placeholder
- `static/description/icon.png` -- 128x128, use imagemagick skill to generate
- `static/description/index.html` -- HTML with feature list, screenshots placeholders

## Success Criteria
- [ ] `odoo-bin -d test --init theme_flavor` completes without error
- [ ] Module appears in Apps list with correct icon and description
- [ ] Uninstall removes all `theme_flavor.*` config parameters
- [ ] No dependency on `ui_enhance_crm_sale` or any non-core module

## Risk Assessment
- **Low:** Scaffold is standard Odoo boilerplate
- Ensure `uninstall_hook` is in `__manifest__.py` not just `__init__.py`

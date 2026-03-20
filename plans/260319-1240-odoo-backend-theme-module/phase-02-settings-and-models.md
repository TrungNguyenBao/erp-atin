---
phase: 2
title: "Settings & Models"
status: pending
effort: 4h
depends_on: [1]
---

# Phase 2: Settings & Models

## Context
- [plan.md](plan.md) | Phase 1 scaffold must be complete
- Pattern: `addons/base_setup/models/res_config_settings.py` (uses `config_parameter=`)
- Pattern: `addons/web/models/res_config_settings.py` (`web.web_app_name`)

## Overview
Define all theme settings as fields on `res.config.settings` backed by `ir.config_parameter`. Build the Settings UI XML view. Create `theme.flavor.icon` model for icon overrides.

## Key Insights
- `config_parameter='theme_flavor.xxx'` auto-maps field <-> ir.config_parameter
- Selection fields for theme_style and menu_layout; Char fields for colors
- Settings view inherits `res.config.settings` form via xpath on `base_setup.res_config_settings_view_form`
- Multi-company: `ir.config_parameter` is global. For per-company, use `res.company` fields instead. Start global (YAGNI) -- add per-company later if needed.

## Models

### `res.config.settings` (inherit)
File: `models/res_config_settings.py`

```python
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

    # -- Colors --
    tf_brand_color = fields.Char(
        'Brand Color', default='#714B67',
        config_parameter='theme_flavor.brand_color')
    tf_nav_color = fields.Char(
        'Navigation Color', default='#2563EB',
        config_parameter='theme_flavor.nav_color')
    tf_accent_color = fields.Char(
        'Form Accent', default='#714B67',
        config_parameter='theme_flavor.accent_color')
    tf_btn_primary_color = fields.Char(
        'Button Primary', default='#714B67',
        config_parameter='theme_flavor.btn_primary_color')
    tf_btn_secondary_color = fields.Char(
        'Button Secondary', default='#6C757D',
        config_parameter='theme_flavor.btn_secondary_color')
    tf_btn_success_color = fields.Char(
        'Button Success', default='#28A745',
        config_parameter='theme_flavor.btn_success_color')
    tf_btn_danger_color = fields.Char(
        'Button Danger', default='#DC3545',
        config_parameter='theme_flavor.btn_danger_color')

    # -- Preset Palette --
    tf_color_preset = fields.Selection([
        ('default', 'Odoo Default'),
        ('ocean', 'Ocean Blue'),
        ('forest', 'Forest Green'),
        ('sunset', 'Sunset Orange'),
        ('royal', 'Royal Purple'),
        ('custom', 'Custom'),
    ], string='Color Preset', default='default',
       config_parameter='theme_flavor.color_preset')
```

### `theme.flavor.icon` (new model)
File: `models/theme_flavor_icon.py`

```python
class ThemeFlavorIcon(models.Model):
    _name = 'theme.flavor.icon'
    _description = 'Module Icon Override'

    menu_id = fields.Many2one('ir.ui.menu', string='Menu', required=True,
                               domain=[('parent_id', '=', False)])
    icon_type = fields.Selection([
        ('fa', 'FontAwesome'),
        ('custom', 'Custom Image'),
    ], string='Icon Type', default='fa', required=True)
    fa_icon = fields.Char('FontAwesome Class', default='fa-cube')
    custom_icon = fields.Binary('Custom Icon', attachment=True)
    custom_icon_filename = fields.Char('Filename')
    preview_url = fields.Char('Preview URL', compute='_compute_preview_url')
```

## Settings View XML

File: `views/res-config-settings-views.xml`

Inherit `base_setup.res_config_settings_view_form` and add a new section "Theme Flavor" with:
1. **Theme Style** -- radio-style selection with visual preview cards
2. **Menu Layout** -- radio selection (horizontal / vertical) with icons
3. **Color Palette** -- preset dropdown + conditional custom color pickers
4. **Module Icons** -- link to icon override list view

### Layout sketch:
```
[Theme Flavor]
  ├── Style: (o) Flat Design  (o) Aurora UI
  ├── Layout: (o) Horizontal  (o) Vertical Sidebar
  ├── Colors:
  │     Preset: [dropdown] ──> shows preview swatch
  │     (if custom) Brand: [color] Nav: [color] Accent: [color]
  │     (if custom) Buttons: Primary/Secondary/Success/Danger [color pickers]
  └── Module Icons: [Configure Icons →]
```

## Implementation Steps

1. Implement `res_config_settings.py` with all fields
2. Implement `theme_flavor_icon.py` with computed preview
3. Create `views/res-config-settings-views.xml` -- xpath into settings form
4. Create `views/theme-flavor-icon-views.xml` -- tree + form for icon management
5. Add an `onchange` for `tf_color_preset` that populates color fields from preset definitions
6. Add `set_values` override to trigger frontend notification (bus) on save
7. Update `data/theme-flavor-defaults.xml` with all color defaults

## Preset Color Definitions (in `set_values` onchange)

| Preset | Brand | Nav | Accent | Btn Primary | Btn Success | Btn Danger |
|--------|-------|-----|--------|-------------|-------------|------------|
| default | #714B67 | #714B67 | #714B67 | #714B67 | #28A745 | #DC3545 |
| ocean | #0077B6 | #023E8A | #0096C7 | #0077B6 | #2EC4B6 | #E63946 |
| forest | #2D6A4F | #1B4332 | #40916C | #2D6A4F | #52B788 | #D62828 |
| sunset | #E76F51 | #264653 | #F4A261 | #E76F51 | #2A9D8F | #E63946 |
| royal | #7209B7 | #3A0CA3 | #4361EE | #7209B7 | #4CC9F0 | #F72585 |

## Success Criteria
- [ ] Settings page shows Theme Flavor section with all controls
- [ ] Changing preset auto-fills color fields
- [ ] Saving persists to `ir.config_parameter`
- [ ] `theme.flavor.icon` CRUD works from icon management view
- [ ] All strings wrapped in `_()` for translation

## Risk Assessment
- **Medium:** Color picker widget -- Odoo 18 has `color_picker` widget for some fields. Check if it supports hex input. May need custom OWL widget (Phase 5).
- **Low:** Bus notification on save -- needed so frontend picks up changes without reload.

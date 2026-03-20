---
title: "Odoo Backend Theme Module (theme_flavor)"
description: "Standalone backend theme with style presets, layout switching, color customization, and icon overrides for Odoo App Store"
status: pending
priority: P1
effort: 28h
branch: kai/feat/theme-flavor-module
tags: [odoo, theme, backend, app-store, owl, scss]
created: 2026-03-19
---

# theme_flavor - Odoo 18 Backend Theme Module

## Overview

Standalone Odoo 18 backend theme module for the App Store. Users pick a visual style (Flat or Aurora), choose menu layout (horizontal/vertical), customize colors via Settings UI, and override module icons.

**Module name:** `theme_flavor` -- short, memorable, app-store friendly.

## Architecture Summary

- **Models:** `res.config.settings` (transient) + `ir.config_parameter` (persistence) + `theme.flavor.icon` (icon overrides)
- **Frontend:** CSS custom properties (`--tf-*`) toggled at runtime via `<body>` data attributes; no reload needed
- **OWL:** Patch `WebClient` for layout switching; patch `NavBar` for icon overrides; settings widget for color picker
- **SCSS:** Two theme layers loaded via `web.assets_backend`; variables override via `web._assets_primary_variables`

## Phases

| # | Phase | Effort | Status |
|---|-------|--------|--------|
| 1 | [Module Scaffold](phase-01-module-scaffold.md) | 2h | pending |
| 2 | [Settings & Models](phase-02-settings-and-models.md) | 4h | pending |
| 3 | [Theme Styles (SCSS)](phase-03-theme-styles-scss.md) | 6h | pending |
| 4 | [Menu Layout System](phase-04-menu-layout-system.md) | 6h | pending |
| 5 | [Color Customization](phase-05-color-customization.md) | 5h | pending |
| 6 | [Module Icon Customizer](phase-06-module-icon-customizer.md) | 3h | pending |
| 7 | [Testing & Polish](phase-07-testing-and-polish.md) | 2h | pending |

## Key Dependencies

- Odoo 18 (v19.0 source / 18.0 image)
- `base`, `web` modules only (standalone)
- No dependency on `ui_enhance_crm_sale` -- code extracted and adapted

## Key Decisions

- **CSS custom properties over SCSS recompilation** -- enables runtime color switching without asset rebuild
- **`data-tf-theme` and `data-tf-layout` attributes on `<body>`** -- CSS selectors switch styles; OWL sets attributes
- **`ir.config_parameter` for all settings** -- simplest persistence, multi-company via company-scoped keys
- **License:** LGPL-3 (matches Odoo Community)

## File Structure Preview

```
addons/theme_flavor/
  __init__.py
  __manifest__.py
  models/__init__.py
  models/res_config_settings.py
  models/theme_flavor_icon.py
  views/res-config-settings-views.xml
  views/theme-flavor-icon-views.xml
  static/description/icon.png
  static/src/
    scss/_variables.scss
    scss/_mixins.scss
    scss/_brand-override.scss
    scss/theme-flat.scss
    scss/theme-aurora.scss
    scss/layout-vertical.scss
    scss/layout-horizontal.scss
    scss/color-customization.scss
    scss/icon-customizer.scss
    js/theme-flavor-service.js
    js/webclient-layout-patch.js
    js/navbar-icon-patch.js
    js/settings-color-picker-widget.js
    xml/webclient-sidebar-template.xml
    xml/settings-widgets.xml
  security/ir.model.access.csv
  data/theme-flavor-defaults.xml
  data/theme-flavor-presets.xml
  i18n/theme_flavor.pot
```

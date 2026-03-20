---
phase: 7
title: "Testing & Polish"
status: pending
effort: 2h
depends_on: [1, 2, 3, 4, 5, 6]
---

# Phase 7: Testing & Polish

## Context
- [plan.md](plan.md) | All prior phases complete

## Overview
Integration testing, browser compatibility checks, clean uninstall verification, App Store readiness, and documentation polish.

## Testing Checklist

### Functional Tests

- [ ] **Install/Uninstall cycle**: Install module, configure settings, uninstall. Verify no leftover `ir.config_parameter` entries, no orphan menu items, no broken assets.
- [ ] **Theme switching**: Flat -> Aurora -> Flat. All components render correctly.
- [ ] **Layout switching**: Horizontal -> Vertical -> Horizontal. No layout artifacts.
- [ ] **Color presets**: Each preset applies correct colors. Switch between presets.
- [ ] **Custom colors**: Pick custom hex values. Verify they persist and render.
- [ ] **Icon overrides**: Add FA override, add custom image, remove override. Verify restore.
- [ ] **Multi-user**: User A changes theme, User B sees changes (global settings).
- [ ] **Mobile responsive**: Sidebar hidden on <768px. Navbar functional.
- [ ] **RTL support**: Test with Arabic/Hebrew language. Sidebar on right side.

### Browser Compatibility

| Feature | Chrome 90+ | Firefox 90+ | Safari 15+ | Edge 90+ |
|---------|-----------|------------|-----------|---------|
| CSS custom properties | Y | Y | Y | Y |
| `color-mix()` | Y | Y | Y (16.2+) | Y |
| `backdrop-filter` | Y | Y | Y | Y |
| `<input type="color">` | Y | Y | Y | Y |
| `:has()` selector | Y | Y (121+) | Y | Y |

Fallback strategy for older browsers:
- `@supports not (backdrop-filter: blur(1px))` -> solid background
- `@supports not (color-mix(in srgb, red, blue))` -> hardcoded derived colors

### Python Tests

File: `tests/test_theme_flavor.py`

```python
class TestThemeFlavor(TransactionCase):
    def test_default_settings(self):
        """Default config params exist after install."""
        ICP = self.env['ir.config_parameter'].sudo()
        self.assertEqual(ICP.get_param('theme_flavor.theme_style'), 'flat')
        self.assertEqual(ICP.get_param('theme_flavor.menu_layout'), 'horizontal')

    def test_preset_colors(self):
        """Preset selection fills color fields."""
        settings = self.env['res.config.settings'].create({})
        settings.tf_color_preset = 'ocean'
        settings._onchange_color_preset()
        self.assertEqual(settings.tf_brand_color, '#0077B6')

    def test_icon_override_unique(self):
        """Duplicate menu override raises constraint."""
        menu = self.env['ir.ui.menu'].search([('parent_id', '=', False)], limit=1)
        self.env['theme.flavor.icon'].create({'menu_id': menu.id, 'fa_icon': 'fa-star'})
        with self.assertRaises(Exception):
            self.env['theme.flavor.icon'].create({'menu_id': menu.id, 'fa_icon': 'fa-heart'})

    def test_uninstall_cleanup(self):
        """Uninstall removes config params."""
        # Covered by uninstall_hook test
```

### JS Tests (optional, nice-to-have)

Tour test: Open Settings -> Theme Flavor -> Change preset -> Save -> Verify body attributes.

## App Store Readiness

### Required Files
- [ ] `static/description/icon.png` -- 128x128 module icon
- [ ] `static/description/index.html` -- rich description with screenshots
- [ ] `static/description/banner.png` -- 1200x600 banner image
- [ ] Screenshots in `static/description/` (flat theme, aurora theme, settings page, color picker)

### Manifest Checks
- [ ] `license: 'LGPL-3'`
- [ ] `version: '18.0.1.0.0'`
- [ ] `category: 'Theme'`
- [ ] `application: True`
- [ ] `depends` only `['base', 'web']`
- [ ] `images` field lists banner

### i18n
- [ ] All Python strings use `_()`
- [ ] XML labels have `string=` attributes (auto-extracted)
- [ ] Generate `.pot` file: `./odoo-bin -d test --modules theme_flavor --i18n-export`

## Polish Items

1. **Settings page UX**: Add visual theme preview cards (small screenshots of flat vs aurora)
2. **Color preset swatches**: Show color dots next to each preset name in dropdown
3. **Sidebar animation**: Smooth collapse/expand transition
4. **Loading state**: Brief skeleton/spinner while theme service loads settings
5. **Error handling**: If RPC fails, fall back to defaults (no blank UI)
6. **Console warnings**: Zero console errors/warnings in both themes and layouts

## Success Criteria
- [ ] All functional tests pass
- [ ] Clean install -> configure -> uninstall cycle: no errors, no leftover data
- [ ] Works in Chrome, Firefox, Safari, Edge (latest versions)
- [ ] App Store requirements met (icon, description, license, version)
- [ ] No console errors in browser DevTools
- [ ] Module size < 500KB (excluding screenshots)

## Risk Assessment
- **Low:** Screenshot generation -- use browser DevTools or manual capture
- **Medium:** RTL support -- sidebar positioning may need `[dir="rtl"]` overrides. Test with Arabic.

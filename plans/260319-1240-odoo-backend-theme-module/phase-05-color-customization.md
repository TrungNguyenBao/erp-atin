---
phase: 5
title: "Color Customization"
status: pending
effort: 5h
depends_on: [2, 3, 4]
---

# Phase 5: Color Customization

## Context
- [plan.md](plan.md) | Phase 2 (models), Phase 3 (CSS vars), Phase 4 (service)
- Color values stored in `ir.config_parameter`, loaded by `theme-flavor-service.js`

## Overview
Runtime color customization via Settings UI. Users pick a preset palette OR enter custom hex colors. Changes apply instantly via CSS custom property updates (no asset rebuild).

## Key Insights
- **No SCSS recompilation needed** -- colors flow through CSS custom properties
- Service reads colors from backend, sets `document.documentElement.style.setProperty()`
- Preset selection triggers `onchange` that fills color fields
- Color picker widget: Odoo 18 doesn't have a hex color picker widget. Build a minimal OWL widget.
- `$o-community-color` override in `_brand-override.scss` is static (compile-time). For full brand override, also set CSS vars on `:root` at runtime. This covers 95% of UI; the SCSS override handles the remaining compiled assets.

## Architecture

```
Settings UI                          Frontend
┌──────────────┐    save     ┌────────────────────┐
│ Color Picker │───────────→│ ir.config_parameter │
│ Preset Select│             └────────┬───────────┘
└──────────────┘                      │ bus notify
                                      ▼
                         ┌────────────────────────┐
                         │ theme-flavor-service.js │
                         │   loadSettings()        │
                         │   applyToDOM()          │
                         │   → style.setProperty() │
                         └────────────────────────┘
```

## Files to Create/Modify

| File | Purpose |
|------|---------|
| `js/settings-color-picker-widget.js` | OWL color picker widget for settings form |
| `xml/settings-widgets.xml` | Template for color picker widget |
| `scss/color-customization.scss` | Map `--tf-*` vars to Odoo component overrides |
| `views/res-config-settings-views.xml` | Update: add color picker fields |
| `data/theme-flavor-presets.xml` | Preset palette definitions |

## Implementation Steps

### 1. Color Picker Widget (`settings-color-picker-widget.js`)

Minimal OWL widget wrapping `<input type="color">` + hex text input.

```javascript
/** @odoo-module **/
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useState } from "@odoo/owl";

class TfColorPicker extends Component {
    static template = "theme_flavor.ColorPicker";
    static props = { ...standardFieldProps };

    setup() {
        this.state = useState({ color: this.props.record.data[this.props.name] || '#714B67' });
    }

    onColorChange(ev) {
        this.state.color = ev.target.value;
        this.props.record.update({ [this.props.name]: ev.target.value });
    }

    onTextChange(ev) {
        const val = ev.target.value;
        if (/^#[0-9A-Fa-f]{6}$/.test(val)) {
            this.state.color = val;
            this.props.record.update({ [this.props.name]: val });
        }
    }
}

registry.category("fields").add("tf_color_picker", {
    component: TfColorPicker,
    supportedTypes: ["char"],
});
```

### 2. Color Picker Template (`xml/settings-widgets.xml`)

```xml
<templates>
  <t t-name="theme_flavor.ColorPicker">
    <div class="tf-color-picker d-flex align-items-center gap-2">
      <input type="color" t-att-value="state.color"
             t-on-input="onColorChange"
             class="tf-color-picker__swatch"/>
      <input type="text" t-att-value="state.color"
             t-on-change="onTextChange"
             class="form-control tf-color-picker__hex"
             maxlength="7" placeholder="#000000"
             style="width: 100px;"/>
      <span class="tf-color-picker__preview rounded-circle"
            t-attf-style="background: #{state.color}; width: 24px; height: 24px;"/>
    </div>
  </t>
</templates>
```

### 3. Settings View Update

In `res-config-settings-views.xml`, use `widget="tf_color_picker"` on color fields:

```xml
<field name="tf_brand_color" widget="tf_color_picker"/>
<field name="tf_nav_color" widget="tf_color_picker"/>
<!-- etc. -->
```

Conditional visibility for custom colors:
```xml
<div t-attf-class="#{record.tf_color_preset.raw_value != 'custom' ? 'd-none' : ''}">
    <!-- custom color pickers here -->
</div>
```

### 4. Preset Onchange (in `res_config_settings.py`)

```python
@api.onchange('tf_color_preset')
def _onchange_color_preset(self):
    PRESETS = {
        'default': {'brand': '#714B67', 'nav': '#714B67', ...},
        'ocean': {'brand': '#0077B6', 'nav': '#023E8A', ...},
        # ... other presets
    }
    if self.tf_color_preset and self.tf_color_preset != 'custom':
        preset = PRESETS.get(self.tf_color_preset, {})
        self.tf_brand_color = preset.get('brand', '#714B67')
        self.tf_nav_color = preset.get('nav', '#714B67')
        # ... map all fields
```

### 5. `color-customization.scss` -- Bridge CSS Vars to Odoo Classes

Map `--tf-*` to Odoo's actual component selectors:

```scss
// Buttons
.btn-primary {
  background-color: var(--tf-btn-primary) !important;
  border-color: var(--tf-btn-primary) !important;
}
.btn-secondary {
  background-color: var(--tf-btn-secondary) !important;
  border-color: var(--tf-btn-secondary) !important;
}
.btn-success {
  background-color: var(--tf-btn-success) !important;
  border-color: var(--tf-btn-success) !important;
}
.btn-danger {
  background-color: var(--tf-btn-danger) !important;
  border-color: var(--tf-btn-danger) !important;
}

// Forms
.o_form_view .o_form_sheet {
  border-color: var(--tf-border);
}

// Focus states
.form-control:focus {
  border-color: var(--tf-brand) !important;
  box-shadow: 0 0 0 0.2rem color-mix(in srgb, var(--tf-brand) 25%, transparent) !important;
}

// Links
a:not(.btn) { color: var(--tf-brand); }

// Selection highlights, badges, etc.
.o_kanban_header .o_kanban_count { color: var(--tf-brand); }
```

### 6. Bus Notification on Save

In `res_config_settings.py` `set_values()`:
```python
def set_values(self):
    super().set_values()
    self.env['bus.bus']._sendone(
        self.env.user.partner_id,
        'theme_flavor/settings_changed', {}
    )
```

### 7. Live Preview in Service

`theme-flavor-service.js` `applyToDOM` sets all color properties:
```javascript
function applyToDOM(s) {
    const root = document.documentElement;
    const colorMap = {
        '--tf-brand': s.colors.brand,
        '--tf-nav-bg': s.colors.nav,
        '--tf-accent': s.colors.accent,
        '--tf-btn-primary': s.colors.btnPrimary,
        '--tf-btn-secondary': s.colors.btnSecondary,
        '--tf-btn-success': s.colors.btnSuccess,
        '--tf-btn-danger': s.colors.btnDanger,
    };
    for (const [prop, val] of Object.entries(colorMap)) {
        if (val) root.style.setProperty(prop, val);
    }
}
```

## Success Criteria
- [ ] Selecting a preset fills all color fields and shows preview swatches
- [ ] Custom colors: each picker updates its field
- [ ] Saving colors applies immediately without page reload
- [ ] Colors affect: buttons, navbar, sidebar, forms, links, focus rings
- [ ] Hex validation: only valid 6-digit hex accepted
- [ ] Preset "Custom" does not overwrite existing custom colors

## Risk Assessment
- **Medium:** `!important` overload on button colors. Odoo uses `!important` itself on buttons. Test specificity carefully.
- **Low:** `color-mix()` browser support. Fallback: service also sets derived colors (hover, light variants) as separate properties.
- **Medium:** Some Odoo colors come from compiled SCSS (`$o-community-color`). CSS vars won't override those. Document that a page reload after first install is needed for SCSS-compiled elements.

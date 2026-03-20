---
phase: 3
title: "Theme Styles (SCSS)"
status: pending
effort: 6h
depends_on: [1]
---

# Phase 3: Theme Styles (SCSS)

## Context
- [plan.md](plan.md) | Reference: `addons/ui_enhance_crm_sale/static/src/scss/`
- Patterns established in `_variables.scss`, `_mixins.scss` from existing module

## Overview
Implement two theme style layers (Flat Design, Aurora UI) using CSS custom properties. Styles activate based on `data-tf-theme="flat|aurora"` on `<body>`. Both themes share a common variable layer (`_variables.scss`).

## Key Insights
- **CSS custom properties (not SCSS vars) for runtime switching** -- SCSS vars compile once; CSS vars switch instantly
- `_brand-override.scss` loaded before `primary_variables.scss` reads from `ir.config_parameter` at page load via controller (or uses defaults)
- Both themes override the same `--tf-*` custom properties, so components only reference `--tf-*` vars
- Keep `!important` minimal -- use specificity via `[data-tf-theme="flat"]` selector

## Architecture

```
<body data-tf-theme="flat" data-tf-layout="horizontal">
  ├── CSS: [data-tf-theme="flat"] .o_form_view { ... }
  └── CSS: [data-tf-theme="aurora"] .o_form_view { ... }
```

### Variable Layer (`_variables.scss`)
Defines SCSS defaults + CSS custom property declarations on `:root`.

### Theme Layers
Each theme file overrides `--tf-*` vars under its `[data-tf-theme]` selector.

## Files to Create/Modify

| File | Purpose |
|------|---------|
| `scss/_variables.scss` | Design tokens as CSS custom properties |
| `scss/_mixins.scss` | Shared mixins (card, badge, focus-ring, glassmorphism) |
| `scss/_brand-override.scss` | Override `$o-community-color` / `$o-enterprise-color` |
| `scss/theme-flat.scss` | Flat Design theme overrides |
| `scss/theme-aurora.scss` | Aurora UI theme overrides |

## Implementation Steps

### 1. `_variables.scss` -- CSS Custom Property Layer

```scss
:root {
  // -- Brand --
  --tf-brand: #714B67;
  --tf-brand-hover: color-mix(in srgb, var(--tf-brand) 85%, black);
  --tf-brand-light: color-mix(in srgb, var(--tf-brand) 15%, white);

  // -- Navigation --
  --tf-nav-bg: #714B67;
  --tf-nav-text: rgba(255, 255, 255, 0.9);
  --tf-nav-text-active: #FFFFFF;

  // -- Surface --
  --tf-surface: #FFFFFF;
  --tf-surface-alt: #F8FAFC;
  --tf-surface-hover: #F1F5F9;

  // -- Text --
  --tf-text: #1E293B;
  --tf-text-secondary: #475569;
  --tf-text-muted: #94A3B8;

  // -- Borders --
  --tf-border: #E2E8F0;
  --tf-border-focus: var(--tf-brand);

  // -- Shadows --
  --tf-shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --tf-shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1);
  --tf-shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1);

  // -- Radius --
  --tf-radius-sm: 6px;
  --tf-radius-md: 10px;
  --tf-radius-lg: 14px;

  // -- Buttons --
  --tf-btn-primary: var(--tf-brand);
  --tf-btn-secondary: #6C757D;
  --tf-btn-success: #28A745;
  --tf-btn-danger: #DC3545;

  // -- Transition --
  --tf-transition-fast: 0.15s ease;
  --tf-transition-base: 0.2s ease;
}
```

### 2. `theme-flat.scss` -- Flat Design

Target: clean, minimal, solid colors, no shadows, sharp corners.

```scss
[data-tf-theme="flat"] {
  --tf-shadow-sm: none;
  --tf-shadow-md: none;
  --tf-shadow-lg: none;
  --tf-radius-sm: 4px;
  --tf-radius-md: 6px;
  --tf-radius-lg: 8px;

  // Form views: flat cards, subtle borders
  .o_form_view .o_form_sheet {
    box-shadow: none;
    border: 1px solid var(--tf-border);
    border-radius: var(--tf-radius-md);
  }

  // Kanban: flat cards
  .o_kanban_record {
    box-shadow: none;
    border: 1px solid var(--tf-border);
    &:hover { border-color: var(--tf-brand); }
  }

  // Buttons: solid, no shadow
  .btn-primary {
    box-shadow: none;
    border-radius: var(--tf-radius-sm);
  }

  // Navbar: solid color
  .o_main_navbar {
    box-shadow: none;
    border-bottom: 2px solid var(--tf-border);
  }
}
```

### 3. `theme-aurora.scss` -- Aurora UI

Target: gradients, glassmorphism, blur effects, soft shadows, rounded corners.

```scss
[data-tf-theme="aurora"] {
  --tf-shadow-sm: 0 2px 8px rgba(0,0,0,0.06);
  --tf-shadow-md: 0 8px 24px rgba(0,0,0,0.08);
  --tf-shadow-lg: 0 16px 48px rgba(0,0,0,0.12);
  --tf-radius-sm: 8px;
  --tf-radius-md: 12px;
  --tf-radius-lg: 16px;

  // Glassmorphism mixin application
  .o_form_view .o_form_sheet {
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: var(--tf-shadow-md);
    border-radius: var(--tf-radius-lg);
  }

  // Kanban: glass cards with hover lift
  .o_kanban_record {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.4);
    box-shadow: var(--tf-shadow-sm);
    border-radius: var(--tf-radius-md);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    &:hover {
      transform: translateY(-2px);
      box-shadow: var(--tf-shadow-lg);
    }
  }

  // Navbar: gradient + blur
  .o_main_navbar {
    background: linear-gradient(135deg,
      var(--tf-nav-bg),
      color-mix(in srgb, var(--tf-nav-bg) 70%, white)) !important;
    backdrop-filter: blur(10px);
    box-shadow: var(--tf-shadow-sm);
  }

  // Buttons: gradient + soft shadow
  .btn-primary {
    background: linear-gradient(135deg, var(--tf-btn-primary),
      color-mix(in srgb, var(--tf-btn-primary) 80%, white));
    box-shadow: 0 4px 12px color-mix(in srgb, var(--tf-btn-primary) 30%, transparent);
    border-radius: var(--tf-radius-sm);
  }

  // Subtle gradient background
  .o_action_manager {
    background: linear-gradient(180deg, var(--tf-surface) 0%, var(--tf-surface-alt) 100%);
  }
}
```

### 4. `_mixins.scss` -- Shared Utilities

```scss
@mixin tf-glassmorphism($opacity: 0.75, $blur: 12px) {
  background: rgba(255, 255, 255, $opacity);
  backdrop-filter: blur($blur);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

@mixin tf-card-hover {
  transition: transform var(--tf-transition-base),
              box-shadow var(--tf-transition-base);
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--tf-shadow-lg);
  }
}

@mixin tf-focus-ring {
  &:focus-within {
    outline: none;
    box-shadow: 0 0 0 2px var(--tf-brand-light), 0 0 0 4px rgba(var(--tf-brand), 0.2);
  }
}
```

### 5. `_brand-override.scss`

Loaded before `primary_variables.scss`. Initially static; Phase 5 makes it dynamic.

```scss
// Default brand override -- overridden at runtime by CSS custom properties
$o-community-color: #714B67;
$o-enterprise-color: #714B67;
```

## Success Criteria
- [ ] `data-tf-theme="flat"` renders flat UI (no shadows, minimal radius)
- [ ] `data-tf-theme="aurora"` renders glassmorphism effects
- [ ] Switching attribute on `<body>` instantly changes appearance
- [ ] No `!important` on custom property declarations (only on Odoo overrides where necessary)
- [ ] Each SCSS file under 200 lines
- [ ] `color-mix()` used for derived colors (modern CSS, supported in all modern browsers)

## Risk Assessment
- **Medium:** `backdrop-filter` not supported in older browsers. Degrade gracefully with `@supports`.
- **Medium:** `color-mix()` requires modern browsers. Add fallback solid colors.
- **Low:** SCSS file ordering matters -- `_variables.scss` before theme files.

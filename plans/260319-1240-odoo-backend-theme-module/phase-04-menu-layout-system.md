---
phase: 4
title: "Menu Layout System"
status: pending
effort: 6h
depends_on: [1, 3]
---

# Phase 4: Menu Layout System

## Context
- [plan.md](plan.md) | Reference: `ui_enhance_crm_sale/static/src/js/vertical-sidebar-webclient-patch.js`
- Reference: `ui_enhance_crm_sale/static/src/xml/vertical-sidebar-template.xml`
- Reference: `ui_enhance_crm_sale/static/src/scss/vertical-sidebar-enhance.scss`

## Overview
Two menu layouts selectable from Settings: horizontal (default Odoo top navbar) and vertical sidebar. Controlled by `data-tf-layout="horizontal|vertical"` on `<body>`. Extract and adapt vertical sidebar from `ui_enhance_crm_sale`.

## Key Insights
- Horizontal layout = default Odoo behavior, zero CSS changes needed (just don't activate vertical styles)
- Vertical layout uses CSS Grid to position sidebar + navbar + action_manager
- OWL patch on `WebClient` manages layout state and reads from `ir.config_parameter` via RPC on setup
- `t-if` on sidebar template to conditionally render based on layout setting
- Mobile: always hide sidebar, revert to horizontal (existing pattern works)

## Architecture

```
data-tf-layout="horizontal" --> Default Odoo, sidebar hidden
data-tf-layout="vertical"   --> CSS Grid layout, sidebar visible

WebClient.setup():
  1. RPC to get theme_flavor.menu_layout from ir.config_parameter
  2. Set data-tf-layout on document.body
  3. Listen to bus for setting changes (live update)
```

## Files to Create/Modify

| File | Purpose |
|------|---------|
| `js/theme-flavor-service.js` | OWL service: loads settings, sets body attrs, listens for changes |
| `js/webclient-layout-patch.js` | Patch WebClient: sidebar state, app list, navigation |
| `xml/webclient-sidebar-template.xml` | Sidebar template (extracted from ui_enhance_crm_sale) |
| `scss/layout-vertical.scss` | Vertical sidebar CSS (adapted from ui_enhance_crm_sale) |
| `scss/layout-horizontal.scss` | Minimal overrides for horizontal mode (mostly theme vars on navbar) |

## Implementation Steps

### 1. `theme-flavor-service.js` -- Central Theme Service

```javascript
/** @odoo-module **/
import { registry } from "@web/core/registry";
import { reactive } from "@odoo/owl";

const themeFlavorService = {
    dependencies: ["rpc", "bus_service"],
    start(env, { rpc, bus_service }) {
        const state = reactive({
            themeStyle: "flat",
            menuLayout: "horizontal",
            colors: {},
        });

        // Load settings on startup
        async function loadSettings() {
            const result = await rpc("/theme_flavor/settings");
            Object.assign(state, result);
            applyToDOM(state);
        }

        function applyToDOM(s) {
            document.body.dataset.tfTheme = s.themeStyle;
            document.body.dataset.tfLayout = s.menuLayout;
            // Apply color custom properties
            const root = document.documentElement;
            if (s.colors.brand) root.style.setProperty('--tf-brand', s.colors.brand);
            if (s.colors.nav) root.style.setProperty('--tf-nav-bg', s.colors.nav);
            // ... other colors
        }

        // Listen for setting changes via bus
        bus_service.subscribe("theme_flavor/settings_changed", () => {
            loadSettings();
        });

        loadSettings();
        return state;
    },
};

registry.category("services").add("theme_flavor", themeFlavorService);
```

### 2. Backend Controller for Settings Endpoint

File: `controllers/theme_flavor_controller.py`

```python
from odoo import http
from odoo.http import request

class ThemeFlavorController(http.Controller):
    @http.route('/theme_flavor/settings', type='json', auth='user')
    def get_settings(self):
        ICP = request.env['ir.config_parameter'].sudo()
        return {
            'themeStyle': ICP.get_param('theme_flavor.theme_style', 'flat'),
            'menuLayout': ICP.get_param('theme_flavor.menu_layout', 'horizontal'),
            'colors': {
                'brand': ICP.get_param('theme_flavor.brand_color', '#714B67'),
                'nav': ICP.get_param('theme_flavor.nav_color', '#2563EB'),
                'accent': ICP.get_param('theme_flavor.accent_color', '#714B67'),
                'btnPrimary': ICP.get_param('theme_flavor.btn_primary_color', '#714B67'),
                'btnSecondary': ICP.get_param('theme_flavor.btn_secondary_color', '#6C757D'),
                'btnSuccess': ICP.get_param('theme_flavor.btn_success_color', '#28A745'),
                'btnDanger': ICP.get_param('theme_flavor.btn_danger_color', '#DC3545'),
            },
        }
```

### 3. `webclient-layout-patch.js` -- Sidebar State

Extract from `ui_enhance_crm_sale` vertical-sidebar-webclient-patch.js. Key changes:
- **Conditional**: only activate sidebar behavior when `state.menuLayout === 'vertical'`
- Use `theme_flavor` service instead of hardcoded behavior
- Same `sidebarApps`, `currentApp`, `getAppHref`, `onSidebarAppClick` methods

```javascript
/** @odoo-module **/
import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";

patch(WebClient.prototype, {
    setup() {
        super.setup(...arguments);
        this.themeFlavorService = useService("theme_flavor");
        this.sidebarMenuService = useService("menu");
        this.sidebarState = useState({ collapsed: false });
    },
    get isVerticalLayout() {
        return this.themeFlavorService.menuLayout === 'vertical';
    },
    get sidebarCollapsed() { return this.sidebarState.collapsed; },
    get sidebarApps() { return this.sidebarMenuService.getApps() || []; },
    get currentApp() { return this.sidebarMenuService.getCurrentApp(); },
    getAppHref(app) { return `/odoo/${app.actionPath || "action-" + app.actionID}`; },
    onSidebarAppClick(app) { app && this.sidebarMenuService.selectMenu(app); },
    onToggleSidebar() { this.sidebarState.collapsed = !this.sidebarState.collapsed; },
});
```

### 4. `webclient-sidebar-template.xml`

Adapted from `ui_enhance_crm_sale`. Key change: wrap in `t-if="isVerticalLayout"`.

```xml
<t t-inherit="web.WebClient" t-inherit-mode="extension">
  <xpath expr="//NavBar" position="before">
    <aside t-if="isVerticalLayout"
           t-att-class="'tf-sidebar' + (sidebarCollapsed ? ' collapsed' : '')"
           t-if="!state.fullscreen">
      <!-- Logo, Toolbar, Nav (same structure as ui_enhance_crm_sale) -->
    </aside>
  </xpath>
</t>
```

### 5. `layout-vertical.scss`

Adapted from `ui_enhance_crm_sale/static/src/scss/vertical-sidebar-enhance.scss`:
- Replace `$sidebar-bg` with `var(--tf-nav-bg)`
- Replace all hardcoded colors with `--tf-*` CSS variables
- Scope under `[data-tf-layout="vertical"]`
- Same CSS Grid approach

### 6. `layout-horizontal.scss`

Minimal: apply theme colors to default Odoo navbar.

```scss
[data-tf-layout="horizontal"] {
  .o_main_navbar {
    background: var(--tf-nav-bg) !important;
    .o_menu_brand { color: var(--tf-nav-text-active) !important; }
    .o_menu_sections .o_nav_entry { color: var(--tf-nav-text); }
  }
}
```

## Additional Files

Add to scaffold:
```
controllers/__init__.py
controllers/theme_flavor_controller.py
```
Update `__init__.py` to import controllers.

## Success Criteria
- [ ] Horizontal layout: default Odoo navbar with theme colors applied
- [ ] Vertical layout: sidebar appears, navbar becomes secondary
- [ ] Switching layout in Settings applies on next page load (or via bus for live)
- [ ] Sidebar collapse/expand works
- [ ] Mobile: sidebar hidden, horizontal navbar restored
- [ ] No conflicts with `ui_enhance_crm_sale` if both installed (different selectors)

## Risk Assessment
- **Medium:** Bus notification for live layout switching -- may require page reload for CSS Grid change. Acceptable to show "reload required" toast.
- **Low:** Sidebar z-index conflicts with Odoo dialogs. Use z-index 1050 (below modals at 1055).
- **Medium:** When both `ui_enhance_crm_sale` and `theme_flavor` installed, duplicate sidebar. Mitigate: document as incompatible, or detect and skip.

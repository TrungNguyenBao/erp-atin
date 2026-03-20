# Odoo 18 Backend Theming & Customization Research Report

**Date:** 2026-03-19
**Focus:** Odoo 18 asset bundling, web client architecture, SCSS theming, menu system, OWL components, and settings integration
**Status:** Comprehensive technical analysis

---

## Executive Summary

Odoo 18 provides a robust system for backend theming through **asset bundles**, **SCSS variable overrides**, **OWL component patching**, and **configuration settings integration**. The architecture separates concerns across:

1. **Asset management** (bundles, loading order, operations)
2. **SCSS theming** (primary variables, custom properties, color palettes)
3. **WebClient architecture** (NavBar, menu service, component hierarchy)
4. **Component extension** (patching via `@web/core/utils/patch`)
5. **Settings integration** (res.config.settings, theme configuration)

---

## 1. Odoo 18 Asset Bundle System

### 1.1 Asset Bundle Fundamentals

**Definition:** Assets are static resources (JS, CSS/SCSS, XML templates) organized into named bundles in `__manifest__.py`. Each bundle groups related resources that load together.

**Key characteristics:**
- Defined via `'assets'` key in manifest with bundle name → file list mapping
- Supports lazy loading and conditional inclusion
- Order-dependent (respects load sequence)
- Modifiable via directives (prepend, before, after, remove, include)

### 1.2 Asset Operations & Loading Order

**Operation Syntax:**

```python
'assets': {
    'web.assets_backend': [
        # Standard append (end of bundle)
        'module/path/file.js',

        # Prepend (start of bundle)
        ('prepend', 'module/path/early-load.js'),

        # Before a target file
        ('before', 'target_file.js', 'module/path/new-file.js'),

        # After a target file
        ('after', 'target_file.js', 'module/path/new-file.js'),

        # Remove a file from bundle
        ('remove', 'unwanted_file.js'),

        # Include sub-bundles (minimizes duplication)
        'module/_assets_sub_bundle',
    ],
}
```

**Critical:** Loading order matches sequence → CSS specificity & variable precedence depend on file position.

### 1.3 Asset Bundle Names (Odoo 18 Standard)

| Bundle Name | Purpose | Scope |
|---|---|---|
| `web.assets_backend` | Main backend JS/CSS | All backend views |
| `web._assets_primary_variables` | SCSS color/font variables | Loads before primary_variables.scss |
| `web.assets_common` | Shared JS/CSS | Backend + Portal |
| `web.assets_frontend` | Website/Portal styles | Frontend only |
| `web.assets_tests` | Test runner assets | Tests only |
| `web.qweb` | QWeb templates | All views |

**Example usage:**
```python
'assets': {
    'web._assets_primary_variables': [
        ('before', 'web/static/src/scss/primary_variables.scss',
         'my_module/static/src/scss/_brand-override.scss'),
    ],
    'web.assets_backend': [
        'my_module/static/src/scss/theme.scss',
        'my_module/static/src/js/patches.js',
    ],
}
```

### 1.4 Asset Types & File Handling

**JavaScript:**
- ES6 modules with `/** @odoo-module */` header
- Lazy-loaded or bundled into main JS file
- Patching syntax: `import { patch } from "@web/core/utils/patch"`

**SCSS/CSS:**
- Compiled to CSS during asset processing
- Variable/mixin inheritance via SCSS `!default` flag
- Custom properties supported for runtime theming

**XML Templates:**
- OWL component templates (`.xml`)
- QWeb templates (`.qweb`)
- Loaded into component context

---

## 2. Odoo 18 SCSS Variable System & Theming

### 2.1 Primary Variables Architecture

**File:** `web/static/src/scss/primary_variables.scss`

**Purpose:** Defines all Odoo brand colors, fonts, spacing, breakpoints used across backend. Modules **override via `_assets_primary_variables` bundle** before this file loads.

**Key variables (defaults):**

```scss
// Colors
$o-community-color: #71639e !default;      // Purple (Odoo default)
$o-enterprise-color: #714B67!default;      // Enterprise purple
$o-brand-primary: $o-community-color !default;
$o-brand-secondary: #8f8f8f !default;      // Gray

// Semantic colors
$o-action: $o-brand-primary !default;      // Active/CTA
$o-success: #28a745 !default;              // Green
$o-warning: #ffac00 !default;              // Orange
$o-danger: #dc3545 !default;               // Red
$o-info: #17a2b8 !default;                 // Cyan

// Typography
$o-font-size-base: 0.875rem !default;      // 14px
$o-font-weight-normal: 400 !default;
$o-font-weight-bold: 700 !default;
$o-system-fonts: (...) !default;           // System font stack

// Spacing & layout
$o-spacer: 16px !default;                  // Base spacing unit
$o-horizontal-padding: $o-spacer !default;
$o-form-spacing-unit: 5px !default;

// Grays palette
$o-gray-100 through $o-gray-900 !default;  // Light → dark

// Component-specific
$o-input-padding-y: 2px !default;
$o-input-padding-x: 4px !default;
$o-dropdown-max-height: 70vh !default;
```

### 2.2 Overriding Primary Variables (Recommended Pattern)

**Step 1:** Create `_brand-override.scss` in theme module:

```scss
// Override BEFORE primary_variables loads
// Use !default so they can be overridden by actual primary_variables
$o-community-color: #2563EB !default;      // Custom blue
$o-enterprise-color: #2563EB !default;
// Automatically cascades to all $o-brand-primary dependent variables
```

**Step 2:** Load in manifest BEFORE `primary_variables.scss`:

```python
'assets': {
    'web._assets_primary_variables': [
        ('before', 'web/static/src/scss/primary_variables.scss',
         'ui_enhance_crm_sale/static/src/scss/_odoo-brand-override.scss'),
    ],
}
```

**Why:** The `!default` flag in SCSS means "assign only if variable not already defined." By loading overrides first, they take precedence.

### 2.3 SCSS Inheritance System Details

**The !default Flag:**
```scss
// In override file (loads first)
$o-brand-primary: #2563EB !default;

// In primary_variables.scss (loads second)
$o-brand-primary: $o-community-color !default;  // SKIPPED - already defined!
```

**Cascade order for theme customization:**

1. Module override (`_brand-override.scss`) → defines custom values
2. Primary variables (`primary_variables.scss`) → adds !default vars (skipped if already set)
3. Component styles (`*.scss`) → uses all variables
4. CSS custom properties → runtime theming (fallback)

### 2.4 Color Palettes & Design Tokens

**Theme colors structure:**

```scss
// In _variables.scss
$theme-primary: #2563EB;
$theme-primary-hover: #1D4ED8;
$theme-primary-light: #DBEAFE;
$theme-primary-lighter: #EFF6FF;

$theme-success: #10B981;
$theme-warning: #F59E0B;
$theme-danger: #EF4444;

// Backgrounds
$bg-primary: #F8FAFC;      // Section bg
$bg-secondary: #FFFFFF;    // Card bg
$bg-hover: #F1F5F9;        // Hover state
$bg-active: #EFF6FF;       // Active state

// Text colors
$text-primary: #1E293B;
$text-secondary: #475569;
$text-muted: #94A3B8;
$text-on-primary: #FFFFFF; // On colored backgrounds

// Borders
$border-default: #E2E8F0;
$border-light: #F1F5F9;
```

### 2.5 CSS Custom Properties (Modern Approach)

**Optional:** Define as CSS variables for runtime switching:

```scss
:root {
    --o-brand-primary: #2563EB;
    --o-brand-secondary: #3B82F6;
    --o-success: #10B981;
    --o-danger: #EF4444;
    --o-text-primary: #1E293B;
    --o-bg-primary: #F8FAFC;
}

// Usage in components
.button {
    background-color: var(--o-brand-primary);
    &:hover {
        background-color: var(--o-brand-secondary);
    }
}
```

---

## 3. WebClient Architecture (Navigation & Rendering)

### 3.1 WebClient Component Hierarchy

**Structure:**

```
WebClient
├── NavBar (top navigation)
│   ├── AppsMenu (home/apps switcher)
│   │   ├── Dropdown (desktop) or Sidebar (mobile)
│   │   └── Apps list
│   ├── MenuBrand (current app title)
│   ├── SectionsMenu (app sub-navigation)
│   │   └── Recursive nested menus
│   └── Systray (right side)
│       ├── Notifications
│       ├── User menu
│       └── Custom components
├── ActionContainer (current view/form)
└── MainComponentsContainer (dynamic components)
    └── Modals, sidebars, etc.
```

**Key file:** `web/static/src/webclient/webclient.xml`

```xml
<t t-name="web.WebClient">
    <t t-if="!state.fullscreen">
        <NavBar/>
    </t>
    <ActionContainer/>
    <MainComponentsContainer/>
</t>
```

### 3.2 NavBar Component Structure

**File:** `web/static/src/webclient/navbar/navbar.xml`

**Sections:**

1. **AppsMenu** (`o_menu_toggle` button)
   - Home icon opens apps dropdown/sidebar
   - Shows list of installed apps with icons
   - Desktop: dropdown; Mobile: sidebar
   - Hotkey: `h` (Alt+H)

2. **MenuBrand** (`o_menu_brand`)
   - Current app name/title
   - Clickable to go to app root
   - Hidden on small screens

3. **SectionsMenu** (recursive `web.SectionMenu` template)
   - Nested app sub-menus (e.g., Quotations > Draft)
   - Hidden on mobile (via `env.isSmall` check)
   - Hierarchical menu tree rendering

4. **Systray** (`o_menu_systray`)
   - Right-aligned components
   - Contains: Notifications, Messages, User menu, Clock
   - Populated from `systray` registry category
   - Order controlled by `sequence` property

### 3.3 Menu Service Architecture

**Location:** `web/static/src/webclient/menus/menu_service.js`

**Core methods:**

```javascript
// Get all apps (root menus)
menuService.getApps() → [{id, name, actionID, webIconData, ...}]

// Get currently active app
menuService.getCurrentApp() → {id, name, ...}

// Set current menu/app
menuService.setCurrentMenu(menuId)

// Get all menus (flat list)
menuService.getAll() → [{id, name, parent_id, actionID, ...}]

// Get menu by ID
menuService.getMenu(menuId)

// Navigate to menu (internal)
menuService.selectMenu(menuId)
```

### 3.4 Menu Data Model

**Odoo model:** `ir.ui.menu` (database table)

**Key fields:**

```python
class IrUiMenu(models.Model):
    _name = 'ir.ui.menu'

    name = fields.Char()
    action_id = fields.Many2one('ir.actions.actions')  # Linked action
    parent_id = fields.Many2one('ir.ui.menu')          # Parent menu
    web_icon = fields.Char()                           # Icon path (FA/OI)
    web_icon_data = fields.Char()                      # Base64 icon image
    sequence = fields.Integer()                        # Sort order
    active = fields.Boolean()
    groups_id = fields.Many2many('res.groups')         # Access control
```

**Menu hierarchy in frontend:**

- **Root (App):** parent_id = null, shown in AppsMenu
- **Section:** Has parent_id, shown in SectionsMenu
- **Action:** parent_id + actionID, triggers view

### 3.5 Customizing Navigation (Patching WebClient)

**Example: Add custom sidebar to WebClient**

```javascript
// my_module/static/src/js/webclient-patch.js
/** @odoo-module */

import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";

patch(WebClient.prototype, {
    setup() {
        super.setup(...arguments);
        this.menuService = useService("menu");
        this.sidebarState = useState({ collapsed: false });
    },

    get sidebarApps() {
        return this.menuService.getApps();
    },

    toggleSidebar() {
        this.sidebarState.collapsed = !this.sidebarState.collapsed;
    },
});
```

**Manifest:**

```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/js/webclient-patch.js',
        'my_module/static/src/xml/sidebar-template.xml',
    ],
}
```

---

## 4. OWL Component Patching & Extension

### 4.1 Patching Fundamentals

**Import:** `import { patch } from "@web/core/utils/patch"`

**Pattern:**

```javascript
import { SomeComponent } from "@web/path/to/component";
import { patch } from "@web/core/utils/patch";

patch(SomeComponent.prototype, {
    // Add/override methods
    myMethod() {
        // Custom logic
    },

    // Override setup for hooks
    setup() {
        super.setup(...arguments);
        // Add additional hooks
    },
});
```

### 4.2 Patching Classes vs Components

**Regular class:**
```javascript
patch(MyClass, {
    myMethod() { /* ... */ }
});

// Unpatch if needed
const unpatch = patch(MyClass, { /* ... */ });
unpatch();
```

**OWL Component (preferred):**
```javascript
patch(MyComponent.prototype, {
    setup() {
        super.setup(...arguments);
        // Hooks MUST go in setup() for proper Owl lifecycle
        const service = useService("my_service");
        const state = useState({ count: 0 });
    },

    onButtonClick() {
        // Method override
    },
});
```

### 4.3 Patching Common Web Client Components

**NavBar:**
```javascript
import { NavBar } from "@web/webclient/navbar/navbar";
import { patch } from "@web/core/utils/patch";

patch(NavBar.prototype, {
    setup() {
        super.setup(...arguments);
        // Add custom logic to navbar
    },

    onCustomAction() {
        // Custom navbar action
    },
});
```

**WebClient:**
```javascript
import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";

patch(WebClient.prototype, {
    setup() {
        super.setup(...arguments);
        this.customService = useService("custom_service");
    },
});
```

**ActionContainer, MainComponentsContainer:** Similar pattern.

### 4.4 Patch File Organization

**Convention:**
```
my_module/static/src/js/
├── patches/
│   ├── webclient-patch.js
│   ├── navbar-patch.js
│   ├── form-patch.js
│   └── kanban-patch.js
└── main.js (imports all patches)
```

**Manifest:**
```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/js/patches/webclient-patch.js',
        'my_module/static/src/js/patches/navbar-patch.js',
        # ... other patches
    ],
}
```

**or use wildcard:**
```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/js/patches/*.js',
    ],
}
```

---

## 5. Menu System & Customization

### 5.1 Menu Declaration (XML)

**Standard menuitem syntax:**

```xml
<!-- In data/menus.xml -->
<odoo>
    <!-- Root app menu -->
    <menuitem id="menu_my_app" name="My App" sequence="1" />

    <!-- Sections -->
    <menuitem id="menu_section1" name="Section 1" parent="menu_my_app" sequence="10" />
    <menuitem id="menu_section2" name="Section 2" parent="menu_my_app" sequence="20" />

    <!-- Actions (leaves) -->
    <menuitem id="menu_list_view" name="List"
              parent="menu_section1"
              action="action_my_model_list"
              sequence="1"/>

    <menuitem id="menu_form_view" name="Forms"
              parent="menu_section1"
              action="action_my_model_form"
              sequence="2"/>
</odoo>
```

### 5.2 Menu Icons

**Icon types:**

1. **Font Awesome:** `web_icon="fa-icon-name"` (v6+)
   ```xml
   <menuitem ... web_icon="fa-cogs" />
   ```

2. **Odoo Icons:** `web_icon="oi oi-icon-name"`
   ```xml
   <menuitem ... web_icon="oi oi-folder" />
   ```

3. **Image/base64:** `web_icon_data="data:image/png;base64,..."` (stored in DB)

4. **Module icon:** `static/description/icon.png` (shown in app switcher)

**How app icons load:**

- Read from `module/static/description/icon.png`
- Converted to base64 and stored in `ir.ui.menu.web_icon_data`
- Rendered in AppsMenu with `<img src="data:image/png;base64,..." />`

### 5.3 Customizing Menu Structure

**Add sections via inherited XML:**

```xml
<!-- my_module/data/menus_inherit.xml -->
<odoo>
    <!-- Insert new section after CRM menu -->
    <menuitem id="menu_custom_analytics" name="Analytics"
              parent="crm.menu_crm_opportunities"
              sequence="100"
              action="action_custom_analytics"
              web_icon="oi oi-chart-line" />
</odoo>
```

**Hide menu items:**

```python
# In models/ir_ui_menu.py
from odoo import models

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    def _get_menus(self, debug):
        # Called to filter visible menus
        menus = super()._get_menus(debug)
        # Hide certain menus based on logic
        return menus.filtered(lambda m: m.id != self.env.ref('my_module.menu_to_hide').id)
```

### 5.4 Mobile vs Desktop Navigation

**Responsive detection in components:**

```javascript
// In NavBar or custom component
import { useEnv } from "@odoo/owl";

setup() {
    const env = useEnv();

    // env.isSmall = true if viewport < 768px
    if (env.isSmall) {
        // Mobile: show sidebar (BurgerMenu)
        // Desktop: show navbar sections
    }
}
```

**NavBar adjusts:**
- Desktop: Apps dropdown + Sections menu + Systray
- Mobile: Burger menu (sidebar) + Systray only

---

## 6. Module Icons & Branding

### 6.1 App Icon in Manifest

**Not directly in manifest**, but:

```python
{
    'name': 'My Module',
    'icon': 'my_module/static/description/icon.png',  # Not standard Odoo 18
    # Instead, Odoo reads: my_module/static/description/icon.png
}
```

**File must exist:** `my_module/static/description/icon.png` (64x64 or 256x256)

**Odoo process:**
1. Scans module directory for `icon.png`
2. Converts to base64
3. Stores in `ir.ui.menu.web_icon_data`
4. Renders in AppsMenu as `<img />`

### 6.2 Custom App Icons via Patches

```javascript
// Customize how icons load
import { NavBar } from "@web/webclient/navbar/navbar";
import { patch } from "@web/core/utils/patch";

patch(NavBar.prototype, {
    getAppIconUrl(app) {
        // Custom icon URL generation
        if (app.id === MY_APP_ID) {
            return '/my_module/static/images/custom-icon.svg';
        }
        return super.getAppIconUrl(app);
    },
});
```

---

## 7. Configuration via res.config.settings

### 7.1 Adding Theme Settings

**Model inheritance:**

```python
# my_module/models/res_config_settings.py
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Theme color settings
    theme_primary_color = fields.Char(
        'Primary Color',
        config_parameter='my_module.theme_primary_color',
        default='#2563EB'
    )

    theme_sidebar_width = fields.Integer(
        'Sidebar Width (px)',
        config_parameter='my_module.sidebar_width',
        default=210
    )

    sidebar_collapsed_by_default = fields.Boolean(
        'Collapse Sidebar by Default',
        config_parameter='my_module.sidebar_collapsed_default',
        default=False
    )

    use_dark_mode = fields.Boolean(
        'Dark Mode',
        config_parameter='my_module.use_dark_mode',
        default=False
    )
```

### 7.2 Settings View (Settings form)

```xml
<!-- my_module/views/res_config_settings_views.xml -->
<odoo>
    <record id="res_config_settings_form_inherit" model="ir.ui.view">
        <field name="name">Settings Form - Theme Tab</field>
        <field name="model">res.config.settings</field>
        <field name="inherit_id" ref="base.res_config_settings_view_form"/>
        <field name="arch" type="xml">
            <xpath expr="//page[@string='General Settings']" position="after">
                <page string="Theme" name="theme">
                    <group>
                        <group string="Colors">
                            <field name="theme_primary_color" widget="color" />
                        </group>
                        <group string="Layout">
                            <field name="theme_sidebar_width" />
                            <field name="sidebar_collapsed_by_default" />
                        </group>
                        <group string="Appearance">
                            <field name="use_dark_mode" />
                        </group>
                    </group>
                </page>
            </xpath>
        </field>
    </record>
</odoo>
```

### 7.3 Using Config Settings in Frontend

**Fetch at runtime:**

```javascript
import { useService } from "@web/core/utils/hooks";

setup() {
    const rpc = useService("rpc");

    onMounted(async () => {
        const settings = await rpc('/web/session/get_web_client_data');
        const primaryColor = settings.theme_primary_color;
        // Apply dynamically
        document.documentElement.style.setProperty('--theme-primary', primaryColor);
    });
}
```

**Alternative: Store in localStorage & sync on save:**

```python
# Model method to broadcast setting change
def set_values(self):
    super().set_values()
    self.env['bus.bus']._sendone(
        self.env.user.partner_id,
        'config_settings_updated',
        {
            'theme_primary_color': self.theme_primary_color,
        }
    )
```

---

## 8. Real-World Pattern: Complete Theme Module

### 8.1 Module Structure

```
ui_enhance_crm_sale/
├── __manifest__.py
├── __init__.py
├── models/
│   └── res_config_settings.py
├── views/
│   ├── res_config_settings_views.xml
│   ├── crm_lead_views_inherit.xml
│   └── sale_order_views_inherit.xml
├── static/
│   └── src/
│       ├── scss/
│       │   ├── _variables.scss          # Design tokens
│       │   ├── _mixins.scss             # Utilities
│       │   ├── _odoo-brand-override.scss # Primary color override
│       │   ├── vertical-sidebar-enhance.scss
│       │   ├── common-enhance.scss
│       │   ├── crm-form-enhance.scss
│       │   ├── crm-kanban-enhance.scss
│       │   ├── sale-form-enhance.scss
│       │   └── sale-kanban-enhance.scss
│       ├── js/
│       │   ├── vertical-sidebar-webclient-patch.js
│       │   ├── form-save-feedback-patch.js
│       │   └── patches/
│       │       └── *.js
│       └── xml/
│           ├── vertical-sidebar-template.xml
│           └── *.xml
└── data/
    └── project-scrum-demo.xml

```

### 8.2 Manifest Example (ui_enhance_crm_sale)

```python
{
    'name': 'CRM & Sale UI Enhancement',
    'version': '18.0.3.0.0',
    'category': 'Sales',
    'summary': 'Tableau-style UI with vertical sidebar',
    'description': """
        Enhances CRM/Sale with:
        - Vertical sidebar with app icons
        - Custom color palette (#2563EB primary)
        - Form & Kanban enhancements
    """,
    'depends': ['crm', 'sale', 'web'],
    'data': [
        'views/crm-lead-views-inherit.xml',
        'views/sale-order-views-inherit.xml',
    ],
    'assets': {
        # CRITICAL: Load brand override BEFORE primary_variables
        'web._assets_primary_variables': [
            ('before', 'web/static/src/scss/primary_variables.scss',
             'ui_enhance_crm_sale/static/src/scss/_odoo-brand-override.scss'),
        ],

        # Backend assets (in order)
        'web.assets_backend': [
            # Variables & mixins first
            'ui_enhance_crm_sale/static/src/scss/_variables.scss',
            'ui_enhance_crm_sale/static/src/scss/_mixins.scss',

            # Layout (grid, sidebar)
            'ui_enhance_crm_sale/static/src/scss/vertical-sidebar-enhance.scss',

            # Component styles
            'ui_enhance_crm_sale/static/src/scss/common-enhance.scss',
            'ui_enhance_crm_sale/static/src/scss/crm-form-enhance.scss',
            'ui_enhance_crm_sale/static/src/scss/crm-kanban-enhance.scss',
            'ui_enhance_crm_sale/static/src/scss/sale-form-enhance.scss',
            'ui_enhance_crm_sale/static/src/scss/sale-kanban-enhance.scss',

            # JS patches
            'ui_enhance_crm_sale/static/src/js/vertical-sidebar-webclient-patch.js',
            'ui_enhance_crm_sale/static/src/js/form-save-feedback-patch.js',

            # XML templates
            'ui_enhance_crm_sale/static/src/xml/vertical-sidebar-template.xml',
        ],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
```

### 8.3 Key Implementation Details

**Brand override (_odoo-brand-override.scss):**
- Loaded in `_assets_primary_variables` BEFORE `primary_variables.scss`
- Sets `$o-community-color: #2563EB !default`
- Cascades to all dependent vars: buttons, links, form borders, focus rings, badges

**Sidebar patch (vertical-sidebar-webclient-patch.js):**
- Extends WebClient.prototype
- Adds sidebar state (collapsed/expanded)
- Exposes `sidebarApps`, `currentApp`, `toggleSidebar()` methods
- Used by `vertical-sidebar-template.xml` to render custom sidebar

**Layout SCSS (vertical-sidebar-enhance.scss):**
- Uses CSS Grid: `grid-template-columns: sidebar-width 1fr`
- Positions: sidebar (col 1), navbar (col 2, row 1), action (col 2, row 2)
- Responsive: collapses sidebar width at small breakpoints

---

## 9. Best Practices & Patterns

### 9.1 Asset Organization

**DO:**
- Organize SCSS by concern (variables, layout, components)
- Load overrides BEFORE target files (use `before` directive)
- Use `!default` flag for all SCSS variables
- Document asset loading order in comments

**DON'T:**
- Load CSS/SCSS out of order (breaks variable cascade)
- Directly modify Odoo core files (use inheritance/patching)
- Mix CSS custom properties with SCSS variables (use one approach)
- Load large JS bundles synchronously (lazy-load non-critical code)

### 9.2 SCSS Theming

**DO:**
- Define all theme colors as top-level variables
- Use mixins for repeated patterns
- Leverage `!default` for overridability
- Create separate `_variables.scss` file per theme module

**DON'T:**
- Use hardcoded colors in component SCSS (use variables)
- Nest variables too deep (breaks readability)
- Override variables multiple times (confusing cascade)

### 9.3 Component Patching

**DO:**
- Patch only what you need (minimal modifications)
- Call `super.setup()` to preserve parent behavior
- Use hooks (useState, useService) in `setup()` method only
- Test patches against different Odoo versions

**DON'T:**
- Replace entire methods if you just need to extend
- Assume method signatures won't change
- Create cyclical patch dependencies
- Patch internal/private methods (prefixed `_`)

### 9.4 Menu Customization

**DO:**
- Inherit XML menus rather than creating new structure
- Use `sequence` to control menu order
- Add `groups_id` for role-based visibility
- Provide icons (FA/OI) for better UX

**DON'T:**
- Create deep menu hierarchies (>3 levels confusing)
- Change parent menu IDs (breaks existing references)
- Hide menus via CSS (use `active=False` in DB)

---

## 10. Unresolved Questions & Gaps

1. **Runtime theme switching:** How to toggle dark mode without page reload? (Likely via CSS custom properties + localStorage, but no direct Odoo 18 docs found)

2. **Mobile menu customization:** Exact BurgerMenu component structure not deeply explored. Is it directly patchable or does it have a registry system?

3. **Asset versioning:** How does Odoo handle cache busting for theme assets during development? (Likely via asset bundles, but not confirmed)

4. **Multi-theme support:** Can multiple theme modules coexist without conflicts? (Should work via asset bundle ordering, but edge cases unclear)

5. **Module icon SVG support:** Does Odoo 18 prefer PNG or SVG icons? (PNG documented, SVG support unclear)

6. **Systray registry extension:** Can custom components be added to systray registry, and what's the exact pattern?

7. **Portal theme:** Can backend theme also style portal/website, or are they separate systems? (Likely separate, but integration points unclear)

---

## 11. Key Sources & References

| Topic | Source | Relevance |
|---|---|---|
| Assets & Bundles | [Odoo 18 Assets Documentation](https://www.odoo.com/documentation/18.0/developer/reference/frontend/assets.html) | ⭐⭐⭐⭐⭐ Complete coverage |
| SCSS Inheritance | [SCSS Inheritance Guide](https://www.odoo.com/documentation/18.0/developer/reference/user_interface/scss_inheritance.html) | ⭐⭐⭐⭐⭐ Critical |
| Patching Code | [Patching Code Documentation](https://www.odoo.com/documentation/18.0/developer/reference/frontend/patching_code.html) | ⭐⭐⭐⭐⭐ Essential |
| Menu Architecture | [Menu System Docs](https://www.odoo.com/documentation/18.0/developer/tutorials/web.html) | ⭐⭐⭐⭐ Good coverage |
| WebClient Customization | [Web Client Tutorial](https://www.odoo.com/documentation/18.0/developer/tutorials/web.html) | ⭐⭐⭐⭐ Complete |
| OWL Components | [OWL Framework (GitHub)](https://github.com/odoo/owl) | ⭐⭐⭐⭐ Reference |
| Theme Modules | [MuK Backend Theme (Apps Store)](https://apps.odoo.com/apps/themes/18.0/muk_web_theme) | ⭐⭐⭐⭐ Real-world example |
| Odoo Core Source | `addons/web/static/src/` | ⭐⭐⭐⭐⭐ Authoritative |

---

## 12. Next Steps for Implementation

**Phase 1: Foundation (Research → Planning)**
- [ ] Analyze existing `ui_enhance_crm_sale` module structure
- [ ] Document custom color palette & design tokens
- [ ] Identify all components to customize (forms, kanban, list, navbar)
- [ ] Map SCSS variable dependencies

**Phase 2: Core Styling**
- [ ] Create `_variables.scss` with design tokens
- [ ] Create `_odoo-brand-override.scss` for primary color override
- [ ] Verify asset load order (brand override BEFORE primary_variables)
- [ ] Test color cascade across all components

**Phase 3: Layout & Navigation**
- [ ] Implement vertical sidebar via WebClient patch
- [ ] Create sidebar template (`sidebar-template.xml`)
- [ ] Customize navbar sections menu
- [ ] Add sidebar collapse/expand toggle

**Phase 4: Component Enhancements**
- [ ] Style forms, kanban, list views per design
- [ ] Add form field enhancements
- [ ] Customize modal/dialog styling
- [ ] Ensure responsive breakpoints

**Phase 5: Configuration & Settings**
- [ ] Add theme configuration model (res.config.settings)
- [ ] Create settings view with theme options
- [ ] Implement color picker widget
- [ ] Test setting persistence

**Phase 6: Testing & Documentation**
- [ ] Test across browsers (Chrome, Firefox, Safari, Edge)
- [ ] Test responsive (mobile, tablet, desktop)
- [ ] Document asset loading order
- [ ] Create developer guide for extending theme

---

## Summary

Odoo 18 provides **4 primary mechanisms** for backend theming:

1. **Asset Bundles:** `__manifest__.py` assets key controls JS/SCSS/XML loading order
2. **SCSS Variables:** `primary_variables.scss` + `!default` flag enable cascading overrides
3. **OWL Patching:** `@web/core/utils/patch` extends components without source modification
4. **Configuration:** `res.config.settings` transient model integrates user-configurable theme options

The **recommended pattern** for a new theme module:

```
✅ Create _odoo-brand-override.scss → Load in _assets_primary_variables BEFORE primary_variables
✅ Create _variables.scss with design tokens → Load in web.assets_backend
✅ Create component-specific SCSS files → Load in order (layout → base → components)
✅ Create WebClient/NavBar patches → Customize navigation structure
✅ Create res.config.settings model → Allow user theme configuration
✅ Document asset loading order in manifest comments
```

This approach maintains **backward compatibility**, **modularity**, and **maintainability** while enabling **full UI customization**.


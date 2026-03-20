# Phase 6: Sidebar & Navbar Styling

## Overview
- **Priority:** P1 (high visual impact)
- **Status:** pending
- **File:** `addons/ui_enhance_crm_sale/static/src/scss/common-enhance.scss` (append new section)

## Key Insights
- Odoo 18/19 sidebar uses `.o_main_navbar` for top bar and `.o_action_manager` for content
- The left sidebar/app switcher uses `.o_navbar_apps_menu` or `.o_web_client .o_action_manager`
- Need to verify exact selectors in Odoo 18 community edition
- **Important:** Odoo 18 has a vertical sidebar by default (`.o_main_navbar` is already vertical in some configurations)

## Odoo 18 Sidebar Selectors to Target
```
.o_web_client .o_main_navbar          // Top navigation bar
.o_web_client .o_navbar_apps_menu     // App switcher sidebar
.o_web_client .o_menu_brand           // Brand/logo area
.o_web_client .o_menu_sections        // Menu sections
```

**CRITICAL:** Before implementing, developer MUST inspect the actual DOM of the running Odoo instance to confirm selector names. Odoo 18 may use different class names than expected.

## Changes Required

### Top Navbar
```scss
// Top navbar - clean white background
.o_web_client .o_main_navbar {
    background-color: $ui-enhance-navbar-bg;
    border-bottom: 1px solid $ui-enhance-navbar-border;
    box-shadow: none;  // Remove any existing shadow

    // Brand area
    .o_menu_brand {
        color: $ui-enhance-text-primary;
        font-weight: $ui-enhance-font-weight-semibold;
    }

    // "New" button - rounded solid blue
    .o_menu_sections .btn-primary,
    .o-kanban-button-new {
        border-radius: $ui-enhance-radius-pill;
        background-color: $ui-enhance-primary;
        border-color: $ui-enhance-primary;
        font-weight: $ui-enhance-font-weight-medium;
        padding: 6px 20px;
    }
}
```

### Left Sidebar (App Switcher)
```scss
// Dark navy sidebar
.o_web_client .o_navbar_apps_menu,
.o_web_client .o_action_manager .o_cp_switch_buttons {
    // Target the actual sidebar container - verify selector
    background-color: $ui-enhance-sidebar-bg;

    // Menu items
    .o_nav_entry, .dropdown-item {
        color: $ui-enhance-sidebar-text;

        &:hover {
            background-color: $ui-enhance-sidebar-bg-hover;
        }

        &.active {
            background-color: $ui-enhance-sidebar-active-bg;
            font-weight: $ui-enhance-font-weight-semibold;
        }
    }
}
```

## Risk Assessment
- **HIGH RISK:** Odoo sidebar selectors vary between versions and Community vs Enterprise
- **Mitigation:** Use broad selectors with `!important` sparingly, test against running instance
- **Fallback:** If selectors don't match, this phase can be deferred without breaking other phases

## Pre-Implementation Checklist
- [ ] Developer inspects running Odoo DOM for exact sidebar/navbar class names
- [ ] Document actual selectors found
- [ ] Implement only confirmed selectors

## Todo List
- [ ] Inspect running Odoo instance for navbar/sidebar DOM structure
- [ ] Add navbar white background + border styles
- [ ] Add sidebar dark navy background styles
- [ ] Add menu item hover/active states
- [ ] Test that styles don't break other Odoo views
- [ ] Verify common-enhance.scss stays under 200 lines (if not, extract to separate file)

## File Size Consideration
If adding sidebar/navbar section pushes `common-enhance.scss` over 200 lines:
- Extract sidebar/navbar styles to new file `sidebar-navbar-enhance.scss`
- Register in `__manifest__.py` assets
- This is the ONLY acceptable new file creation

## Success Criteria
- Top navbar has clean white background
- Sidebar has dark navy background (if selectors confirmed)
- Menu items properly styled with hover/active states
- No regressions in other views

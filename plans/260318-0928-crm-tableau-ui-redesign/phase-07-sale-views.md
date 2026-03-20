# Phase 7: Sale View Styles

## Overview
- **Priority:** P3
- **Status:** pending
- **Files:**
  - `addons/ui_enhance_crm_sale/static/src/scss/sale-form-enhance.scss` (186 lines)
  - `addons/ui_enhance_crm_sale/static/src/scss/sale-kanban-enhance.scss` (88 lines)

## Key Insights
- Sale views should follow same flattening treatment as CRM
- Most changes are auto-resolved by Phase 1 token updates
- Need to remove hover shadows on buttons and reduce visual intensity

## Changes Required

### sale-form-enhance.scss

**Button Hover Shadows** (multiple locations):
- Replace all `box-shadow: 0 2px 8px rgba(...)` with `$ui-enhance-shadow-sm`
- Affects: cancel button, confirm button (lines 36, 55)

**Accent Border** (line 64):
- `@include ui-enhance-accent-border` is now empty (Phase 2), auto-resolved

**Selected Row** (line 121):
- Keep `inset 3px 0 0 $ui-enhance-primary` left highlight for selected editable row (this is functional, not decorative)

**Row Hover** (line 113):
- Keep light blue tint on hover, auto-muted via new token values

### sale-kanban-enhance.scss

- Most styles are scoped under `.ui-enhance-kanban` which is already flattened in Phase 3
- Card-specific overrides (partner name, monetary, footer) - auto-resolved via tokens
- No additional changes needed beyond token cascading

## Todo List
- [ ] Replace explicit `box-shadow: 0 2px 8px` with `$ui-enhance-shadow-sm` in sale-form
- [ ] Verify accent-border removal cascades correctly
- [ ] Verify sale-kanban styles cascade correctly from token + common changes
- [ ] Test both sale form and kanban views compile

## Success Criteria
- Sale views match flattened corporate style
- No hover shadows on buttons
- Files still under 200 lines

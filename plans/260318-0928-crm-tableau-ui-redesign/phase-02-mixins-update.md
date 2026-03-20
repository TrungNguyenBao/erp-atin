# Phase 2: Mixins Update

## Overview
- **Priority:** P1 (used by all component files)
- **Status:** pending
- **File:** `addons/ui_enhance_crm_sale/static/src/scss/_mixins.scss`

## Key Insights
- `ui-enhance-card-hover` currently applies `translateY(-2px)` and blue-tinted shadow - must remove
- `ui-enhance-accent-border` adds left border - screenshot shows NO left accent borders on cards
- `ui-enhance-fade-in` animation too playful for corporate style - remove or simplify
- Badge mixin is fine, keep as-is

## Changes Required

### `ui-enhance-card-hover` -> Flatten
```scss
// Remove transform: translateY(-2px) on hover
// Remove blue-tinted shadow-hover
// Keep subtle border-color change on hover only
@mixin ui-enhance-card-hover {
    border-radius: $ui-enhance-radius-md;
    box-shadow: $ui-enhance-shadow-card;
    transition: border-color $ui-enhance-transition-fast;

    &:hover {
        border-color: darken($ui-enhance-border, 8%);
        // NO transform, NO shadow change
    }
}
```

### `ui-enhance-accent-border` -> Remove or No-op
Cards in screenshot have NO left accent borders. Two options:
- **Option A:** Empty the mixin body (safe, no breaking changes)
- **Option B:** Keep mixin but use for form sections only, not cards

Recommend **Option A** - empty it, then remove usage from card styles in phase 4.

### `ui-enhance-fade-in` -> Remove animation
```scss
// Replace with no-op or simple opacity-only fade
@mixin ui-enhance-fade-in($duration: 0.15s) {
    // Removed: no entry animation in flat corporate style
}
```
Remove the `@keyframes uiEnhanceFadeIn` block.

### `ui-enhance-focus-ring` -> Simplify
```scss
@mixin ui-enhance-focus-ring {
    &:focus-within {
        outline: none;
        box-shadow: 0 0 0 2px rgba($ui-enhance-primary, 0.15);
    }
}
```

### Keep unchanged
- `ui-enhance-section-header` - still useful
- `ui-enhance-btn-group` - layout helper, fine
- `ui-enhance-truncate` - utility, fine
- `ui-enhance-badge` - keep
- `ui-enhance-form-section` - keep
- `ui-enhance-block` - keep

## Todo List
- [ ] Flatten `ui-enhance-card-hover` (remove transform, reduce shadow)
- [ ] Empty `ui-enhance-accent-border` body
- [ ] Remove fade-in animation keyframes and mixin body
- [ ] Simplify focus-ring to single ring
- [ ] Verify file compiles and stays under 200 lines

## Success Criteria
- No hover lift/transform on any card
- No entry animations on cards
- All files using these mixins still compile

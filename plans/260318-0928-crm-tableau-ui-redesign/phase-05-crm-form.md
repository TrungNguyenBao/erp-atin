# Phase 5: CRM Form Styles

## Overview
- **Priority:** P2
- **Status:** pending
- **File:** `addons/ui_enhance_crm_sale/static/src/scss/crm-form-enhance.scss`
- **Current size:** 147 lines

## Changes Required

### Revenue Section (lines 18-39)
- Keep block-style grouping but use muted colors from new palette
- Auto-resolved via token changes in Phase 1

### Won/Lost Buttons (lines 42-67)
- Keep functional but reduce hover shadow intensity
- Change `box-shadow: 0 2px 8px rgba(...)` to `$ui-enhance-shadow-sm`

### Form Groups - Remove Accent Border (lines 83-92)
```scss
// The @include ui-enhance-accent-border usage here:
// After Phase 2, the mixin is empty, so this is a no-op
// Optionally remove the include call for clarity
```

### Priority Stars (lines 95-105)
- Remove hover `transform: scale(1.1)` - too playful
- Keep color transitions

### Tags (lines 129-134)
- Keep pill badges, auto-updated via tokens

## Todo List
- [ ] Reduce button hover shadows to $ui-enhance-shadow-sm
- [ ] Remove priority star scale transform on hover
- [ ] Clean up accent-border include calls (now no-op)
- [ ] Verify colors cascade correctly from new tokens

## Success Criteria
- Form maintains clean corporate look
- No playful hover animations
- File under 200 lines

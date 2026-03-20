# Phase 3: Common Styles Update

## Overview
- **Priority:** P2
- **Status:** pending
- **File:** `addons/ui_enhance_crm_sale/static/src/scss/common-enhance.scss`

## Key Insights
- File currently 288 lines - already near limit, keep concise
- Contains form, list, and kanban shared styles
- Main changes: reduce visual intensity, flatten interactions
- Kanban card hover in `.ui-enhance-kanban .o_kanban_record` must lose transform

## Changes Required

### Form Sheet (lines 7-13)
- Reduce shadow: use `$ui-enhance-shadow-sm` (already flattened in phase 1)
- OK as-is after token changes

### Notebook Tabs (lines 16-47)
- Remove hover background color change (`background: $ui-enhance-primary-lighter`)
- Keep active state but make subtler
- Remove border-radius on individual tabs for cleaner look

### Stat Buttons (lines 50-78)
- Remove hover shadow on stat buttons
- Keep hover background tint but use lighter value

### Animations Section (lines 148-181)
- Remove or simplify `uiEnhanceSavedFlash` keyframes
- Remove `uiEnhanceHighlightPulse` keyframes
- Replace with minimal opacity transitions if needed

### Kanban Shared `.ui-enhance-kanban` (lines 233-287)
**Critical changes:**
```scss
.o_kanban_record {
    // REMOVE: transform: translateY(-2px) on hover
    // REMOVE: box-shadow: $ui-enhance-shadow-hover on hover
    // REMOVE: border-color: $ui-enhance-secondary-light on hover
    // KEEP: subtle border, flat card
    &:hover {
        border-color: darken($ui-enhance-border, 8%);
    }
}
```

### Progress Bar (lines 275-286)
- Increase height from 6px to 8px for more prominence (screenshot shows thicker bars)
- Keep pill radius

### Quick Create (lines 262-272)
- Reduce focus shadow intensity

## Todo List
- [ ] Flatten kanban card hover (remove transform + shadow)
- [ ] Remove/simplify animation keyframes
- [ ] Tone down tab hover effects
- [ ] Increase progress bar height
- [ ] Reduce stat button hover shadow
- [ ] Verify file stays under 200 lines (may need to trim animation section)

## Success Criteria
- Cards hover with border-color change only, no lift
- No playful animations remain
- Progress bars more prominent
- File under 200 lines

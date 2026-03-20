# Phase 4: CRM Kanban Styles

## Overview
- **Priority:** P1 (most visible change)
- **Status:** pending
- **File:** `addons/ui_enhance_crm_sale/static/src/scss/crm-kanban-enhance.scss`
- **Current size:** 127 lines

## Key Insights from Screenshot

### Cards should be:
- Clean white with subtle border (no heavy shadow)
- NO left accent border (currently has `border-left: 3px solid transparent` + blue on hover)
- NO hover elevation/transform
- Flat design with good whitespace

### Column headers should have:
- Clean title text
- Colored progress bars under headers (green/gray/orange/red per stage)
- Dollar amounts next to bars

### Card content layout (top to bottom):
1. Lead name (bold, dark)
2. Revenue amount
3. Company icon + name
4. Colored tag badges (pills)
5. Footer: priority stars | activity icons | user avatar

## Changes Required

### Remove Left Accent Border (line 11-16)
```scss
// DELETE entirely:
border-left: 3px solid transparent;
&:hover { border-left-color: $ui-enhance-primary; }
```

### Remove Fade-in Animation (line 10)
```scss
// DELETE: @include ui-enhance-fade-in(0.25s);
```

### Revenue Display (lines 28-35)
- Keep green color for monetary but use slightly muted green
- Keep tabular-nums

### Tags (lines 52-61)
- Already pill-shaped, keep
- Ensure padding matches screenshot (`3px 10px`)

### Footer (lines 65-81)
- Keep footer separator line
- Avatar border: change from primary-light blue to neutral gray

```scss
.o_m2o_avatar > img,
.o_field_many2one_avatar img {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 2px solid $ui-enhance-border;  // was primary-light
}
```

### Column Header (lines 89-105)
- Change bottom border from primary-light to stage-aware colors
- This is tricky in pure CSS - Odoo kanban columns don't have stage-specific classes by default
- **Approach:** Style the existing `.o_kanban_counter_progress .progress-bar` which already has Odoo's built-in colors based on stage configuration

```scss
.o_kanban_header {
    padding-bottom: $ui-enhance-space-sm;
    border-bottom: 2px solid $ui-enhance-border;  // neutral, not blue
    margin-bottom: $ui-enhance-space-sm;
}
```

### Progress Bar (lines 116-126)
- Make progress bar more prominent (height 8px)
- Let Odoo's native stage colors show through (don't override to primary blue)
- Style the counter side value

```scss
.o_kanban_counter {
    .o_kanban_counter_progress .progress {
        height: 8px;
        border-radius: $ui-enhance-radius-pill;

        .progress-bar {
            border-radius: $ui-enhance-radius-pill;
            // REMOVE: background-color override
            // Let Odoo's native success/danger/warning colors show
        }
    }

    .o_kanban_counter_side {
        font-weight: $ui-enhance-font-weight-bold;
        color: $ui-enhance-text-primary;  // was primary blue
        font-size: 0.85rem;
    }
}
```

### Drag State (lines 108-113)
- Remove rotate transform, keep opacity + shadow only

```scss
.o_kanban_record.o_dragged {
    opacity: 0.7;
    box-shadow: $ui-enhance-shadow-md;
    // REMOVE: transform: rotate(2deg)
    // REMOVE: border-left-color
}
```

## Todo List
- [ ] Remove `border-left: 3px solid transparent` and hover left-border
- [ ] Remove `@include ui-enhance-fade-in`
- [ ] Remove hover transform/shadow from card (already in common, but verify no override here)
- [ ] Change avatar border from blue to neutral
- [ ] Change column header border from blue to neutral
- [ ] Remove progress-bar background-color override (let Odoo native colors show)
- [ ] Increase progress bar height to 8px
- [ ] Change counter side text from blue to neutral dark
- [ ] Simplify drag state (remove rotate)
- [ ] Verify file compiles

## Success Criteria
- Cards: flat, no left border, no hover lift
- Progress bars: show native Odoo stage colors, 8px height
- Column headers: clean neutral border
- Avatars: neutral border ring
- File under 200 lines

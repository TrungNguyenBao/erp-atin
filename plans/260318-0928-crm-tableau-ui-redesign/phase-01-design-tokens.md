# Phase 1: Design Tokens Update

## Overview
- **Priority:** P1 (foundation for all other phases)
- **Status:** pending
- **File:** `addons/ui_enhance_crm_sale/static/src/scss/_variables.scss`

## Key Insights
- Current palette centered on Trust Blue #2563EB - too vibrant for Tableau style
- Tableau uses darker, more muted blues and a navy sidebar
- Shadows are currently too prominent; need flattening
- Transitions/animations should be reduced or removed

## Changes Required

### Color Palette
Replace vibrant blue with Tableau-style muted corporate palette:

```scss
// OLD -> NEW
$ui-enhance-primary: #2563EB -> #2B5797  // Muted corporate blue (Tableau-like)
$ui-enhance-primary-hover: #1D4ED8 -> #1E3F6F
$ui-enhance-primary-light: #DBEAFE -> #E8EEF5
$ui-enhance-primary-lighter: #EFF6FF -> #F4F7FA

$ui-enhance-secondary: #3B82F6 -> #4A90C4  // Softer secondary
$ui-enhance-secondary-light: #BFDBFE -> #C8DDF0
```

### NEW: Sidebar/Navbar tokens
Add new variables for dark sidebar:

```scss
// --- Sidebar (Tableau dark navy) ---
$ui-enhance-sidebar-bg: #1B2559;
$ui-enhance-sidebar-bg-hover: #243073;
$ui-enhance-sidebar-text: #FFFFFF;
$ui-enhance-sidebar-text-muted: rgba(255, 255, 255, 0.6);
$ui-enhance-sidebar-active-bg: rgba(255, 255, 255, 0.1);

// --- Navbar ---
$ui-enhance-navbar-bg: #FFFFFF;
$ui-enhance-navbar-border: #E5E7EB;
```

### Shadows - Flatten
Reduce all shadows to near-flat:

```scss
// OLD -> NEW
$ui-enhance-shadow-sm: ... -> 0 1px 2px rgba(0, 0, 0, 0.04);
$ui-enhance-shadow-md: ... -> 0 1px 3px rgba(0, 0, 0, 0.06);
$ui-enhance-shadow-lg: ... -> 0 2px 6px rgba(0, 0, 0, 0.08);
$ui-enhance-shadow-hover: ... -> 0 1px 3px rgba(0, 0, 0, 0.08);  // NO blue tint
$ui-enhance-shadow-card: ... -> 0 1px 2px rgba(0, 0, 0, 0.03);
```

### Transitions - Reduce
```scss
$ui-enhance-transition-fast: 0.15s ease;   // keep
$ui-enhance-transition-base: 0.15s ease;   // was 0.2s, reduce
$ui-enhance-transition-slow: 0.2s ease;    // was 0.3s ease-in-out, simplify
```

### Border Radius - Slightly less rounded
```scss
$ui-enhance-radius-sm: 4px;    // was 6px
$ui-enhance-radius-md: 8px;    // was 10px
$ui-enhance-radius-lg: 12px;   // was 14px
$ui-enhance-radius-pill: 50px; // keep
```

### Progress Bar Colors (NEW)
```scss
// --- Kanban Progress Bar Stage Colors ---
$ui-enhance-stage-new: #22C55E;       // Green
$ui-enhance-stage-qualified: #94A3B8; // Gray
$ui-enhance-stage-proposal: #F97316;  // Orange
$ui-enhance-stage-won: #EF4444;       // Red
```

## Todo List
- [ ] Update primary color palette to muted corporate blue
- [ ] Add sidebar/navbar color tokens
- [ ] Flatten all shadow values
- [ ] Reduce transition durations
- [ ] Slightly reduce border-radius values
- [ ] Add progress bar stage color tokens
- [ ] Remove CTA orange variables (unused in Tableau style) or repurpose

## Success Criteria
- All downstream SCSS files compile without errors
- No hardcoded color values remain in other files (all use tokens)
- File stays under 200 lines

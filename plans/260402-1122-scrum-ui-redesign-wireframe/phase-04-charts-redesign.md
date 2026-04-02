# Phase 4: Charts Redesign

## Context Links
- [Plan Overview](plan.md)
- [Phase 1: Tokens](phase-01-design-tokens.md)
- Reference wireframe: Screen 5 (Reports & Analytics) — `assets/designs/wireframe-agile-full.html` lines ~550–562 (CSS), ~1322–1480 (HTML)
- Files: `addons/project_scrum/static/src/scss/charts.scss`, `addons/project_scrum/static/src/xml/burndown-chart.xml`, `addons/project_scrum/static/src/xml/velocity-chart.xml`

## Overview

- **Priority:** P2
- **Status:** Completed
- **Effort:** ~3h
- **Depends on:** Phase 1 (tokens)
- **Description:** Update chart widget XML templates and SCSS to match wireframe Screen 5. Replace emoji, add legend row, style stat bar and status badge using design tokens. Zero Chart.js changes; badge class aliases kept in SCSS to avoid JS edits.

## Design Reference (from wireframe)

### Reports Layout (Screen 5)
```
[Tab bar: Burndown | Burnup | Velocity | Cycle Time | Lead Time]
[Stats row: 5 stat-cards in grid — Committed | Completed | Not Done | Scope Added | Scope Removed]
[reports-layout]
  [reports-chart-area: flex:1] — chart card with legend row
  [reports-stats-panel: 200px] — compact velocity + cycle time cards
```

### stat-card (wireframe)
```css
.stat-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-card);  /* 12px */
  padding: 12px 14px;
  margin-bottom: 8px;
  box-shadow: var(--shadow-card);
}
.stat-card-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .5px; color: var(--text-sec); margin-bottom: 4px; }
.stat-card-val   { font-size: 22px; font-weight: 800; color: var(--text); }
.stat-card-sub   { font-size: 10px; color: var(--text-sec); margin-top: 2px; }
```

### Tab bar (wireframe)
```css
.tab-bar { display: flex; gap: 0; border-bottom: 2px solid var(--border); margin-bottom: 16px; }
.tab { padding: 8px 16px; font-size: 12px; font-weight: 600; color: var(--text-sec); cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -2px; transition: all 150ms; }
.tab.active { color: var(--primary); border-bottom-color: var(--primary); }
```

### Burndown chart card legend row (wireframe)
```
[card: padding 16px]
  [header row: "Burndown Chart — Sprint 12"   |   Ideal ── · Actual ── · Today │]
  [SVG chart: ideal dashed gray, actual blue with area fill, amber TODAY marker]
```

### Status badge (wireframe style)
```
On Track: background #DCFCE7, color #166534
Behind:   background #FEE2E2, color #991B1B
No Data:  background #E2E8F0, color $text-secondary
```

### Empty state (wireframe pattern — no emoji)
```
[SVG chart icon, 40px]
[text: "No burndown data yet"]
[hint text, max-width 280px]
```

## Requirements

### XML Changes

#### `burndown-chart.xml`

1. **Header title** — Remove emoji `📉`, add inline SVG chart-bar icon before "Sprint Burndown"
2. **Legend row** — Add `.o-scrum-chart__legend` with 3 items: Ideal (dashed line swatch), Actual (solid blue swatch), Today (amber vertical bar swatch)
3. **Status badge** — Add new BEM classes `.o-scrum-chart__badge--on-track`, `--behind`, `--no-data` with wireframe colors. **Keep old `.badge-on-track/behind/no-data` as aliases** (used by `burndown-chart.js:217-219` — avoids JS changes)
4. **Status text** — Replace emoji `⚠ Behind` / `✓ On Track` with plain text `Behind` / `On Track`
5. **Empty state icon** — Replace emoji `📊` with inline SVG (bar chart outline, 36×36px)
6. **Stats bar** — Wrap existing stats row in `.o-scrum-chart__stats-bar` (no structure change, just rename for clarity)

```xml
<!-- Legend row (add after header, before canvas-wrap) -->
<div class="o-scrum-chart__legend">
    <span class="o-scrum-chart__legend-item">
        <span class="o-scrum-chart__legend-swatch o-scrum-chart__legend-swatch--ideal"/>
        Ideal
    </span>
    <span class="o-scrum-chart__legend-item">
        <span class="o-scrum-chart__legend-swatch o-scrum-chart__legend-swatch--actual"/>
        Actual
    </span>
    <span class="o-scrum-chart__legend-item o-scrum-chart__legend-item--today">
        <span class="o-scrum-chart__legend-swatch o-scrum-chart__legend-swatch--today"/>
        Today
    </span>
</div>
```

#### `velocity-chart.xml`

1. **Header title** — Remove emoji `📊`, add inline SVG bar-chart icon before "Team Velocity"
2. **Empty state icon** — Replace emoji `📈` with inline SVG (trending-up outline, 36×36px)
3. **Forecast stat value** — Remove inline `style="color:#F97316"` → use CSS class `.o-scrum-chart__stat-val--accent`

### SCSS Changes (`charts.scss`)

Full token alignment — replace raw hex values with design token variables:

1. **Container** — `border: 1px solid $border-color` (was `#dee2e6`), `border-radius: $card-radius`, `font-family: $font-family`
2. **Title** — `font-size: $font-size-base`, `color: $text-primary` (was `#212529`)
3. **Subtitle** — `color: $text-secondary` (was `#6c757d`)
4. **Stats bar border** — `border-top: 1px solid $border-color` (was `#dee2e6`)
5. **Stat val** — `font-size: $font-dash-stat` (22px), `color: $text-primary`
6. **Stat lbl** — `font-size: $font-size-xs` (10px), `color: $text-secondary`
7. **Status badges** — Update to wireframe semantic colors. Keep old class names as aliases for JS compat:
   - `.badge-on-track, .o-scrum-chart__badge--on-track`: `background: #DCFCE7`, `color: #166534`
   - `.badge-behind, .o-scrum-chart__badge--behind`:     `background: #FEE2E2`, `color: #991B1B`
   - `.badge-no-data, .o-scrum-chart__badge--no-data`:   `background: $border-color`, `color: $text-secondary`
8. **Skeleton** — `background: linear-gradient(90deg, $border-color 25%, $bg 50%, $border-color 75%)`, `border-radius: $card-radius`
9. **Empty icon** — `font-size` block removed (SVG now); `.o-scrum-chart__empty-icon svg { width: 36px; height: 36px; color: $text-subtle; }`
10. **Empty text** — `color: $text-primary`, `font-size: $font-size-base`
11. **Empty hint** — `color: $text-secondary`, `font-size: $font-size-sm`
12. **Legend row** — New styles:
    - `.o-scrum-chart__legend`: `display: flex; gap: 12px; margin-bottom: 8px`
    - `.o-scrum-chart__legend-item`: `font-size: $font-size-xs; color: $text-secondary; display: flex; align-items: center; gap: 4px`
    - `.o-scrum-chart__legend-item--today`: `color: $scrum-warning`
    - `.o-scrum-chart__legend-swatch`: `display: inline-block; width: 16px; height: 2px`
    - `--ideal`: `border-top: 1px dashed #CBD5E1; background: transparent`
    - `--actual`: `background: $scrum-primary`
    - `--today`: `width: 2px; height: 12px; background: $scrum-warning`
13. **Accent stat val** — `.o-scrum-chart__stat-val--accent { color: $scrum-accent; }`

## Implementation Steps

### Step 1: SCSS update (~1.5h)
- [x] Replace all raw hex colors with design token variables
- [x] Update status badge classes to new BEM names (`--on-track`, `--behind`, `--no-data`)
- [x] Add `.o-scrum-chart__legend` and swatch styles
- [x] Add `.o-scrum-chart__stat-val--accent` modifier
- [x] Add `font-family: $font-family` to `.o-scrum-chart`
- [x] Verify skeleton shimmer uses token colors

### Step 2: XML redesign (~1.5h)
- [x] `burndown-chart.xml`: remove `📉`, add SVG icon
- [x] `burndown-chart.xml`: add legend row with 3 swatches
- [x] `burndown-chart.xml`: update badge class names (`badge-on-track` → `o-scrum-chart__badge--on-track`)
- [x] `burndown-chart.xml`: replace `⚠ Behind` / `✓ On Track` text with plain text
- [x] `burndown-chart.xml`: replace `📊` empty icon with SVG
- [x] `velocity-chart.xml`: remove `📊`, add SVG icon
- [x] `velocity-chart.xml`: replace `📈` empty icon with SVG
- [x] `velocity-chart.xml`: remove inline `style="color:#F97316"`, add class `o-scrum-chart__stat-val--accent`

## Todo Checklist

- [x] Replace all `#dee2e6`, `#6c757d`, `#212529`, `#495057` with design tokens in `charts.scss`
- [x] Update status badge CSS: add new BEM classes + keep old names as aliases (JS compat)
- [x] Add legend row styles and XML
- [x] Remove all emoji from both XML templates
- [x] Add SVG icons (bar chart, trending up) to chart headers and empty states
- [x] Add `.o-scrum-chart__stat-val--accent` for forecast value
- [x] Test: charts load, skeleton shows, empty state shows without emoji, badge colors match wireframe

## Risks

| Risk | Mitigation |
|------|------------|
| Badge class rename breaks JS status logic | **Mitigated:** Keep old `.badge-on-track/behind/no-data` as SCSS aliases alongside new BEM names. `burndown-chart.js:217-219` unchanged. |
| SVG inline in QWeb XML breaks rendering | Test SVG render; if issues, use `t-call` sub-template |
| Legend row takes vertical space in dashboard widget | Dashboard embeds charts at fixed height; verify canvas-wrap still renders at correct height with legend added |

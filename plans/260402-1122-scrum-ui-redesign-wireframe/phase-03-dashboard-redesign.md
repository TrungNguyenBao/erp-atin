# Phase 3: Agile Dashboard Redesign

## Context Links
- [Plan Overview](plan.md)
- [Phase 1: Tokens](phase-01-design-tokens.md)
- Reference wireframe: Screen 1 (Dashboard) — `assets/designs/wireframe-agile-full.html` lines ~350–399 (CSS), ~696–900 (HTML)
- Files: `addons/project_scrum/static/src/xml/agile-dashboard.xml`, `addons/project_scrum/static/src/scss/agile-dashboard.scss`

## Overview

- **Priority:** P1
- **Status:** Completed
- **Effort:** ~4h
- **Depends on:** Phase 1 (tokens)
- **Description:** Redesign Agile Dashboard OWL template and SCSS to match wireframe Screen 1. Zero JS changes.

## Design Reference (from wireframe)

### Sprint Hero Card
```
[gradient bg: linear-gradient(135deg, #2563EB, #1D4ED8)]
  [small label: "Active Sprint"]
  [name: "Sprint 12 — CRM Module"  font-size:18px font-weight:800 color:white]
  [dates: "Apr 1 – Apr 14, 2026 · 8 days remaining"  opacity:.7]
  [stats row: Committed SP | Completed SP | Remaining SP | Progress%]
    each: num 20px bold, label 10px opacity.7
  [progress bar: rgba(255,255,255,.2) bg / white fill]
```

### Widget Card Pattern
```
[card: bg white, border 1px #E2E8F0, radius 12px, shadow-card]
  [card-header: SVG_ICON + TITLE  |  subtitle/action]
  [card-body: widget-specific content]
```

### Widget 3: Team Workload
```
[stat-row: NAME  [===bar===  SP]]
  bar: background #E2E8F0, fill $scrum-primary, height 6px
  SP: font-weight:700
```

### Widget 4: Backlog Health — 2×2 grid of stat-cards
```
[stat-card] x 4: number 22px bold | label 10px text-sec
warn stat: amber border/bg
danger stat: red border/bg
```

### Widget 6: Activity Feed
```
[activity-item: dot + text + time]
  dot: 8px circle, $scrum-primary bg
  text: "Task Name by Author"
  time: right-aligned, 10px, $text-secondary
```

### Dashboard Grid Layout
```
[row 1: Sprint Hero full-width]
[row 2: Burndown (1fr) | Team Workload (1fr)]
[row 3: Backlog Health (1fr) | Activity Feed (1fr)]  
[row 4: Velocity (full-width)]
```

## Requirements

### XML Changes (`agile-dashboard.xml`)

#### Topbar
- Remove emoji `🎯` from title
- Add SVG chart icon before "Agile Dashboard" text
- Breadcrumb style: `Projects / Dashboard`

#### Sprint Widget (Widget 1) — gradient hero
Replace plain card with:
```xml
<div class="o-agile-dashboard__sprint-hero" t-if="sprint">
    <div class="o-agile-dashboard__sprint-hero-label">Active Sprint</div>
    <div class="o-agile-dashboard__sprint-hero-name" t-esc="sprint.name"/>
    <div class="o-agile-dashboard__sprint-hero-dates">
        <t t-esc="sprint.start_date"/> – <t t-esc="sprint.end_date"/>
        · <t t-esc="sprint.days_remaining"/> days remaining
    </div>
    <div class="o-agile-dashboard__sprint-hero-stats">
        <!-- 4 stat items -->
    </div>
    <div class="o-agile-dashboard__sprint-hero-progress">
        <div class="o-agile-dashboard__sprint-hero-fill"
             t-att-style="'width:' + (sprint.completion_pct||0) + '%'"/>
    </div>
</div>
```

#### Widget headers — remove emojis, add SVG icons
- Widget 2 (Sprint Burndown): Remove `📉` → SVG chart-down icon
- Widget 3 (Team Workload): SVG users icon
- Widget 4 (Backlog Health): SVG list icon
- Widget 6 (Recent Activity): SVG clock icon

#### Widget 4: Backlog Health — change to stat-card grid
Replace flat flex row with 2×2 grid of `.o-agile-dashboard__bh-stat` cards.

### SCSS Changes (`agile-dashboard.scss`)

Key additions:
1. `.o-agile-dashboard__sprint-hero`: gradient bg, white text, border-radius `$card-radius`
2. `.o-agile-dashboard__sprint-hero-label`: `font-size: 11px`, `opacity: .7`, uppercase
3. `.o-agile-dashboard__sprint-hero-name`: `font-size: 18px`, `font-weight: 800`, `color: #fff`
4. `.o-agile-dashboard__sprint-hero-dates`: `font-size: 11px`, `opacity: .7`
5. `.o-agile-dashboard__sprint-hero-stats`: flexbox, 4 items, `gap: 20px`
6. `.o-agile-dashboard__sprint-hero-progress`: `background: rgba(255,255,255,.2)`, `height: 6px`, radius `100px`
7. `.o-agile-dashboard__sprint-hero-fill`: `background: #fff`, `height: 6px`
8. Card base: `border-radius: $card-radius` (12px), `box-shadow: $card-shadow`
9. Card title: `font-size: 11px`, `font-weight: 700`, `text-transform: uppercase`, `letter-spacing: .5px`
10. `.o-agile-dashboard__bh-stat`: white bg card, border, radius 8px, number 22px bold
11. Grid: Sprint hero = `grid-column: 1 / -1` (full width first row)
12. Workload bar: `height: 6px` (slim, matches wireframe)
13. Activity dot: `8px` circle, `$scrum-primary`
14. Font: `font-family: $font-family`

Updated grid template:
```scss
.o-agile-dashboard__grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: $gap-md;
    padding: $gap-md;

    .o-agile-dashboard__card--sprint    { grid-column: 1 / -1; }  // hero full-width
    .o-agile-dashboard__card--velocity  { grid-column: 1 / -1; }  // full-width
}
```

## Implementation Steps

### Step 1: XML redesign (~2h)
- [x] Update topbar: remove `🎯`, add SVG icon + breadcrumb text
- [x] Replace Widget 1 sprint card with `.sprint-hero` gradient structure
- [x] Remove `📉` from Widget 2 header (Sprint Burndown) → SVG chart-down icon
- [x] Remove `👥` from Widget 3 header → SVG users icon
- [x] Remove `📋` from Widget 4 header → SVG list icon; change to 2×2 stat grid
- [x] Remove `🕐` from Widget 6 header → SVG clock icon
- [x] Remove `🏃` from empty states → SVG running/sprint icon
- [x] Update "No active sprint" empty state: remove emoji, use SVG

### Step 2: SCSS redesign (~2h)
- [x] Add sprint hero styles (gradient, white text, progress bar)
- [x] Update card base: radius 12px, shadow-card
- [x] Update card-title typography: uppercase, letter-spacing
- [x] Add `.o-agile-dashboard__bh-stat` 2×2 grid card styles
- [x] Update workload bar to 6px height
- [x] Update activity item: dot + body + time layout
- [x] Update grid: sprint hero full-width row 1, velocity full-width
- [x] Update font-family to Plus Jakarta Sans

## Todo Checklist

- [x] Remove all emoji from `agile-dashboard.xml`
- [x] Sprint hero gradient card (white text on blue gradient)
- [x] Widget headers with SVG icons
- [x] Backlog health 2×2 stat-card grid
- [x] SCSS: sprint-hero, card radius, workload, activity, grid layout
- [x] Test: dashboard loads, sprint hero shows gradient, no emojis visible

## Risks

| Risk | Mitigation |
|------|------------|
| Sprint hero gradient clashes with Odoo dark mode | Add `@media (prefers-color-scheme: dark)` override or skip dark mode for now |
| SVG inline in XML escaped incorrectly | Use `t-call` sub-template pattern or escape `<>` as `&lt;&gt;` |

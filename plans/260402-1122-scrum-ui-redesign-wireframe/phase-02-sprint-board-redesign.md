# Phase 2: Sprint Board Redesign

## Context Links
- [Plan Overview](plan.md)
- [Phase 1: Tokens](phase-01-design-tokens.md)
- Reference wireframe: Screen 3 (Sprint Board) — `assets/designs/wireframe-agile-full.html` lines ~440–520 (CSS), ~1000–1150 (HTML)
- Files: `addons/project_scrum/static/src/xml/sprint-board.xml`, `addons/project_scrum/static/src/scss/sprint-board.scss`

## Overview

- **Priority:** P0
- **Status:** Completed
- **Effort:** ~5h
- **Depends on:** Phase 1 (tokens)
- **Description:** Redesign Sprint Board OWL template and SCSS to match wireframe Screen 3. Zero JS changes.

## Design Reference (from wireframe)

### Layout
```
[Topbar: breadcrumb + "Create Issue" btn]
[Board header: sprint name · date range · filter chips · "Backlog" toggle]
[Board body]
  [Col: #F1F5F9 bg, 12px radius]  × N columns
    [Col header: NAME  COUNT_BADGE  SP_LABEL]
    [Col body: task cards scrollable]
    [Col footer: + Create Issue dashed button]
  [Backlog sidebar: 260px, white bg]
```

### Task Card anatomy
```
[top row: PRIORITY_DOT  TYPE_SVG_ICON  TASK_KEY]
[title: 2-line clamp, 13px bold]
[blocked badge: ⚠ Blocked (red chip) — only if blocked]
[footer: AVATAR  ASSIGNEE_NAME  ·  SP_BADGE (circle)]
```

### Board Header chips (wireframe filter chips)
```
[Sprint selector (select)]  [· dates]
[chip: All]  [chip: My Issues]  [chip: Blocked]
[btn-outline: ≡ Backlog]  [btn-primary: + Create Issue]
```

### Status color coding for columns
- To Do → `--status-todo` badge bg (#F1F5F9)
- In Progress → `--status-inprogress` badge bg (#EFF6FF)
- In Review → `--status-review` badge bg (#F5F3FF)
- Testing → `--status-testing` badge bg (#FFFBEB)
- Done → `--status-done` badge bg (#ECFDF5)

## Requirements

### XML Changes (`sprint-board.xml`)

#### Board header — add filter chips
```xml
<!-- Filter chips row (visual-only — no t-on-click to avoid OWL runtime error; wire in follow-up) -->
<div class="o-sprint-board__filter-chips">
    <button class="o-sprint-board__chip o-sprint-board__chip--active">All</button>
    <button class="o-sprint-board__chip">My Issues</button>
    <button class="o-sprint-board__chip">Blocked</button>
</div>
<button class="btn btn-primary btn-sm o-sprint-board__create-btn">
    <!-- Heroicons plus svg --> + Create Issue
</button>
```
Note: Filter chips are visual-only in Phase 2 — no `t-on-click` handlers (adding handlers for undefined methods causes OWL runtime errors). Wire `setFilter` in a follow-up JS phase.

#### Task card — replace emoji with SVG
Replace emoji `taskTypeIcon[task.task_type]` with inline SVG `<t t-call="project_scrum.TypeIcon">` sub-template per type.

Add priority dot before type icon:
```xml
<span class="o-sprint-board__priority-dot"
      t-att-data-priority="task.priority || '0'"/>
```

Add task key display:
```xml
<span class="o-sprint-board__task-key">
    <t t-esc="'#' + task.id"/>
</span>
```

Replace blocked-bar (emoji) with blocked-badge chip:
```xml
<t t-if="task.is_blocked">
    <span class="o-sprint-board__blocked-badge">
        <!-- warning svg --> Blocked
    </span>
</t>
```

#### Column footer — add "Create Issue" button
```xml
<div class="o-sprint-board__col-footer">
    <button class="o-sprint-board__col-add-btn">
        <!-- plus svg --> Create Issue
    </button>
</div>
```

#### Empty state — replace emoji with SVG
```xml
<div class="o-sprint-board__empty">
    <div class="o-sprint-board__empty-icon">
        <!-- SVG: running person outline -->
    </div>
    ...
</div>
```

### SCSS Changes (`sprint-board.scss`) — Full rewrite

Key changes from current state:
1. `font-family: $font-family` (Plus Jakarta Sans)
2. Column bg: `$column-bg` (#F1F5F9), radius `$column-radius` (12px)
3. Column header: no `border-bottom: 2px solid` → `border-bottom: 1px solid $border-color`
4. Col count badge: pill shape, bg `$border-color`, text `$text-secondary`
5. Card: `border-radius: 8px`, `box-shadow: $card-shadow`, hover = `$card-shadow-hover + translateY(-2px)`
6. Card title: `font-weight: 600`, `color: $text-primary`
7. SP badge: circular `22px`, `background: #EFF6FF`, `color: $scrum-primary`
8. Priority dot: `8px × 8px`, `border-radius: 2px` (square dot)
9. Task key: `font-size: 10px`, `font-weight: 700`, `color: $scrum-primary`
10. Blocked badge: `background: #FEE2E2`, `color: $scrum-danger`, `border-radius: 4px`, `font-size: 9px`
11. Filter chips: `border-radius: 100px`, outline style, active = `#EFF6FF` bg + `$scrum-primary` border + color
12. Col add button: `border: 1px dashed $border-color`, `color: $text-secondary`, hover = `border-color: $scrum-primary`, `color: $scrum-primary`

## Implementation Steps

### Step 1: XML redesign (~2.5h)
- [x] Add `project_scrum.TypeIcon` sub-template with inline SVG per type (story/task/bug/improvement/epic)
- [x] Update board header: filter chips + "Create Issue" button with SVG plus icon
- [x] Update `project_scrum.TaskCard`: priority dot, type SVG, task key (#ID), blocked-badge chip, remove emojis
- [x] Add column footer with "col-add-btn"
- [x] Replace empty-state emoji with SVG icon
- [x] Remove all emoji (`🏃`, `🔴`, `≡`) — replace with SVG or text

### Step 2: SCSS redesign (~2.5h)
- [x] Update root `.o-sprint-board`: `font-family: $font-family`, `background: $bg`
- [x] Header: `background: $surface`, `border-bottom: 1px solid $border-color`
- [x] Sprint selector: `border-radius: $input-radius`, `border-color: $border-color`
- [x] Filter chips: `.o-sprint-board__chip` — pill, outline, active state
- [x] Create Issue button: primary style
- [x] Columns: `background: $column-bg`, `border-radius: $column-radius`, no overflow: hidden (let cards show shadow)
- [x] Column header: `background: $column-bg`, `padding: 10px 12px`, header border `1px solid $border-color`
- [x] Col count: pill badge `background: $border-color`, `color: $text-secondary`
- [x] Col body: `padding: 8px`, `gap: 6px`
- [x] Card: `background: $surface`, `border: 1px solid $border-color`, `border-radius: 8px`, `box-shadow: $card-shadow`, transition 200ms, hover `$card-shadow-hover + translateY(-2px)`
- [x] Card blocked: `border-left: 3px solid $scrum-danger`
- [x] Card title: `font-size: 13px`, `font-weight: 600`, `color: $text-primary`, 2-line clamp
- [x] Priority dot: `.o-sprint-board__priority-dot` 8×8px square dot, data-priority color map
- [x] Task key: `font-size: 10px`, `font-weight: 700`, `color: $scrum-primary`
- [x] Type icon: SVG 14×14px, colored per type
- [x] Blocked badge: chip style `#FEE2E2`/`$scrum-danger`
- [x] SP badge: `22px` circle, `background: #EFF6FF`, `color: $scrum-primary`
- [x] Avatar: `22px` circle, `object-fit: cover`
- [x] Col add btn: dashed border button
- [x] Backlog sidebar: `background: $surface`, `border-left: 1px solid $border-color`
- [x] Backlog items: card style with hover

## Todo Checklist

- [x] Add `TypeIcon` sub-template (5 SVG variants)
- [x] Update board header template: filter chips + CTA
- [x] Update `TaskCard` template: priority dot, SVG type icon, task key, blocked chip
- [x] Add column footer: col-add-btn
- [x] Remove all emoji from templates
- [x] Full SCSS rewrite: tokens, layout, cards, chips
- [x] Test in browser: columns render, cards drag, backlog toggle
- [x] Verify no emoji in rendered output

## Risks

| Risk | Mitigation |
|------|------------|
| SVG inline in XML breaks QWEB | Use `t-call` sub-templates; test SVG render in Odoo 18 |
| Filter chips wired to non-existent JS state | No `t-on-click` handlers — pure visual. Wire `setFilter` in follow-up JS phase |
| Column `overflow: hidden` breaks card hover shadow | Remove overflow:hidden from column container; use `overflow-y: auto` only on column-body |

# Phase 2: Wireframe & UI/UX Design

## Context Links

- [Plan Overview](plan.md)
- [Phase 1: Ceremony & Security](phase-01-ceremony-model-and-security.md)
- Existing Sprint Board view: `addons/project_scrum/views/project-sprint-board-views.xml`
- Existing backlog view: `addons/project_scrum/views/project-backlog-views.xml`
- Odoo 18 design patterns: OWL components, QWeb templates
- Design guidelines: `docs/design-guidelines.md`

## Overview

- **Priority:** P0 -- Critical (blocks all OWL phases)
- **Status:** Completed
- **Effort:** ~4h
- **Depends on:** Phase 1 (ceremony model informs ceremony UI wireframes)
- **Description:** Create HTML wireframes for all OWL components: Sprint Board, Burndown Chart, Velocity Chart, Agile Dashboard, Ceremony views. Establish visual language, layout grid, interaction patterns before coding.

## Requirements

### Functional

- F1: Sprint Board wireframe -- column layout, task card anatomy, sprint selector, backlog sidebar
- F2: Burndown Chart wireframe -- chart area, legend, tooltip, sprint info header
- F3: Velocity Chart wireframe -- bar chart layout, rolling average overlay, sprint comparison
- F4: Agile Dashboard wireframe -- widget grid, sprint summary card, team workload, backlog health, activity feed
- F5: Ceremony views wireframe -- form layout, calendar integration, retro template
- F6: Interaction patterns -- drag-drop feedback, hover states, loading skeletons, empty states

### Non-Functional

- NF1: Wireframes must be self-contained HTML files (viewable in browser)
- NF2: Follow Odoo 18 visual language (colors, typography, spacing)
- NF3: Include mobile responsive breakpoints
- NF4: Dark mode considerations noted
- NF5: Accessibility annotations (ARIA roles, keyboard navigation)

## Design System Tokens

### Colors (aligned with Odoo 18 + project_scrum)

| Token | Value | Usage |
|-------|-------|-------|
| `--scrum-primary` | `#714B67` | Odoo primary purple |
| `--scrum-success` | `#28A745` | On track, completed |
| `--scrum-warning` | `#FFC107` | At risk, WIP limit near |
| `--scrum-danger` | `#DC3545` | Behind, blocked, over WIP |
| `--scrum-info` | `#17A2B8` | Story points badge |
| `--board-bg` | `#F8F9FA` | Board background |
| `--card-bg` | `#FFFFFF` | Task card background |
| `--column-bg` | `#F1F3F5` | Column background |
| `--sidebar-bg` | `#E9ECEF` | Backlog sidebar |

### Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| Board header | System (Odoo default) | 18px | 600 |
| Column title | System | 14px | 600 |
| Task card title | System | 13px | 500 |
| SP badge | System | 11px | 700 |
| Chart labels | System | 12px | 400 |
| Dashboard stat | System | 24px | 700 |

### Spacing

| Token | Value |
|-------|-------|
| `--gap-xs` | 4px |
| `--gap-sm` | 8px |
| `--gap-md` | 16px |
| `--gap-lg` | 24px |
| `--gap-xl` | 32px |
| `--card-radius` | 6px |
| `--column-radius` | 8px |

## Wireframe Specifications

### W1: Sprint Board

```
┌─────────────────────────────────────────────────────────────┐
│ [Sprint Selector ▼]    Sprint 5 (Apr 1-14)    [⚙ Settings] │
│ Committed: 34 SP  |  Completed: 12 SP  |  Days left: 9     │
├──────────┬──────────┬──────────┬──────────┬─────────────────┤
│ TO DO    │IN PROGRESS│IN REVIEW │  DONE    │ ≡ BACKLOG      │
│ 5 tasks  │ 3 tasks  │ 2 tasks  │ 4 tasks  │ (sidebar)      │
│ 15 SP    │ 10 SP    │ 5 SP     │ 12 SP    │                │
│ ──────── │ ──────── │ ──────── │ ──────── │ □ Unassigned   │
│ ┌──────┐ │ ┌──────┐ │ ┌──────┐ │ ┌──────┐ │   task 1 [3SP] │
│ │Task  │ │ │Task  │ │ │Task  │ │ │Task  │ │ □ Another      │
│ │title │ │ │title │ │ │title │ │ │✓done │ │   task [5SP]   │
│ │[5SP] │ │ │[3SP] │ │ │[2SP] │ │ │[3SP] │ │                │
│ │👤 AV │ │ │👤 AV │ │ │👤 AV │ │ │👤 AV │ │ [+ Add to      │
│ │🏷 bug │ │ │🔴blk │ │ │      │ │ │      │ │  Sprint]       │
│ └──────┘ │ └──────┘ │ └──────┘ │ └──────┘ │                │
│ ┌──────┐ │ ┌──────┐ │          │          │                │
│ │...   │ │ │...   │ │          │          │                │
│ └──────┘ │ └──────┘ │          │          │                │
└──────────┴──────────┴──────────┴──────────┴─────────────────┘
```

**Task Card Anatomy:**
```
┌────────────────────────┐
│ 🏷 story  Task Title   │  ← type icon + title
│ that can wrap to two   │
│ lines max              │
├────────────────────────┤
│ 👤 Avatar  Name   [5]  │  ← assignee + SP badge
│ 🔴 Blocked: reason...  │  ← blocked indicator (conditional)
└────────────────────────┘
```

**Interactions:**
- Drag task card → semi-transparent ghost, drop zone highlights
- Column over WIP limit → amber header bar
- Sprint selector → dropdown with draft/active sprints
- Backlog sidebar → collapsible with toggle button
- Empty column → "No tasks" placeholder with dashed border

### W2: Burndown Chart

```
┌─────────────────────────────────────────────┐
│ 📉 Sprint Burndown    Sprint 5 (Apr 1-14)   │
├─────────────────────────────────────────────┤
│ 35 ┤╲                                       │
│    │  ╲  - - - Ideal                        │
│ 25 ┤   ╲ ────── Actual                      │
│    │    ╲╲                                   │
│ 20 ┤     ╲ ╲                                │
│    │      ╲  ╲                               │
│ 15 ┤       ╲  ╲                              │
│    │        ╲   ╲                             │
│ 10 ┤         ╲    ╲                           │
│    │          ╲                                │
│  5 ┤           ╲                              │
│    │            ╲                              │
│  0 ┤─────────────────────────────────────    │
│    Apr1  Apr3  Apr5  Apr7  Apr9  Apr11 Apr14 │
├─────────────────────────────────────────────┤
│ Remaining: 18 SP | Ideal: 15 SP | Δ: +3 SP  │
└─────────────────────────────────────────────┘
```

**Interactions:**
- Hover point → tooltip with date, remaining SP, ideal SP
- Status indicator: green (below ideal), red (above ideal)

### W3: Velocity Chart

```
┌─────────────────────────────────────────────┐
│ 📊 Team Velocity     Last 6 Sprints         │
├─────────────────────────────────────────────┤
│ 40 ┤                                        │
│    │    ██                          ██       │
│ 35 ┤    ██  ░░          ██          ██       │
│    │    ██  ░░    ██    ██  ░░      ██  ░░   │
│ 30 ┤    ██  ░░    ██    ██  ░░  ━━━━██━━░░━  │ ← rolling avg
│    │    ██  ░░    ██    ██  ░░      ██  ░░   │
│ 25 ┤    ██  ░░    ██    ██  ░░      ██  ░░   │
│    │    ██  ░░    ██    ██  ░░      ██  ░░   │
│ 20 ┤    ██  ░░    ██    ██  ░░      ██  ░░   │
│    │                                         │
│  0 ┤─────────────────────────────────────    │
│      S1    S2    S3    S4    S5    S6         │
├─────────────────────────────────────────────┤
│ ██ Completed  ░░ Committed  ━━ Avg (3-sprint)│
│ Avg Velocity: 31 SP | Forecast next: 32 SP   │
└─────────────────────────────────────────────┘
```

### W4: Agile Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│ 🎯 Agile Dashboard    [Project Selector ▼]                  │
├─────────────────────────────┬───────────────────────────────┤
│ ACTIVE SPRINT               │ SPRINT BURNDOWN (mini)        │
│ ┌─────────────────────────┐ │ ┌───────────────────────────┐ │
│ │ Sprint 5                │ │ │ (mini burndown chart)     │ │
│ │ Apr 1 - Apr 14          │ │ │                           │ │
│ │ ████████░░░░░░ 65%      │ │ │ 📉                        │ │
│ │ 22/34 SP completed      │ │ │                           │ │
│ │ 9 days remaining        │ │ └───────────────────────────┘ │
│ │ 14 tasks (10 done)      │ │                               │
│ └─────────────────────────┘ │                               │
├─────────────────────────────┼───────────────────────────────┤
│ TEAM WORKLOAD               │ BACKLOG HEALTH                │
│ ┌─────────────────────────┐ │ ┌───────────────────────────┐ │
│ │ Alice   ████████ 13 SP  │ │ │ 📋 Total: 47 items       │ │
│ │ Bob     ██████   8 SP   │ │ │ ⚠️  Unestimated: 12      │ │
│ │ Carol   ████     5 SP   │ │ │ 🔴 Critical: 3           │ │
│ │ Dave    ████████ 8 SP   │ │ │ 📊 Total SP: 156         │ │
│ └─────────────────────────┘ │ └───────────────────────────┘ │
├─────────────────────────────┴───────────────────────────────┤
│ VELOCITY TREND (compact)                                     │
│ ┌───────────────────────────────────────────────────────────┐│
│ │ (velocity bar chart - last 6 sprints)                     ││
│ └───────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│ RECENT ACTIVITY                                              │
│ • Task "Login API" moved to Done by Alice          2h ago   │
│ • Task "DB Migration" moved to In Review by Bob    4h ago   │
│ • Sprint 5 started by Scrum Master                 1d ago   │
│ • Task "UI Polish" added to Sprint 5               1d ago   │
└─────────────────────────────────────────────────────────────┘
```

### W5: Ceremony Views

**Ceremony Form:**
```
┌─────────────────────────────────────────────┐
│ [Planning ▼]  Sprint Planning - Sprint 5     │
│ ═══════════════════════════════════════════  │
│ Sprint:  [Sprint 5 ▼]                        │
│ Date:    [2026-04-01 09:00]                  │
│ Duration: [2.0] hours                        │
│ ─────────────────────────────────────────── │
│ Attendees: [Alice] [Bob] [Carol] [Dave] [+]  │
│ ─────────────────────────────────────────── │
│ ┌─ Meeting Notes ─────────────────────────┐ │
│ │ (rich text editor)                      │ │
│ └─────────────────────────────────────────┘ │
│ ┌─ Action Items ──────────────────────────┐ │
│ │ - [ ] Review backlog priorities          │ │
│ │ - [ ] Assign story points to new items   │ │
│ └─────────────────────────────────────────┘ │
│ ─── Retrospective (visible if type=retro) ─ │
│ ┌ What Went Well ┐ ┌ To Improve ──────────┐ │
│ │                 │ │                      │ │
│ └─────────────────┘ └──────────────────────┘ │
│ [💬 Chatter / Activity Log]                  │
└─────────────────────────────────────────────┘
```

**Ceremony Calendar:**
```
┌─────────────────────────────────────────────┐
│ April 2026        [< Month >]    [+Create]  │
├────┬────┬────┬────┬────┬────┬────┤
│Mon │Tue │Wed │Thu │Fri │Sat │Sun │
├────┼────┼────┼────┼────┼────┼────┤
│    │ 1  │ 2  │ 3  │ 4  │ 5  │ 6  │
│    │🟦P │🟩D │🟩D │🟩D │    │    │
│    │9am │9am │9am │9am │    │    │
├────┼────┼────┼────┼────┼────┼────┤
│ 7  │ 8  │ 9  │ 10 │ 11 │ 12 │ 13 │
│🟩D │🟩D │🟩D │🟩D │🟩D │    │    │
│9am │9am │9am │9am │9am │    │    │
├────┼────┼────┼────┼────┼────┼────┤
│ 14 │ 15 │    │    │    │    │    │
│🟧R │🟪Re│    │    │    │    │    │
│2pm │3pm │    │    │    │    │    │
└────┴────┴────┴────┴────┴────┴────┘
🟦 Planning  🟩 Daily  🟧 Review  🟪 Retro
```

### W6: Mobile Responsive Layouts

**Sprint Board (< 768px):**
```
┌─────────────────────┐
│ [Sprint 5 ▼]        │
│ 22/34 SP | 9 days   │
├─────────────────────┤
│ [TO DO ▼] 5 tasks   │  ← tabs or accordion
├─────────────────────┤
│ ┌─────────────────┐ │
│ │ Task title      │ │
│ │ 👤 Alice  [5SP] │ │
│ └─────────────────┘ │
│ ┌─────────────────┐ │
│ │ Task title      │ │
│ │ 👤 Bob    [3SP] │ │
│ └─────────────────┘ │
└─────────────────────┘
```

**Dashboard (< 768px):**
```
┌─────────────────────┐
│ [Project ▼]         │
├─────────────────────┤
│ Sprint 5            │
│ ████████░░░░ 65%    │
│ 22/34 SP | 9 days   │
├─────────────────────┤
│ 📉 Burndown (mini)  │
├─────────────────────┤
│ 👥 Team Workload    │
│ Alice ████████ 13SP │
│ Bob   ██████    8SP │
├─────────────────────┤
│ 📋 Backlog: 47      │
│ ⚠️  Unest: 12       │
└─────────────────────┘
```

## Implementation Steps

### Step 1: Design system & tokens (~0.5h)

- [ ] Define SCSS variables file `static/src/scss/scrum-design-tokens.scss`
- [ ] Document color palette, typography, spacing tokens
- [ ] Create color scheme for task types (story=blue, bug=red, task=gray, improvement=green)

### Step 2: Sprint Board wireframe HTML (~1h)

- [ ] Create `assets/designs/wireframe-sprint-board.html`
- [ ] Desktop layout: 4 columns + collapsible sidebar
- [ ] Task card component with all states (normal, blocked, dragging)
- [ ] Column header with WIP indicator states (normal, warning, danger)
- [ ] Empty state designs
- [ ] Drag-drop visual feedback mockup

### Step 3: Charts wireframe HTML (~0.5h)

- [ ] Create `assets/designs/wireframe-burndown-chart.html`
- [ ] Create `assets/designs/wireframe-velocity-chart.html`
- [ ] Chart containers with proper aspect ratios
- [ ] Legend placement, tooltip mockups
- [ ] Status indicators (on-track vs behind)

### Step 4: Dashboard wireframe HTML (~1h)

- [ ] Create `assets/designs/wireframe-agile-dashboard.html`
- [ ] 2-column grid layout with all 6 widgets
- [ ] Sprint summary card with progress bar
- [ ] Team workload horizontal bars
- [ ] Backlog health stat cards
- [ ] Activity feed timeline
- [ ] Empty/no-sprint state

### Step 5: Ceremony wireframe HTML (~0.5h)

- [ ] Create `assets/designs/wireframe-ceremony-views.html`
- [ ] Form layout with conditional retro section
- [ ] Calendar view color coding by type
- [ ] Attendee picker component

### Step 6: Mobile responsive wireframes (~0.5h)

- [ ] Add responsive variants to each wireframe HTML
- [ ] Sprint Board: tab/accordion column switcher
- [ ] Dashboard: single-column stack
- [ ] Document breakpoints: 768px (tablet), 480px (phone)

### Step 7: Interaction & state documentation

- [ ] Document all interaction patterns in wireframe files:
  - Drag states: idle, grabbed, over-target, dropped
  - Loading: skeleton screens for each widget
  - Error: failed RPC, conflict resolution
  - Empty: no sprint, no tasks, no data
- [ ] Accessibility notes: keyboard nav order, ARIA labels, focus indicators

## Deliverables

| File | Content |
|------|---------|
| `assets/designs/wireframe-sprint-board.html` | Sprint Board full wireframe |
| `assets/designs/wireframe-burndown-chart.html` | Burndown Chart wireframe |
| `assets/designs/wireframe-velocity-chart.html` | Velocity Chart wireframe |
| `assets/designs/wireframe-agile-dashboard.html` | Dashboard wireframe |
| `assets/designs/wireframe-ceremony-views.html` | Ceremony UI wireframe |
| `static/src/scss/scrum-design-tokens.scss` | Design tokens SCSS |

## Risks

| Risk | Mitigation |
|------|------------|
| Wireframes drift from Odoo 18 native look | Reference `addons/web/static/src/` SCSS variables, match existing component patterns |
| Over-designing before implementation | Keep wireframes low-fidelity, focus on layout + interaction, not pixel-perfect |
| Mobile layout too complex for OWL | Prioritize desktop, mobile = simplified view (tabs instead of columns) |

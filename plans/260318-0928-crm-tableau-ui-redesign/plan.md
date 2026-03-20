---
title: "CRM Tableau/Salesforce UI Redesign"
description: "Redesign CRM module UI from vibrant blue to flat Tableau/Salesforce corporate style"
status: pending
priority: P1
effort: 3h
branch: main
tags: [ui, scss, crm, redesign]
created: 2026-03-18
---

# CRM Tableau/Salesforce UI Redesign

## Overview

Transform the current vibrant blue, block-based UI into a flat, corporate Tableau/Salesforce aesthetic. Key shift: remove playful animations/shadows, adopt dark navy sidebar, flatten kanban cards, strengthen progress bars.

## Current State

- 7 SCSS files + 1 JS patch + 2 XML views
- Style: "Trust Blue" #2563EB, bold hover shadows, card lift on hover, left accent borders
- Total SCSS ~580 lines across 7 files

## Target State

- Flat, minimal corporate SaaS look (Tableau from Salesforce)
- Dark navy sidebar (#1B2559)
- No card hover lift/transform, no left accent borders
- Subtle borders instead of shadows
- Prominent colored progress bars in kanban column headers
- Clean whitespace, reduced animations

## Phases

| # | Phase | File(s) | Status | Effort |
|---|-------|---------|--------|--------|
| 1 | Design tokens | `_variables.scss` | pending | 20min |
| 2 | Mixins update | `_mixins.scss` | pending | 15min |
| 3 | Common styles | `common-enhance.scss` | pending | 30min |
| 4 | CRM Kanban | `crm-kanban-enhance.scss` | pending | 45min |
| 5 | CRM Form | `crm-form-enhance.scss` | pending | 20min |
| 6 | Sidebar & Navbar | `common-enhance.scss` (new section) | pending | 30min |
| 7 | Sale views | `sale-form-enhance.scss`, `sale-kanban-enhance.scss` | pending | 20min |

## Key Dependencies
- No new files needed (update existing only per dev rules)
- No JS changes needed (purely SCSS)
- No XML view changes needed
- Manifest unchanged (no new assets)

## Risk Assessment
- Low risk: CSS-only changes, no logic changes
- Sidebar styling targets Odoo core `.o_main_navbar` and `.o_action_manager` selectors - verify they exist in Odoo 18/19
- Progress bar colors may need per-stage customization via Odoo's existing data attributes

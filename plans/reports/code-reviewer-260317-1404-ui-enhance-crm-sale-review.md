# Code Review: ui_enhance_crm_sale Module

## Scope
- Files: 15 (1 manifest, 1 init, 2 XML views, 2 JS patches, 7 SCSS, 2 OWL XML templates, 1 __init__)
- LOC: ~750
- Focus: Full module review (XML xpath, SCSS, JS patches, manifest, Odoo 18 conventions)

## Overall Assessment

Solid UI enhancement module with clean architecture. Design tokens, mixins, and SCSS layering are well-structured. Most xpath expressions correctly target core view elements. A few issues found ranging from **critical class-overwrite bugs** to medium-priority scoping concerns.

---

## Critical Issues

### 1. [CRITICAL] Kanban class attribute OVERWRITE (not append)

**File:** `views/crm-lead-views-inherit.xml` line 44, `views/sale-order-views-inherit.xml` line 53

Using `position="attributes"` with `<attribute name="class">` **replaces** the entire class string. The module hardcodes the original classes back in, but this is fragile:

**CRM kanban (line 44):**
```xml
<attribute name="class">o_kanban_small_column o_opportunity_kanban ui-enhance-kanban</attribute>
```
This works today because the original is `o_kanban_small_column o_opportunity_kanban`, but if core Odoo adds/changes classes in a future patch, this override will silently drop them.

**Sale kanban (line 53):**
```xml
<attribute name="class">o_kanban_mobile ui-enhance-kanban</attribute>
```
Same fragility issue.

**Sale list (line 72):**
```xml
<attribute name="class">o_sale_order ui-enhance-list</attribute>
```
Same fragility -- original `o_sale_order` class duplicated manually.

**CRM list (line 61):**
```xml
<attribute name="class">ui-enhance-list</attribute>
```
**BUG:** The original CRM list view has NO class attribute on `<list>`. When Odoo 18 adds one upstream, this will overwrite it. Currently safe, but inconsistent with the pattern used elsewhere.

**Recommendation:** Odoo 18 supports `position="attributes"` with `separator` and `add` operation. Use:
```xml
<xpath expr="//kanban" position="attributes">
    <attribute name="class" separator=" " add="ui-enhance-kanban"/>
</xpath>
```
This appends without overwriting. If `add` is not available in this Odoo version, the current approach works but should be documented as fragile.

### 2. [CRITICAL] Sale order list view - class overwrite drops original class

**File:** `views/sale-order-views-inherit.xml` line 72

The original `sale_order_tree` list element has `class="o_sale_order"`. The inherited view sets:
```xml
<attribute name="class">o_sale_order ui-enhance-list</attribute>
```
While this preserves the original class by hardcoding it, any upstream change will break it. Same fix as above applies.

---

## High Priority

### 3. [HIGH] SCSS selectors too broad - will leak to non-CRM/Sale views

**File:** `static/src/scss/common-enhance.scss` lines 166-268

The selectors `.o_list_view` and `.o_kanban_view` are **global**. Every list and kanban view in the entire Odoo backend will get these styles (zebra striping, sticky headers, kanban card hover effects, etc.). This is almost certainly unintended for a module named "CRM & Sale UI Enhancement."

**Affected selectors:**
- Line 167: `.o_list_view` (no scoping)
- Line 219: `.o_kanban_view` (no scoping)

**Recommendation:** Scope to the custom classes:
```scss
// Instead of:
.ui-enhance-list,
.o_list_view { ... }

// Use:
.ui-enhance-list { ... }
```
Only the views that have `ui-enhance-list` class added via xpath will be affected. The `.o_list_view` fallback makes the scoping pointless.

### 4. [HIGH] sale-kanban-enhance.scss - CRM list styles in wrong file

**File:** `static/src/scss/sale-kanban-enhance.scss` lines 75-96

CRM list view styles (`.o_crm_lead_list`) are defined in the sale kanban file. Should be in a dedicated `crm-list-enhance.scss` or in `common-enhance.scss`.

Also, line 77 has `.o_list_view` as a fallback selector, which again leaks globally.

### 5. [HIGH] sale-kanban-enhance.scss selector `.o_kanban_view .o_kanban_record` too broad

**File:** `static/src/scss/sale-kanban-enhance.scss` lines 12-48

The selector `.o_kanban_view .o_kanban_record` targets ALL kanban records across the entire backend, not just Sale orders. The `.fw-bolder.fs-5` and `.o_field_monetary.fw-bolder` selectors within it will affect any kanban view that happens to use these Bootstrap classes.

**Recommendation:** Scope to `.ui-enhance-kanban .o_kanban_record` or create a sale-specific wrapper class.

### 6. [HIGH] JS patch on KanbanRenderer - global patch for CRM-only behavior

**File:** `static/src/js/crm-kanban-enhance-patch.js`

The `KanbanRenderer` is patched globally. The `setup()` method runs for every kanban view, adding overhead. The scoping check (`el.closest(".o_opportunity_kanban")`) mitigates the functional impact, but:
- Performance: `onMounted` hook fires for every kanban view load
- The class check happens after mount, so there's a brief FOUC potential

This is acceptable for a lightweight check but should be documented.

---

## Medium Priority

### 7. [MEDIUM] Empty OWL XML templates serve no purpose

**Files:** `static/src/xml/crm-kanban-card-template.xml`, `static/src/xml/sale-kanban-card-template.xml`

Both files contain only comments inside empty `<templates>` tags. They are included via `'ui_enhance_crm_sale/static/src/xml/*.xml'` in the manifest. While harmless, empty template files add unnecessary asset bundle weight and confusion.

**Recommendation:** Either add actual template overrides or remove the files and the glob pattern.

### 8. [MEDIUM] JS glob pattern in manifest includes empty XML files

**File:** `__manifest__.py` line 31

```python
'ui_enhance_crm_sale/static/src/xml/*.xml',
```
Loads the empty template files. Not harmful but wasteful.

### 9. [MEDIUM] FormController.onRecordSaved - selector fragility

**File:** `static/src/js/form-save-feedback-patch.js` line 20-21

```js
const crmForm = rootEl.querySelector(".o_lead_opportunity_form");
```
This correctly targets the CRM form class. However, the Sale order check at line 28:
```js
if (rootEl.querySelector(".o_sale_order"))
```
The `.o_sale_order` class exists on both the list view and form view elements. Since `FormController` only applies to form views, this is fine. But the selector could be more specific (e.g., `.o_sale_order.o_form_view`) for clarity.

### 10. [MEDIUM] `darken()` SCSS function deprecated in modern Sass

**File:** `static/src/scss/common-enhance.scss` lines 84, 89, 94, 99

Uses `darken($color, %)` which is deprecated in Dart Sass. Odoo 18 still uses node-sass/libsass where this works, but should be noted for future migration.

### 11. [MEDIUM] Missing `application: False` in manifest

**File:** `__manifest__.py`

While `application` defaults to `False`, explicit declaration is an Odoo convention for clarity.

---

## Low Priority

### 12. [LOW] File naming uses kebab-case (non-standard for Odoo)

Odoo convention is underscore_case for file names (e.g., `crm_lead_views_inherit.xml`). This module uses kebab-case (`crm-lead-views-inherit.xml`). Functionally fine but deviates from Odoo ecosystem norms. Note: the project's own development rules prescribe kebab-case, so this follows project rules over Odoo convention.

### 13. [LOW] Priority 100 on all inherited views

All six inherited views use `priority="100"`. This works but means all UI enhancements load at the same priority. If ordering matters between them, use different values.

### 14. [LOW] sale-kanban-enhance.scss empty ruleset

**File:** `static/src/scss/sale-kanban-enhance.scss` lines 6-9

```scss
.o_sale_order_kanban,
.o_kanban_view .o_kanban_record .o_sale_order {
    // Reuse the shared kanban enhancements from common-enhance
}
```
Empty ruleset with only a comment. Remove or implement.

---

## Positive Observations

1. **Clean design token system** - Variables file provides consistent palette, spacing, shadows, transitions
2. **Well-structured SCSS layering** - _variables -> _mixins -> common -> specific follows best practices
3. **Correct manifest asset ordering** - SCSS files load in dependency order
4. **FormController patch correctly calls super** and returns result
5. **KanbanRenderer patch uses safe optional chaining** (`this.rootRef?.el`, `el?.closest?.()`)
6. **XPath targets verified** - All xpath expressions target elements that exist in core views
7. **Good use of `inherit_id` refs** - All references to core view IDs are correct
8. **Appropriate dependencies** - `['crm', 'sale']` correctly declared
9. **License specified** - LGPL-3 appropriate for Odoo community module
10. **JS module declarations** - `/** @odoo-module **/` correctly placed

---

## Recommended Actions (Priority Order)

1. **Fix class attribute overwrites** - Use `add` operation or document fragility (Critical)
2. **Scope global SCSS selectors** - Remove `.o_list_view` and `.o_kanban_view` fallbacks from common-enhance.scss (High)
3. **Move CRM list styles** out of sale-kanban-enhance.scss (High)
4. **Scope sale kanban selectors** to `.ui-enhance-kanban` instead of `.o_kanban_view` (High)
5. **Remove or populate empty XML templates** (Medium)
6. **Add `application: False`** to manifest (Low)
7. **Remove empty SCSS ruleset** in sale-kanban-enhance.scss (Low)

---

## Metrics

- Type Coverage: N/A (no TypeScript)
- Test Coverage: 0% (no tests - acceptable for pure UI/CSS module)
- Linting Issues: Not run (no Python logic to lint)
- SCSS Compilation: Not validated (requires Odoo asset pipeline)

## Unresolved Questions

1. Does Odoo 18.0 `position="attributes"` support `add` / `remove` operations for class manipulation? If yes, Critical #1 and #2 have a clean fix. If not, the current hardcoded approach is the only option but should be documented.
2. Are the global SCSS overrides (zebra striping on all list views, hover on all kanban cards) intentional? If so, the module name/description should reflect that it enhances ALL backend views, not just CRM & Sale.
3. Were the empty XML template files left as stubs for future work? If so, a TODO comment would help.

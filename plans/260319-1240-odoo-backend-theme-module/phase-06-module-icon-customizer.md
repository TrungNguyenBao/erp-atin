---
phase: 6
title: "Module Icon Customizer"
status: pending
effort: 3h
depends_on: [2, 4]
---

# Phase 6: Module Icon Customizer

## Context
- [plan.md](plan.md) | Phase 2 (model defined), Phase 4 (sidebar/navbar rendering)
- Icons shown in sidebar (vertical layout) and app switcher (horizontal layout)

## Overview
Allow admins to override module icons with FontAwesome classes or custom SVG/image uploads. Icon overrides stored in `theme.flavor.icon` model. Frontend reads overrides and applies them in sidebar and app menu.

## Key Insights
- Odoo stores app icons as `web_icon_data` (base64) on `ir.ui.menu`. We do NOT modify core menus.
- Instead, `theme.flavor.icon` stores overrides per root menu. Frontend merges overrides at render time.
- FontAwesome 4.7 bundled with Odoo 18. Support FA class names like `fa-shopping-cart`.
- Custom images: stored as Binary field with attachment=True. Served via standard Odoo image URL.
- Settings UI: list of root menus with current icon preview + override controls.

## Model: `theme.flavor.icon`

Already stubbed in Phase 2. Full implementation:

```python
class ThemeFlavorIcon(models.Model):
    _name = 'theme.flavor.icon'
    _description = 'Module Icon Override'
    _rec_name = 'menu_id'

    menu_id = fields.Many2one('ir.ui.menu', string='Module',
                               required=True, ondelete='cascade',
                               domain=[('parent_id', '=', False)])
    icon_type = fields.Selection([
        ('fa', 'FontAwesome Icon'),
        ('custom', 'Custom Image'),
    ], string='Icon Type', default='fa', required=True)
    fa_icon = fields.Char('FA Class', default='fa-cube',
                           help='FontAwesome 4.7 class, e.g. fa-shopping-cart')
    fa_color = fields.Char('Icon Color', default='#FFFFFF')
    fa_bg_color = fields.Char('Background Color', default='#714B67')
    custom_icon = fields.Binary('Custom Icon', attachment=True)
    custom_icon_filename = fields.Char('Filename')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('menu_unique', 'UNIQUE(menu_id)', 'Only one icon override per module.'),
    ]
```

## Implementation Steps

### 1. Icon Management View (`views/theme-flavor-icon-views.xml`)

Tree view showing: Module name | Icon Type | Preview | Actions

```xml
<record id="theme_flavor_icon_tree" model="ir.ui.view">
    <field name="name">theme.flavor.icon.tree</field>
    <field name="model">theme.flavor.icon</field>
    <field name="arch" type="xml">
        <tree editable="bottom">
            <field name="menu_id"/>
            <field name="icon_type"/>
            <field name="fa_icon" invisible="icon_type != 'fa'"/>
            <field name="fa_color" widget="color" invisible="icon_type != 'fa'"/>
            <field name="fa_bg_color" widget="color" invisible="icon_type != 'fa'"/>
            <field name="custom_icon" widget="image" invisible="icon_type != 'custom'"
                   options="{'size': [64, 64]}"/>
        </tree>
    </field>
</record>
```

Form view for detailed editing with live preview panel.

### 2. Settings Link

In `res-config-settings-views.xml`, add button:
```xml
<button name="%(theme_flavor.action_theme_flavor_icon)d"
        type="action" string="Configure Module Icons"
        class="btn-link" icon="fa-paint-brush"/>
```

### 3. Controller Endpoint for Icon Overrides

Add to `controllers/theme_flavor_controller.py`:

```python
@http.route('/theme_flavor/icon_overrides', type='json', auth='user')
def get_icon_overrides(self):
    overrides = request.env['theme.flavor.icon'].sudo().search([('active', '=', True)])
    result = {}
    for ov in overrides:
        data = {'type': ov.icon_type}
        if ov.icon_type == 'fa':
            data['faIcon'] = ov.fa_icon
            data['faColor'] = ov.fa_color
            data['faBgColor'] = ov.fa_bg_color
        else:
            data['imageUrl'] = f'/web/image/theme.flavor.icon/{ov.id}/custom_icon'
        result[ov.menu_id.id] = data
    return result
```

### 4. Frontend: Apply Icon Overrides

In `webclient-layout-patch.js` (or dedicated `navbar-icon-patch.js`):

```javascript
// In WebClient setup, after theme service loads
async loadIconOverrides() {
    this.iconOverrides = await this.env.services.rpc('/theme_flavor/icon_overrides');
}

getAppIcon(app) {
    const override = this.iconOverrides?.[app.id];
    if (!override) return null;
    return override;
}
```

In sidebar template, check for override:
```xml
<t t-set="iconOv" t-value="getAppIcon(app)"/>
<t t-if="iconOv and iconOv.type === 'fa'">
    <span class="tf-sidebar__item-icon-fa"
          t-attf-style="background: #{iconOv.faBgColor}; color: #{iconOv.faColor};">
        <i t-attf-class="fa #{iconOv.faIcon}"/>
    </span>
</t>
<t t-elif="iconOv and iconOv.type === 'custom'">
    <img t-att-src="iconOv.imageUrl" class="tf-sidebar__item-icon"/>
</t>
<t t-else="">
    <!-- default app.webIconData -->
</t>
```

### 5. Icon Preview in Settings

In icon form view, add a computed preview field or inline OWL component showing how the icon looks in both sidebar and navbar contexts.

### 6. SCSS for FA Icon Styling (`scss/icon-customizer.scss`)

```scss
.tf-sidebar__item-icon-fa {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 5px;
  font-size: 0.75rem;
  flex-shrink: 0;
}
```

## Success Criteria
- [ ] Admin can create icon overrides for any root module menu
- [ ] FontAwesome icons render with custom color/background in sidebar
- [ ] Custom uploaded images display correctly (64x64, rounded)
- [ ] Icon overrides appear in both vertical sidebar and horizontal app switcher
- [ ] Removing override restores default icon
- [ ] SQL constraint prevents duplicate overrides per menu

## Risk Assessment
- **Low:** `ir.ui.menu` IDs differ between databases. Override ties to menu record, not hardcoded ID.
- **Low:** Custom image size. Validate on upload or resize in Python (Pillow via `image_process`).
- **Medium:** App switcher in horizontal mode uses different rendering. May need to patch `NavBar` component too. Test both layouts.

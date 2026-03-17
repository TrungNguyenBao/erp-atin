# Odoo 19.0 - Code Standards & Conventions

## Python Code Standards

### Naming Conventions

```python
# Classes: PascalCase
class AccountMove:
    pass

# Functions/Methods: snake_case
def validate_invoice(self):
    pass

# Constants: UPPER_SNAKE_CASE
MAX_BATCH_SIZE = 100
SQL_DEFAULT = psycopg2.extensions.AsIs("DEFAULT")

# Private methods: _leading_underscore
def _prepare_lines(self):
    pass

# Model names: dot.notation (snake_case with dots)
class SaleOrder(models.Model):
    _name = 'sale.order'  # NOT SaleOrder or sale_order
    _description = 'Sales Order'

# Field names: snake_case
customer_name = fields.Char()
is_archived = fields.Boolean()
```

### Type Hints (Python 3.10+)

```python
from typing import Optional, List, Dict
from collections.abc import Iterable

class AccountMove(models.Model):
    def _compute_amount(self) -> None:
        """Compute total amount."""
        pass

    def search_moves(self, domain: list, offset: int = 0) -> recordset:
        """Search for moves matching domain."""
        pass

    def get_amounts(self) -> Dict[int, float]:
        """Return mapping of move_id to amount."""
        return {move.id: move.amount_total for move in self}
```

### Imports

```python
# Standard library first
import logging
import datetime
from typing import Optional

# Third-party libraries second
import psycopg2
from lxml import etree

# Local imports last
from odoo import fields, models, api, _
from odoo.tools import float_compare
from odoo.exceptions import ValidationError
from .utils import calculate_tax
```

### Docstrings (Google Style)

```python
def reconcile_payments(self, amount_threshold: float = 0.01) -> bool:
    """Reconcile unmatched payments with outstanding invoices.

    Args:
        amount_threshold: Maximum allowed difference to consider matched.
            Defaults to 0.01 (one cent).

    Returns:
        True if reconciliation succeeded, False otherwise.

    Raises:
        ValidationError: If no valid matching partner found.
        UserError: If account configuration is incomplete.

    Example:
        >>> moves = self.env['account.move'].search([])
        >>> moves.reconcile_payments(amount_threshold=0.5)
    """
    pass
```

### Code Organization

```python
class SaleOrder(models.Model):
    """Sales order for products and services."""
    _name = 'sale.order'
    _description = 'Sales Order'
    _inherit = ['mail.thread']
    _order = 'date_order desc, id desc'

    # 1. Field Declarations (group by type)
    name = fields.Char(readonly=True)
    partner_id = fields.Many2one('res.partner', required=True)
    order_line = fields.One2many('sale.order.line', 'order_id')

    # 2. Computed Fields
    amount_total = fields.Float(compute='_compute_amount', store=True)

    # 3. Default Methods
    @api.model
    def _get_default_warehouse(self):
        return self.env['stock.warehouse'].search([], limit=1)

    # 4. Constraints (SQL and Python)
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Order name must be unique'),
    ]

    @api.constrains('amount_total')
    def _check_amount_positive(self):
        if self.amount_total < 0:
            raise ValidationError('Amount cannot be negative')

    # 5. Lifecycle Methods
    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)

    def write(self, vals):
        return super().write(vals)

    def unlink(self):
        return super().unlink()

    # 6. Search/Read Methods
    def search_read(self, domain=None, fields=None):
        return super().search_read(domain, fields)

    # 7. Action Methods (Business Logic)
    def action_confirm(self):
        """Confirm sales order and create pickings."""
        self.state = 'sale'

    # 8. Compute Methods
    @api.depends('order_line.price_subtotal')
    def _compute_amount(self):
        for record in self:
            record.amount_total = sum(l.price_subtotal for l in record.order_line)

    # 9. Onchange Methods
    @api.onchange('partner_id')
    def _onchange_partner(self):
        """Update payment terms when partner changes."""
        self.payment_term_id = self.partner_id.property_payment_term_id

    # 10. Helper Methods (private)
    def _prepare_invoice_vals(self):
        """Prepare values for invoice creation."""
        return {}
```

### API Decorators

```python
from odoo import api, models

class ResPartner(models.Model):
    @api.model
    def create(self, vals):
        """Model method - self is class, not record instance."""
        return super().create(vals)

    @api.model_create_multi
    def create(self, vals_list):
        """Batch create - efficient for multiple records."""
        return super().create(vals_list)

    @api.depends('name', 'email')
    def _compute_full_contact(self):
        """Depends decorator - recompute when dependencies change."""
        for record in self:
            record.full_contact = f"{record.name} <{record.email}>"

    @api.constrains('email')
    def _check_email_format(self):
        """Constrains decorator - validate on write/create."""
        for record in self:
            if not self._is_valid_email(record.email):
                raise ValidationError("Invalid email format")

    @api.onchange('country_id')
    def _onchange_country(self):
        """Onchange - update field on form change (client-side)."""
        if self.country_id.code == 'US':
            self.state_id = False

    @api.returns('sale.order')
    def get_sale_orders(self):
        """Returns decorator - specifies return model type."""
        return self.env['sale.order'].search([('partner_id', '=', self.id)])
```

### Error Handling

```python
from odoo.exceptions import UserError, ValidationError, AccessError

# Validation Errors - raised in constrains/onchange
raise ValidationError(_("Amount must be positive"))

# User Errors - raised for invalid business logic
if not self.account_id:
    raise UserError(_("Accounting account is required"))

# Access Errors - raised for permission violations
if not user.has_group('account.group_account_manager'):
    raise AccessError(_("You don't have permission"))

# Use _() for user-facing messages (translation support)
raise UserError(_("%(name)s is archived") % {'name': self.name})
```

### Security & SQL Injection Prevention

```python
# WRONG - SQL injection vulnerability
query = f"SELECT * FROM {table_name} WHERE id = {record_id}"
self.env.cr.execute(query)

# CORRECT - Use parameterized queries
self.env.cr.execute("SELECT * FROM %s WHERE id = %%s" % (table_name,), (record_id,))

# CORRECT - Use ORM query builder (preferred)
records = self.env[model_name].browse(record_id)

# Handle CSRF protection automatically via JSON-RPC
# Use session tokens for state-changing operations
```

## XML Standards (Views, Data, Security)

### View Definitions

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <!-- Form View: Full record editor -->
    <record id="view_sale_order_form" model="ir.ui.view">
        <field name="name">sale.order.form</field>
        <field name="model">sale.order</field>
        <field name="arch" type="xml">
            <form string="Sales Order">
                <!-- Header for status buttons -->
                <header>
                    <button name="action_confirm" type="object" class="oe_highlight"
                            string="Confirm"/>
                </header>
                <!-- Body with tabs -->
                <sheet>
                    <group>
                        <field name="name" readonly="1"/>
                        <field name="partner_id" required="1"/>
                    </group>
                    <notebook>
                        <page string="Order Lines">
                            <field name="order_line">
                                <tree editable="bottom">
                                    <field name="product_id"/>
                                    <field name="quantity"/>
                                </tree>
                            </field>
                        </page>
                    </notebook>
                </sheet>
            </form>
        </field>
    </record>

    <!-- Tree View: List of records -->
    <record id="view_sale_order_tree" model="ir.ui.view">
        <field name="name">sale.order.tree</field>
        <field name="model">sale.order</field>
        <field name="arch" type="xml">
            <tree string="Orders">
                <field name="name"/>
                <field name="partner_id"/>
                <field name="amount_total" sum="Total Amount"/>
            </tree>
        </field>
    </record>

    <!-- Search View: Filter & sort -->
    <record id="view_sale_order_search" model="ir.ui.view">
        <field name="name">sale.order.search</field>
        <field name="model">sale.order</field>
        <field name="arch" type="xml">
            <search string="Orders">
                <field name="name" filter_domain="[('name', 'ilike', self)]"/>
                <field name="partner_id"/>
                <filter name="draft" string="Draft" domain="[('state', '=', 'draft')]"/>
                <separator/>
                <group expand="0" string="Group By">
                    <filter name="by_partner" string="Partner"
                            context="{'group_by': 'partner_id'}"/>
                </group>
            </search>
        </field>
    </record>

    <!-- Action: Link model to menu -->
    <record id="action_sale_order" model="ir.actions.act_window">
        <field name="name">Sales Orders</field>
        <field name="res_model">sale.order</field>
        <field name="view_mode">tree,form</field>
        <field name="view_ids" eval="[(5, 0, 0), (0, 0, {'view_mode': 'tree', 'view_id': ref('view_sale_order_tree')})]"/>
    </record>

    <!-- Menu Item -->
    <menuitem id="menu_sale_order" name="Orders" parent="sale.menu_root"
              action="action_sale_order" sequence="10"/>
</odoo>
```

### Data Files

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo noupdate="1">  <!-- noupdate: don't overwrite after install -->
    <!-- Create/Update records -->
    <record id="payment_term_net30" model="account.payment.term">
        <field name="name">Net 30</field>
        <field name="line_ids" eval="[
            (0, 0, {
                'value': 'balance',
                'days': 30,
            }),
        ]"/>
    </record>

    <!-- Reference existing records -->
    <record id="company_rule" model="ir.rule">
        <field name="name">Company Rule</field>
        <field name="model_id" ref="model_res_partner"/>
        <field name="domain_force">[('company_id', '=', user.company_id.id)]</field>
    </record>
</odoo>
```

### Security: ir.model.access.csv

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sale_order_user,sale.order.user,model_sale_order,sale.group_sale_user,1,1,1,0
access_sale_order_manager,sale.order.manager,model_sale_order,sale.group_sale_manager,1,1,1,1
```

### Security: Row-Level Domain Rules

```xml
<record id="sale_order_multi_company_rule" model="ir.rule">
    <field name="name">Sale Order - Multi Company</field>
    <field name="model_id" ref="model_sale_order"/>
    <field name="domain_force">[('company_id', 'in', user.company_ids.ids)]</field>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="True"/>
</record>
```

## Field Definition Standards

### Common Field Patterns

```python
# Text fields
name = fields.Char(
    string='Name',              # UI label
    required=True,
    translate=True,             # Supports multiple languages
    index=True,                 # Database index for performance
)

description = fields.Text(
    string='Description',
    help='Detailed information'  # Tooltip text
)

html_content = fields.Html()    # Rich text with formatting

# Numeric fields
quantity = fields.Float(
    string='Quantity',
    default=1.0,
    digits=(10, 2),             # (total_digits, decimal_places)
)

amount = fields.Monetary(
    string='Amount',
    currency_field='currency_id'  # Links to currency field
)

# Boolean
is_active = fields.Boolean(default=True)

# Selection
state = fields.Selection(
    selection=[
        ('draft', 'Draft'),
        ('sale', 'Sales Order'),
        ('done', 'Done'),
    ],
    default='draft'
)

# Date/Time
date_order = fields.Date(default=fields.Date.today)
created_at = fields.Datetime(default=fields.Datetime.now)

# Relational fields
partner_id = fields.Many2one(
    'res.partner',              # Target model
    string='Customer',
    required=True,
    ondelete='cascade'          # Delete when partner deleted
)

order_line = fields.One2many(
    'sale.order.line',          # Target model
    'order_id',                 # Inverse field in target
    string='Order Lines'
)

category_ids = fields.Many2many(
    'product.category',
    'sale_order_category_rel',  # Junction table name
    'order_id',                 # Column in junction table
    'category_id'               # Column in junction table
)

# Computed (read-only)
amount_total = fields.Float(
    string='Total',
    compute='_compute_amount',  # Method name
    store=True,                 # Save to database
    readonly=True
)

# Related field (reference field from related record)
partner_phone = fields.Char(
    related='partner_id.phone',
    readonly=True
)

# JSON field
extra_data = fields.Json(default={})

# Binary (file upload)
document = fields.Binary(
    string='Document',
    attachment=True             # Store as attachment
)
```

## JavaScript/XML Template Standards

### JavaScript Modules

```javascript
// File: static/src/js/sale_order_form.js
import { registry } from "@web/core/registry";
import { FormController } from "@web/views/form/form_controller";

export class SaleOrderFormController extends FormController {
    async onSave() {
        console.log("Saving order...");
        return super.onSave();
    }
}

registry.category("views").add("sale_order_form", {
    Controller: SaleOrderFormController,
});
```

### XML Templates

```xml
<!-- File: static/src/xml/sale_order_buttons.xml -->
<templates id="template_sale_order_buttons" xml:space="preserve">
    <t t-name="SaleOrderButtons">
        <button class="btn btn-primary" t-on-click="confirmOrder">
            Confirm Order
        </button>
        <button class="btn btn-secondary" t-on-click="cancel">
            Cancel
        </button>
    </t>
</templates>
```

## Module Manifest Standards

```python
# File: __manifest__.py
{
    'name': 'Module Display Name',
    'version': '1.0',
    'category': 'Category/Subcategory',  # Hierarchical
    'sequence': 10,                      # Order in module list
    'summary': 'One-line description',
    'description': """
        Extended description with multiple lines.
        Supports markdown formatting.
    """,
    'author': 'Company Name',
    'website': 'https://example.com',
    'license': 'LGPL-3',

    # Dependencies
    'depends': [
        'base',          # Always include base
        'web',           # If using web interface
        'sale',          # Other addons
    ],
    'external_dependencies': {
        'python': ['requests', 'lxml'],
        'bin': ['wkhtmltopdf'],         # External programs
    },

    # Data files (loaded on install)
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/views.xml',
        'reports/report.xml',
    ],

    # Demo data (only in demo mode)
    'demo': [
        'demo/demo_data.xml',
    ],

    # Assets (CSS/JS bundling)
    'assets': {
        'web.assets_backend': [
            'module_name/static/src/scss/styles.scss',
            'module_name/static/src/js/module.js',
        ],
        'web.assets_frontend': [
            'module_name/static/src/css/frontend.css',
        ],
    },

    # Hooks
    'pre_init_hook': 'pre_init_hook',      # Before module install
    'post_init_hook': 'post_init_hook',    # After module install
    'uninstall_hook': 'uninstall_hook',    # Before uninstall

    'installable': True,
    'application': True,  # Appears in "Apps" menu
    'auto_install': False,
}
```

## Testing Standards

### Unit Tests

```python
# File: tests/test_sale_order.py
from odoo.tests import TransactionCase, tagged

@tagged('post_install', '-at_install')
class TestSaleOrder(TransactionCase):
    """Test sale.order model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Test Partner'})
        cls.product = cls.env['product.product'].create({'name': 'Test Product'})

    def test_create_sale_order(self):
        """Test creating a sale order."""
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 10,
            })],
        })
        self.assertEqual(order.state, 'draft')
        self.assertEqual(len(order.order_line), 1)

    def test_confirm_order(self):
        """Test confirming order and creating pickings."""
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })
        order.action_confirm()
        self.assertEqual(order.state, 'sale')
```

## Performance Best Practices

### ORM Operations

```python
# WRONG - N+1 query problem
for order in orders:
    print(order.partner_id.name)  # Query for each order

# CORRECT - Batch load related records
orders.partner_id  # Prefetch all partners in one query

# WRONG - Inefficient loop
for line in lines:
    line.write({'state': 'done'})  # Separate UPDATE per line

# CORRECT - Batch update
lines.write({'state': 'done'})  # Single UPDATE for all

# Use search with limit for large datasets
records = self.search([], limit=100, offset=0)  # Pagination

# Use read_group for aggregations
result = self.read_group([], ['partner_id', 'amount_total:sum'])
```

### Database Queries

```python
# WRONG - Load all fields
records = self.search_read([])

# CORRECT - Only needed fields
records = self.search_read([], ['id', 'name', 'state'])

# Use SQL directly for complex queries
self.env.cr.execute("""
    SELECT partner_id, SUM(amount_total)
    FROM sale_order
    WHERE state = 'sale'
    GROUP BY partner_id
""")
results = self.env.cr.fetchall()
```

## Version Control & Commits

### Commit Message Format

```
[FEATURE] module_name: Brief description

Longer description explaining the change, why it was made,
and any important context.

- Bullet point 1
- Bullet point 2

Fixes #123 (if applicable)
```

### Commit Types

```
[FEATURE] - New functionality
[FIX] - Bug fix
[REFACTOR] - Code restructuring
[PERF] - Performance improvement
[TEST] - Test additions/updates
[DOC] - Documentation updates
[I18N] - Translation updates
[SEC] - Security fixes
```

---

**Last Updated:** March 2026 | **Version:** Odoo 19.0 | **Compliance:** LGPL-3

# Odoo 19.0 - System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Web Browsers / Clients                        │
│            (Modern browsers, ES6+ JavaScript support)            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    HTTP/WSGI Layer                               │
│  (odoo/http.py - 2,857 lines)                                   │
│  • JSON-RPC 2.0 protocol                                        │
│  • Session management, CSRF protection                          │
│  • Gzip compression, caching                                    │
│  • Error handling, logging                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                             │
│  • Controllers (routes, views)                                  │
│  • Service layer (model, db, security, server)                 │
│  • Module system & addon loading                               │
│  • Registry per database instance                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│           Object-Relational Mapping (ORM) Layer                 │
│  (odoo/orm/ - 23 modules, ~15,000 lines)                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Models (BaseModel, Model, TransientModel)               │   │
│  │ • CRUD operations (create, read, update, delete)       │   │
│  │ • Query building with domain language                  │   │
│  │ • Computed fields, stored fields, related fields        │   │
│  │ • Constraints, validations, lifecycle hooks             │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Fields (15+ types organized into modules)               │   │
│  │ • Textual: Char, Text, Html                            │   │
│  │ • Numeric: Integer, Float, Monetary                    │   │
│  │ • Temporal: Date, Datetime                             │   │
│  │ • Relational: Many2one, One2many, Many2many            │   │
│  │ • Selection: Selection, Status                         │   │
│  │ • Binary: Binary, Image                                │   │
│  │ • Specialized: Json, Reference, Properties             │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Environment & Context                                   │   │
│  │ • User context, company context                        │   │
│  │ • Database environment per request                     │   │
│  │ • Timezone and language support                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Database Layer                                │
│  • PostgreSQL 13+ connection pool (psycopg2)                    │
│  • Transaction management (ACID)                                │
│  • SQL query generation and optimization                        │
│  • Prefetch caching (PREFETCH_MAX = 1000)                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              PostgreSQL Database                                 │
│  • Model tables with full schema                                │
│  • System tables (ir_*, res_*)                                  │
│  • Junction tables for Many2many relations                      │
│  • Audit/change tracking tables                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Module System Architecture

### Addon Structure & Lifecycle

```
addon_name/
├── __manifest__.py          ← Metadata, dependencies, hooks
│   ├── name, version, category
│   ├── depends, external_dependencies
│   ├── data (XML), demo, assets
│   └── hooks: pre_init, post_init, uninstall
│
├── models/
│   └── *.py                 ← Model definitions
│
├── views/
│   └── *.xml                ← Form, tree, search views
│
├── security/
│   ├── ir.model.access.csv  ← Field-level permissions
│   └── *.xml                ← Record-level security rules
│
├── data/
│   └── *.xml                ← Initial data fixtures
│
├── wizard/
│   └── *.py, *.xml          ← Transient models (workflows)
│
├── static/src/
│   ├── js/                  ← JavaScript modules
│   ├── xml/                 ← Client templates
│   └── scss/                ← Stylesheets
│
├── tests/
│   ├── test_*.py            ← Unit tests
│   └── tours/               ← UI test scenarios
│
└── report/
    ├── *.py                 ← Report definitions
    └── *.xml                ← Report templates
```

### Installation Sequence

```
1. Load __manifest__.py
   └─ Validate dependencies

2. Create database schema
   ├─ Register model tables
   ├─ Create fields
   └─ Create indexes

3. Load data files (data/*.xml)
   ├─ Fixtures in order
   └─ Computed field evaluation

4. Load security files
   ├─ Field-level ACL (ir.model.access)
   └─ Record-level rules (ir.rule)

5. Load views (views/*.xml)
   ├─ Form, tree, search, action definitions
   └─ Menu structure

6. Execute pre_init_hook (if defined)

7. Execute post_init_hook (if defined)

8. Module marked as INSTALLED
```

### Module Dependencies Resolution

```
Addon A depends on [B, C]
Addon B depends on [base, D]
Addon C depends on [base]
Addon D depends on [base]

Loading order:
1. base (no dependencies)
2. D (depends only on base)
3. B (depends on base, D)
4. C (depends on base)
5. A (depends on B, C)

Circular dependencies → ERROR (detected at load time)
```

## ORM Architecture Deep Dive

### Model Class Hierarchy

```
BaseModel (metaclass: MetaModel)
├── Model                    ← Persistent models (stored in DB)
│   └── inherit='model'
│
├── TransientModel           ← In-memory ephemeral models (wizards)
│   └── inherit='TransientModel'
│
└── AbstractModel            ← Base for mixins, not instantiable
    └── inherit='AbstractModel'
```

### CRUD Operations Flow

```
User Input (HTTP Request)
    ↓
Routes (http.py)
    ↓
Controllers (application code)
    ↓
ORM Methods
    ├─ create(values) → BaseModel.create()
    │   ├─ Check creation permission
    │   ├─ Validate fields (_validate_fields)
    │   ├─ Run @api.constrains methods
    │   ├─ Generate SQL INSERT
    │   ├─ Execute in transaction
    │   ├─ Trigger @api.depends (computed fields)
    │   ├─ Call @api.onchange_methods
    │   ├─ Log changes (ir.model.fields.history)
    │   └─ Return new record instance
    │
    ├─ read(fields, offset, limit)
    │   ├─ Check read permission
    │   ├─ Build domain from _default_search_domain
    │   ├─ Prefetch related records (lazy loading)
    │   ├─ Gather requested fields
    │   ├─ Execute SELECT query
    │   ├─ Format results (convert fields to Python)
    │   └─ Return list of dictionaries
    │
    ├─ write(values) → record.write()
    │   ├─ Check write permission
    │   ├─ Validate new values
    │   ├─ Run @api.constrains
    │   ├─ Generate SQL UPDATE
    │   ├─ Execute in transaction
    │   ├─ Recompute @api.depends fields
    │   ├─ Trigger ir.rule checks
    │   ├─ Log audit trail
    │   └─ Return True
    │
    └─ unlink() → records.unlink()
        ├─ Check delete permission
        ├─ Check for dependent records (CASCADE)
        ├─ Execute DELETE query
        ├─ Update related fields
        └─ Return True

    ↓
Response (JSON)
```

### Field Definition System

#### Field Type Hierarchy

```
Field (base class - odoo/orm/fields.py)
├─ Scalar Fields
│  ├─ Char (textual.py)
│  ├─ Text (textual.py)
│  ├─ Html (textual.py)
│  ├─ Integer (numeric.py)
│  ├─ Float (numeric.py)
│  ├─ Monetary (numeric.py)
│  ├─ Boolean (misc.py)
│  ├─ Date (temporal.py)
│  ├─ Datetime (temporal.py)
│  ├─ Selection (selection.py)
│  ├─ Status (selection.py)
│  ├─ Json (misc.py)
│  ├─ Binary (binary.py)
│  └─ Image (binary.py)
│
├─ Relational Fields
│  ├─ Many2one (relational.py)
│  ├─ One2many (relational.py)
│  ├─ Many2many (relational.py)
│  └─ Reference (reference.py)
│
├─ Specialized Fields
│  ├─ Computed (misc.py) - read-only, calculated on demand
│  ├─ Computed_batch (misc.py) - batch computed fields
│  ├─ Related (misc.py) - proxy to related record field
│  ├─ Id (misc.py) - record ID field
│  └─ Properties (properties.py) - dynamic field definitions
│
└─ Internal Fields (not user-accessible)
   ├─ __last_update (timestamp)
   ├─ create_date, create_uid
   ├─ write_date, write_uid
   └─ parent_path (for hierarchical models)
```

#### Field Lifecycle

```
Field Definition (in Model class)
    ↓
Field Instantiation (by MetaModel metaclass)
    ↓
Registration in Model._fields dictionary
    ↓
Database schema creation (for persistent fields)
    ├─ Column type mapping (Char → varchar, Integer → int8, etc.)
    ├─ NOT NULL constraints
    ├─ DEFAULT values
    └─ Indexes
    ↓
Request time (when field accessed):
    ├─ For stored fields: Load from DB cache/prefetch
    ├─ For computed fields: Call compute method
    ├─ For related fields: Follow relation chain
    └─ Apply field.get_value() for formatting
```

## Environment & Context System

### Environment Structure

```python
env = self.env                    # Current request environment

env.user                          # Current user (res.users)
env.company                       # Current company (res.company)
env.companies                     # All accessible companies
env.lang                          # Current language code
env.context                       # Dictionary of context variables

env['model.name']                 # Access model by technical name
env.ref('module.xml_id')          # Get record by external ID
```

### Context Variables

```python
context = {
    'lang': 'en_US',              # Language code
    'tz': 'America/New_York',     # Timezone
    'company_id': 1,              # Default company
    'allowed_company_ids': [1, 2], # Visible companies
    'force_company': 1,            # Override current company
    'group_by': 'partner_id',     # Group by field (in views)
    'bin_size': True,             # Load binary sizes only
    'no_reset_password': True,    # Skip password reset
    'uid': 1,                      # User ID
}

# Access with default
account_id = self.env.context.get('account_id')
```

## Security Model

### Three-Layer Security

#### 1. Field-Level Security (ir.model.access)

```csv
Model Level:
read   - Can view records
write  - Can modify records
create - Can create records
unlink - Can delete records

Applied per Model + Group combination
```

#### 2. Record-Level Security (ir.rule)

```xml
<record id="rule_sale_order_own_company" model="ir.rule">
    <field name="name">Sale Order - Own Company</field>
    <field name="model_id" ref="model_sale_order"/>
    <field name="domain_force">
        [('company_id', 'in', user.company_ids.ids)]
    </field>
</record>

Applied via ORM automatically:
- search() adds rule domain
- read/write/unlink checks rules
```

#### 3. API-Level Security

```python
@api.model
def search(self, domain=None):
    # Automatically appended to user domain
    if self._check_company_domain:
        domain = domain + self._check_company_domain()
    return super().search(domain)

# Sudo mode (careful!)
admin = self.env['res.users'].sudo().browse(1)  # Bypass security
```

## Database Schema Patterns

### Standard Model Table

```sql
CREATE TABLE sale_order (
    id SERIAL PRIMARY KEY,

    -- System fields (automatic)
    create_date TIMESTAMP DEFAULT now(),
    create_uid INTEGER REFERENCES res_users(id),
    write_date TIMESTAMP DEFAULT now(),
    write_uid INTEGER REFERENCES res_users(id),

    -- User-defined fields
    name VARCHAR(255) UNIQUE NOT NULL,
    state VARCHAR(50) DEFAULT 'draft',
    partner_id INTEGER NOT NULL REFERENCES res_partner(id) ON DELETE CASCADE,
    amount_total FLOAT DEFAULT 0,

    -- Indexes
    INDEX idx_sale_order_partner_id (partner_id),
    INDEX idx_sale_order_state (state),
    INDEX idx_sale_order_company_id (company_id)
);
```

### Many2many Junction Table

```sql
CREATE TABLE sale_order_product_category_rel (
    sale_order_id INTEGER NOT NULL REFERENCES sale_order(id) ON DELETE CASCADE,
    product_category_id INTEGER NOT NULL REFERENCES product_category(id) ON DELETE CASCADE,
    PRIMARY KEY (sale_order_id, product_category_id)
);
```

### System Tables

| Table | Purpose |
|-------|---------|
| **ir_model** | Model definitions registry |
| **ir_model_fields** | Field definitions for all models |
| **ir_model_fields_history** | Audit trail of all changes |
| **ir_model_data** | External ID mappings |
| **ir_rule** | Record-level security rules |
| **ir_actions** | Menu actions, window actions |
| **ir_ui_view** | View definitions (forms, trees) |
| **ir_attachment** | File attachments metadata |
| **ir_cron** | Scheduled jobs |
| **ir_server_actions** | Automated workflows |
| **res_users** | User accounts |
| **res_company** | Company records |
| **res_partner** | Customers/contacts |

## Caching Strategy

### Multi-Level Caching

```
Browser Cache (HTTP headers)
    ↓
Session Cache (in-memory, per session)
    ├─ UserContext cache
    └─ Field value cache
    ↓
Prefetch Cache (in ORM)
    ├─ Batch load up to PREFETCH_MAX=1000 records
    └─ Group by field type
    ↓
LRU Cache (in-memory, per process)
    └─ Used for expensive computations
    ↓
Database Cache (PostgreSQL)
    └─ Buffer pool, query result cache
```

### Cache Invalidation

```python
# Automatic (when write() is called)
self.write({'field': value})  # Invalidates caches for this record

# Manual invalidation
self.env.cache.invalidate()  # Clear all caches
self.invalidate_cache(['field_name'])  # Clear specific fields

# Context-aware
with self.env.context(my_context_var=True):
    # Cache respects context differences
    pass
```

## API & RPC Layer

### JSON-RPC 2.0 Protocol

```json
Request:
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "service": "object",
    "method": "execute",
    "args": ["dbname", "uid", "password", "model", "method", ...]
  },
  "id": 1
}

Response (Success):
{
  "jsonrpc": "2.0",
  "result": {...},
  "id": 1
}

Response (Error):
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32603,
    "message": "Internal error",
    "data": {"type": "ValidationError", "arguments": ["..."]}
  },
  "id": 1
}
```

### XML-RPC (Legacy)

```python
# Still supported for backward compatibility
server = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc')
models = server.execute('database', 'user_id', 'password', 'model', 'method', ...)
```

## Module Loading & Registry

### Registry per Database

```python
# Each database has its own Registry instance
registry = odoo.registry.Registry(dbname)

# Contains all loaded models for that database
registry['sale.order']              # Access model class

# Shared across all requests for same database
# Thread-safe via RLock
```

### Hot Module Reload

```
Development server detects file changes
    ↓
Server restart / module reload
    ↓
Registry cleared
    ↓
__manifest__.py re-evaluated
    ↓
Models re-registered
    ↓
Data files re-loaded (if noupdate=0)
    ↓
Views re-parsed
    ↓
Client UI refreshed
```

## Performance Optimization Techniques

### Query Optimization

```python
# BAD: N+1 query problem
for order in orders:
    print(order.partner_id.name)  # query per order

# GOOD: Batch loading
orders.mapped('partner_id')  # Loads all in one query

# Use search with limits for pagination
page_1 = self.search([], limit=50, offset=0)
page_2 = self.search([], limit=50, offset=50)
```

### Batch Operations

```python
# BAD: Individual updates
for record in records:
    record.write({'state': 'done'})

# GOOD: Batch update
records.write({'state': 'done'})  # Single UPDATE

# BAD: Individual creates
for vals in values_list:
    self.create(vals)

# GOOD: Batch create
self.create(vals_list)  # Optimized batch INSERT
```

### Lazy Loading

```python
# BAD: Load all fields
records = self.search_read([], [])  # All fields

# GOOD: Only needed fields
records = self.search_read([], ['id', 'name', 'state'])
```

## Error Handling & Transactions

### Exception Hierarchy

```
OdooException (base)
├─ ValidationError (field validation failed)
├─ UserError (business logic error, shown to user)
├─ AccessError (permission denied)
├─ LockError (concurrent modification)
├─ MissingError (record not found)
└─ ... others
```

### Transaction Management

```python
with self.env.cr.savepoint():
    # Changes here can be rolled back
    record.write({'amount': 100})
    if self._check_invalid():
        # Savepoint auto-rolls back
        pass
else:
    # Changes committed
    pass
```

## Asynchronous Processing

### Cron Jobs (ir.cron)

```xml
<record id="cron_invoice_send" model="ir.cron">
    <field name="name">Send Invoices</field>
    <field name="model_id" ref="model_account_move"/>
    <field name="state">code</field>
    <field name="code">model.action_send_invoices()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">hours</field>
    <field name="nextcall">2024-01-01 12:00:00</field>
</record>
```

### Delay/Queue

```python
# Delay execution
self.env.add_to_compute_queue('model.method', {'arg': value})

# Automatic retry with exponential backoff
```

---

**Last Updated:** March 2026 | **Version:** Odoo 19.0

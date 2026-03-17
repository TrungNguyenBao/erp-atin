# Odoo 19.0 - Codebase Summary

## Repository Structure

```
odoo/                           # Core framework & monorepo root
├── odoo/                       # Main Python package
│   ├── orm/                    # Object-Relational Mapping (custom ORM)
│   ├── models/                 # Base model classes
│   ├── fields/                 # Field type definitions
│   ├── cli/                    # Command-line interface tools
│   ├── service/                # RPC services layer
│   ├── tools/                  # Utility functions & helpers
│   ├── addons/base/            # Core base addon (models: ir.*, res.*)
│   ├── addons/test_*/          # Framework test addons (23 test modules)
│   ├── http.py                 # HTTP/WSGI layer (2,857 lines)
│   ├── sql_db.py               # Database connection management
│   ├── exceptions.py           # Exception hierarchy
│   ├── api.py                  # API decorators (@api.model, @api.depends, etc.)
│   ├── netsvc.py               # Network service layer
│   └── release.py              # Version information
│
├── addons/                     # 613 community & enterprise addons
│   ├── l10n_*/ (213)          # Localization for 100+ countries
│   ├── account_*/ (16)        # Accounting (core, EDI, taxes, payment)
│   ├── sale_*/ (28)           # Sales (orders, subscriptions, quotes)
│   ├── purchase_*/ (9)        # Purchase management
│   ├── stock_*/ (9)           # Warehouse & inventory
│   ├── mrp_*/ (11)            # Manufacturing & production
│   ├── hr_*/ (28)             # Human resources & payroll
│   ├── crm_*/ (6)             # CRM & customer management
│   ├── project_*/ (18)        # Project management
│   ├── website_*/ (55)        # Website builder & eCommerce
│   ├── pos_*/ (39)            # Point of Sale
│   ├── payment_*/ (22)        # Payment provider integrations
│   ├── auth_*/ (12)           # Authentication methods
│   ├── mail_*/ (5)            # Messaging & discussion
│   ├── mass_*/ (12)           # Mass mailing & marketing
│   ├── base_*/ (10)           # Base framework extensions
│   └── ...                    # 150+ other specialized addons
│
├── setup/                     # Installation and setup scripts
├── debian/                    # Debian/Ubuntu packaging configs
├── doc/                       # Developer documentation sources
├── .claude/                   # Claude development rules
├── .github/                   # GitHub workflows and actions
├── tests/                     # Integration tests
├── requirements.txt           # Python dependencies
├── setup.cfg                  # setuptools configuration
└── README.md                  # Project README
```

## Core Modules Statistics

| Directory | Files | Purpose |
|-----------|-------|---------|
| odoo/orm/ | 23 | Object-relational mapping system |
| odoo/cli/ | 12+ | Command-line interface tools |
| odoo/service/ | 5 | RPC services (model, db, server, security) |
| odoo/tools/ | 30+ | Utilities, caching, PDF, image processing |
| odoo/addons/base/models/ | 40+ | Core models (ir.*, res.*) |
| addons/ | 613 | Business functionality modules |

## ORM Architecture (`odoo/orm/`)

The ORM layer is the heart of Odoo. It's organized into functional modules:

### Core ORM Components (23 files, ~15,000 lines)

| File | Size | Purpose |
|------|------|---------|
| **models.py** | 7,127 L | BaseModel class, CRUD operations, query building |
| **fields.py** | 1,939 L | Base Field class, field definition and storage |
| **fields_relational.py** | - | Many2one, One2many, Many2many field types |
| **fields_temporal.py** | - | Date, Datetime field types with timezone support |
| **fields_textual.py** | - | Char, Text, Html field types |
| **fields_numeric.py** | - | Integer, Float, Monetary field types |
| **fields_selection.py** | - | Selection, Status field types |
| **fields_binary.py** | - | Binary, Image field types |
| **fields_misc.py** | - | Json, Pickle, Serialized field types |
| **fields_properties.py** | - | Properties (dynamic field definitions) |
| **fields_reference.py** | - | Reference field type (polymorphic relations) |
| **model_classes.py** | - | Model, TransientModel, AbstractModel base classes |
| **models_transient.py** | - | In-memory transient models (wizards) |
| **registry.py** | - | Model registry per database |
| **environments.py** | - | Environment class (context, user, database) |
| **domains.py** | - | Domain expression parser and evaluator |
| **commands.py** | - | Relational field command system |
| **decorators.py** | - | API decorators (@model, @depends, @returns) |
| **identifiers.py** | - | NewId, IdManager for record identification |
| **table_objects.py** | - | Query builder for complex SQL generation |
| **types.py** | - | Type hints and aliases |
| **utils.py** | - | Helper functions for ORM operations |

### Field Types Summary

**Total: 15+ distinct field types** organized into modules:

```
Field Types by Category:
├── Textual:        Char, Text, Html
├── Temporal:       Date, Datetime
├── Numeric:        Integer, Float, Monetary
├── Relational:     Many2one, One2many, Many2many
├── Selection:      Selection, Status
├── Binary:         Binary, Image
├── Specialized:    Json, Reference, Properties, Pickle
└── Computed:       Computed, Computed_batch (read-only calculated fields)
```

## HTTP/Web Layer (`odoo/http.py`)

- **Size:** 2,857 lines
- **Framework:** Werkzeug-based HTTP server
- **Protocol Support:** HTTP/1.1, JSON-RPC 2.0, XML-RPC
- **Routing:** Decorator-based URL routing with regex patterns
- **Features:**
  - Session management with secure cookies
  - CSRF protection
  - Query string parsing and validation
  - Response formatting (JSON, HTML, Binary)
  - Gzip compression
  - Error handling and logging

## CLI Tools (`odoo/cli/`)

Command-line interface provided by multiple modules:

| Command | Purpose |
|---------|---------|
| **server** | Run the Odoo application server |
| **shell** | Interactive Python shell with ORM access |
| **scaffold** | Generate new addon template |
| **db** | Database management (create, drop, list) |
| **deploy** | Deploy addons to production |
| **cloc** | Count lines of code in modules |
| **i18n** | Internationalization tools |
| **populate** | Generate demo data |
| **neutralize** | Anonymize sensitive production data |
| **obfuscate** | Hash sensitive data |
| **upgrade_code** | Assist in API upgrades |
| **module** | Module management tools |

## Service Layer (`odoo/service/`)

RPC services implementing business logic:

- **model.py** - Model operations (CRUD, search, read_group)
- **db.py** - Database lifecycle (create, upgrade, backup)
- **server.py** - Server status and statistics
- **security.py** - Authentication and access control

## Addon Module Structure

Each addon is a Python package with standard structure:

```
addon_name/
├── __manifest__.py          # Addon metadata & configuration
├── __init__.py             # Package init, imports public API
├── models/
│   ├── __init__.py
│   ├── model_name.py       # Model definition (one per file)
│   └── ...
├── views/
│   ├── model_name_views.xml        # Form/tree/list views
│   ├── model_name_actions.xml      # Actions and menus
│   └── ...
├── security/
│   ├── ir.model.access.csv         # Model access control
│   ├── security_rules.xml          # Row-level security domains
│   └── ...
├── data/
│   ├── model_data.xml              # Initial data fixtures
│   └── ...
├── wizard/
│   ├── wizard_name.py              # Transient models (workflows)
│   └── wizard_name_views.xml
├── static/
│   ├── src/
│   │   ├── js/                     # JavaScript modules
│   │   ├── xml/                    # XML templates
│   │   ├── scss/                   # Stylesheets
│   │   └── images/
│   └── tests/                      # Frontend tests
├── tests/
│   ├── test_*.py                   # Python test cases
│   └── tours/                      # UI test scenarios
├── report/
│   ├── report_name.py              # Report definition
│   └── report_name_templates.xml
├── i18n/
│   ├── messages.pot                # Translation template
│   └── es.po                       # Translated messages
└── README.md                       # Addon documentation
```

## Addon Categories (613 addons)

### By Country/Localization (213)
- **l10n_*** prefixed addons covering countries A-Z
- Each includes: tax configurations, accounting templates, regulatory compliance, bank integrations

### By Business Domain

| Domain | Count | Key Addons |
|--------|-------|-----------|
| **Accounting** | 16 | account, account_payment, account_edi, account_tax_python |
| **Sales** | 28 | sale, sale_subscription, sales_team, sale_purchase |
| **Purchase** | 9 | purchase, purchase_requisition, purchase_stock |
| **Inventory** | 9 | stock, stock_intrastat, stock_move_common, delivery |
| **Manufacturing** | 11 | mrp, mrp_byproduct, mrp_workorder, mrp_maintenance |
| **HR & Payroll** | 28 | hr, hr_payroll, hr_attendance, hr_leave, recruitment |
| **CRM** | 6 | crm, crm_phone, crm_livechat, crm_phone_validation |
| **Project Management** | 18 | project, project_todo, project_sms, project_enterprise |
| **Website & eCommerce** | 55 | website, website_sale, website_blog, website_form |
| **Point of Sale** | 39 | pos_*, pos_restaurant, pos_iot, pos_iface |
| **Payment** | 22 | payment_*, payment_stripe, payment_paypal, payment_razorpay |
| **Authentication** | 12 | auth_*, auth_oauth, auth_ldap, auth_passkey, auth_totp |
| **Marketing** | 12 | mass_mailing, mass_mail_event, mass_mail_contact_list |
| **Spreadsheet** | 15 | spreadsheet_*, spreadsheet_edition, spreadsheet_dashboard |
| **Base Extensions** | 10 | base_*, base_gengo, base_import, base_sparse_field |
| **Mail & Messaging** | 5 | mail, mail_github, mail_blacklist, mail_enterprise |
| **Services & Tools** | 100+ | Various specialized utilities, integrations, and extensions |

## Database Schema Patterns

### Standard Model Tables

Each persistent model creates:
- **{model_name}** - Main table with fields
- **{model_name}_queue** - Event queue for async processing
- **{model_name}_tag_rel** - Many2many junction table
- **ir_model_fields** - Field metadata registry

### Reserved System Tables

- **ir_model** - Model registry
- **ir_model_fields** - Field definitions
- **ir_model_data** - XML data references
- **ir_attachment** - File storage metadata
- **res_users** - User accounts
- **res_company** - Company records
- **ir_rule** - Row-level security rules
- **ir_server_actions** - Automated actions
- **ir_cron** - Scheduled jobs

## Key Technologies & Dependencies

### Python Ecosystem
- **Web Server:** Gevent + Werkzeug
- **Database:** psycopg2 (PostgreSQL 13+)
- **ORM:** Custom (not SQLAlchemy)
- **Templates:** Jinja2
- **XML Processing:** lxml
- **Crypto:** cryptography, passlib
- **PDF Generation:** reportlab, wkhtmltopdf
- **Image Processing:** Pillow
- **i18n:** Babel
- **Testing:** unittest, pytest (via test addons)

### JavaScript Ecosystem
- **Framework:** Vanilla ES6+ modules (minimal jQuery)
- **Build:** Custom asset bundling system
- **Testing:** QUnit, tour-based UI tests
- **Features:** Reactive views, client-side caching, AJAX

## Code Style & Conventions

### Python
- **Style Guide:** PEP 8 compatible with Odoo conventions
- **Naming:** snake_case for functions/variables, PascalCase for classes
- **Type Hints:** Python 3.10+ type annotations encouraged
- **Docstrings:** Google-style docstrings
- **Imports:** Group by standard library, third-party, local

### XML (Views & Data)
- **Format:** Pretty-printed, 2-space indentation
- **Root Elements:** `<odoo>`, `<data>`, `<record>`, `<field>`
- **Attributes:** id, model, name, type, string
- **Data Loading:** Sequential with noupdate="1" for safe updates

### JavaScript
- **Modules:** ES6 modules with imports/exports
- **Naming:** camelCase for functions, PascalCase for classes
- **Features:** Arrow functions, destructuring, async/await
- **Testing:** Tour-based scenarios for UI workflows

## Important Files to Know

| File | Lines | Purpose |
|------|-------|---------|
| odoo/orm/models.py | 7,127 | BaseModel - heart of ORM |
| odoo/orm/fields.py | 1,939 | Field definitions |
| odoo/http.py | 2,857 | Web server & routing |
| odoo/addons/base/models/ir_actions.py | 69,450 | Action system |
| odoo/addons/base/models/ir_attachment.py | 42,478 | File storage |
| addons/account/__manifest__.py | 142 | Accounting addon config |

## Performance Characteristics

- **Large Modules:** account (~69k), ir_attachment (~42k)
- **ORM Performance:** Optimized via:
  - Prefetch caching (PREFETCH_MAX = 1000)
  - Context-aware batching
  - SQL query optimization
  - Lazy field loading
- **Database Transactions:** ACID with automatic rollback
- **Concurrent Users:** 1000+ supported via connection pooling

## Version Management

- **Current Version:** 19.0.0 (FINAL)
- **Python Support:** 3.10, 3.11, 3.12, 3.13
- **PostgreSQL Support:** 13, 14, 15, 16
- **Release Cycle:** Annual major versions
- **Branch Strategy:** Each major version gets its own branch (e.g., 19.0, 20.0)

---

**Generated:** March 2026 | **Source:** Repository analysis of Odoo 19.0

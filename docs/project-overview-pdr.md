# Odoo 19.0 - Project Overview & Product Development Requirements

## Project Overview

**Odoo 19.0** is a complete open-source ERP (Enterprise Resource Planning) and CRM (Customer Relationship Management) suite. It provides a unified platform for managing all aspects of modern business operations including accounting, sales, inventory, manufacturing, HR, and CRM through an integrated set of modular applications.

## Key Facts

- **Status:** Production-Stable (FINAL release)
- **Version:** 19.0.0 (released with LGPL-3 license)
- **Repository:** https://github.com/odoo/odoo (branch: 19.0)
- **Author:** OpenERP S.A. (info@odoo.com)
- **License:** LGPL-3 (GNU Lesser General Public License v3)
- **Language:** Python 3.10-3.13
- **Database:** PostgreSQL 13+
- **Web Framework:** Python with Werkzeug
- **Framework Type:** Custom ORM-centric architecture built on PostgreSQL

## Target Users

1. **Business Administrators** - Manage and configure business processes, users, and workflows
2. **End Users** - Use integrated CRM, accounting, sales, inventory, and HR modules
3. **System Integrators** - Customize and extend functionality through add-ons
4. **Developers** - Extend core framework with Python modules and JavaScript components
5. **Enterprise Customers** - Deploy on-premise with full customization capabilities

## Core Architecture

Odoo is built on a three-tier architecture:

1. **ORM Layer** (odoo/orm/) - Custom Python ORM with PostgreSQL backend, multiple inheritance modes, 15+ specialized field types
2. **Web Framework** (odoo/http.py) - Werkzeug-based HTTP layer with JSON-RPC and XML-RPC support
3. **Module System** (addons/) - 613+ self-contained Python modules that provide business functionality

## Core Features

### Business Applications (23+ included modules)

| Category | Key Modules | Purpose |
|----------|-----------|---------|
| **Accounting** | account, account_payment, account_edi | Invoicing, payments, financial reporting, EDI compliance |
| **Sales** | sale, sale_purchase, sales_team | Quotations, orders, pipelines, sales analytics |
| **Inventory** | stock, stock_picking_batch, delivery | Warehouse management, stock moves, delivery optimization |
| **Manufacturing** | mrp, mrp_byproduct, mrp_workorder | Production orders, BOM, operations scheduling |
| **HR & Payroll** | hr, hr_payroll, hr_attendance, hr_org_chart | Employee management, leave, attendance, payroll |
| **CRM** | crm, crm_phone, crm_livechat | Leads, opportunities, pipelines, communication |
| **Website & eCommerce** | website, website_sale, website_rating | Online stores, product catalog, customer portal |
| **Project Management** | project, project_todo, project_sms | Projects, tasks, timesheets, collaboration |
| **Point of Sale** | pos_restaurant, pos_iot, pos_iface | Retail POS, order management, IoT integration |

### Specialized Features

- **Multi-company Support** - Manage multiple businesses from one instance
- **Multi-currency** - Handle transactions in multiple currencies
- **Multi-language** - Support for 100+ languages with automatic translations
- **Localization** - 213 country-specific addons for taxes, accounting rules, regulatory compliance
- **Authentication** - OAuth, LDAP, TOTP, passkeys, password policies
- **API & Integration** - JSON-RPC, XML-RPC, REST endpoints, webhooks
- **Reporting** - Dynamic reports, dashboards, analytics, export to Excel/PDF
- **Mobile Ready** - Responsive web interface optimized for mobile devices
- **Audit Trail** - Record all changes with who/what/when tracking

## Product Development Requirements (PDR)

### Functional Requirements

| Requirement | Description | Priority | Status |
|-------------|-------------|----------|--------|
| **Multi-tenancy** | Support multiple companies/organizations in single instance | HIGH | Implemented |
| **Field-level Security** | Control access to specific fields based on user roles | HIGH | Implemented |
| **Record-level Security** | Filter records based on company, department, user via domain rules | HIGH | Implemented |
| **Workflow Automation** | Automated actions via cron jobs, state transitions, event handlers | HIGH | Implemented |
| **Document Management** | Attach files, manage document lifecycle, OCR integration | HIGH | Implemented |
| **Email Integration** | Send/receive emails, mass mailing, discussion threads | HIGH | Implemented |
| **External API Access** | JSON-RPC for third-party integrations | HIGH | Implemented |
| **Data Import/Export** | CSV import/export with field mapping | MEDIUM | Implemented |
| **Custom Fields** | Dynamic field creation without code changes | MEDIUM | Implemented |
| **Extensible Views** | Tree, form, list, pivot, graph, kanban views; custom UI components | HIGH | Implemented |

### Non-Functional Requirements

| Requirement | Target | Status |
|-------------|--------|--------|
| **Performance** | Handle 1000+ concurrent users, sub-second response times | Implemented |
| **Scalability** | Multi-database support, read replicas, load balancing | Implemented |
| **Reliability** | ACID transactions, rollback, automatic recovery | Implemented |
| **Security** | SQL injection prevention, CSRF protection, encrypted passwords | Implemented |
| **Maintainability** | Modular architecture, clear separation of concerns | Implemented |
| **Extensibility** | Plugin system, Python/JavaScript hooks, inheritance | Implemented |
| **Data Integrity** | Constraints, validations, referential integrity | Implemented |
| **Audit Trail** | Full change history with user attribution | Implemented |

## Technical Dependencies

### Python Libraries (Core)
- **psycopg2** - PostgreSQL adapter
- **Werkzeug** - HTTP toolkit
- **lxml** - XML/HTML processing
- **Jinja2** - Template engine
- **Pillow** - Image processing
- **reportlab** - PDF generation
- **gevent** - Coroutine library for async I/O
- **passlib** - Password hashing
- **cryptography** - Encryption utilities
- **requests** - HTTP client
- **num2words** - Number-to-text conversion
- **Babel** - Internationalization
- **freezegun** - Time mocking for tests

### JavaScript Libraries
- Modern ES6+ modules
- No heavy framework dependencies (minimal jQuery)
- Spreadsheet integration for analytics

## Development Workflow

### Version Management
- **Current Stable:** 19.0
- **Release Cycle:** Annual major versions (17, 18, 19, 20...)
- **Format:** (MAJOR, MINOR, MICRO, RELEASE_LEVEL, SERIAL)
  - Example: (19, 0, 0, FINAL, 0) → "19.0"
  - Release levels: alpha < beta < candidate < final

### Module Dependencies
Each addon declares:
- **Dependencies** - Other addons required to function
- **External Dependencies** - Python/JS packages needed
- **Data Files** - XML, CSV fixtures for initial data
- **Demo Data** - Sample data for testing/training
- **Assets** - CSS/JS/SCSS bundles for different contexts

### Supported Customization
1. **Field Extensions** - Add new fields to existing models
2. **Model Inheritance** - Extend behavior via Python classes
3. **View Customization** - Modify XML view definitions
4. **Hook Functions** - `pre_init_hook`, `post_init_hook`, `uninstall_hook`
5. **Python Decorators** - Override methods with custom logic

## Success Metrics

1. **Adoption** - Users can install on standard Python 3.10+ and PostgreSQL 13+ environments
2. **Stability** - Zero breaking changes within 19.x version series
3. **Performance** - Page load times < 1 second, DB queries optimized
4. **Maintainability** - Community can extend with custom addons without core modifications
5. **Security** - Regular vulnerability patches, secure by default configurations

## Constraints & Dependencies

- **Python:** 3.10-3.13 only (no legacy Python 2)
- **PostgreSQL:** 13+ (with psycopg2 adapter)
- **Browser:** Modern browsers with ES6 support (Chrome, Firefox, Safari, Edge)
- **Storage:** Filesystem for attachments, optional S3/Azure blob storage
- **Network:** HTTPS required for production deployments

## Known Limitations

1. **Single Database Server** - No native sharding; requires application-level partitioning
2. **Real-time** - WebSocket communication limited; polling used for some features
3. **File Attachments** - Large files (>100MB) require external storage configuration
4. **Transactional Consistency** - Some async tasks may not be immediately consistent

## Future Direction (Planned)

- Enhanced mobile native apps (current: responsive web)
- Advanced AI/ML integration for forecasting
- Improved real-time collaboration features
- GraphQL API alongside JSON-RPC
- Kubernetes-native deployment options

## How to Get Started

### Installation
```bash
python3 -m odoo.cli.server --addons-path=addons --db_user=odoo --database=odoo
```

### For Developers
1. Clone repository: `git clone https://github.com/odoo/odoo.git --branch 19.0`
2. Install dependencies: See `requirements.txt`
3. Create addon: `odoo scaffold my_addon addons`
4. Run tests: `python3 -m pytest odoo/addons/test_*/tests/`

### Documentation
- **Developer docs:** https://www.odoo.com/documentation/19.0/developer/
- **User guides:** https://www.odoo.com/documentation/19.0/applications/
- **API reference:** Built-in via `/web/api_doc` on running instance

---

**Last Updated:** March 2026 | **Maintained By:** Odoo Development Team

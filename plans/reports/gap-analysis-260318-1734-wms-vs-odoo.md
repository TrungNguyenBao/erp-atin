# WMS vs Odoo Gap Analysis Report

**Date:** 2026-03-18 | **Source:** user-storie-wms.md (38 stories, 10 epics)
**Modules Analyzed:** purchase, purchase_requisition, stock, repair, maintenance

---

## Summary

| Category | Total Stories | ✅ Covered | ⚠️ Partial | ❌ Gap |
|----------|-------------|-----------|-----------|-------|
| Epic 1: Purchase Request (PR) | 4 | 0 | 0 | 4 |
| Epic 2: Purchase Order (PO) | 3 | 1 | 2 | 0 |
| Epic 3: GRN (Goods Received Note) | 6 | 2 | 3 | 1 |
| Epic 4: Outbound | 4 | 3 | 1 | 0 |
| Epic 5: Reservation theo dự án | 2 | 0 | 1 | 1 |
| Epic 6: Device Lifecycle | 4 | 0 | 1 | 3 |
| Epic 7: Warranty & Maintenance | 4 | 0 | 3 | 1 |
| Epic 8: Reports | 4 | 1 | 1 | 2 |
| Epic 9: Internal Controls & Audit | 4 | 4 | 0 | 0 |
| Epic 10: Dashboard & PMS Integration | 3 | 0 | 2 | 1 |
| **TOTAL** | **38** | **11** | **14** | **13** |

**Coverage: 29% full, 37% partial, 34% gap**

---

## Detailed Story-by-Story Mapping

### ✅ FULLY COVERED (11 stories — no work needed)

| ID | Story | Odoo Feature |
|----|-------|--------------|
| US-006 | Phê duyệt PO và gửi NCC | purchase.order: double validation (po_double_validation), button_confirm/approve, action_rfq_send, PDF export |
| US-009 | Scan Serial khi nhập | stock.move.line: lot_id (serial tracking), use_create_lots=True on incoming picking type, barcode module |
| US-010 | Nhập phụ kiện (Non-serial) | stock.move.line: quantity field for non-tracked products, partial receipt support |
| US-012 | Cancel GRN | stock.picking: button_cancel on draft/confirmed pickings |
| US-015 | Xuất kho Serial-based | stock.move.line: lot_id with use_existing_lots=True on outgoing, serial validation |
| US-016 | Xuất kho Non-serial | stock.move: quantity dispatch for non-tracked products |
| US-017 | Hoàn tất Outbound Order | stock.picking: button_validate completes transfer, creates stock.quant updates |
| US-028 | Báo cáo tồn kho tổng hợp | stock.quant: qty_available/virtual_available, report.stock.quantity SQL view, warehouse/product filters |
| US-032 | Audit Log toàn diện | mail.tracking.value: field change tracking, mail.message chatter, complete action history |
| US-033 | Lock chứng từ sau hoàn tất | purchase.order: done state (po_lock), stock.picking: done state makes fields readonly |
| US-034 | Không cho xóa — chỉ Cancel | Odoo standard: confirmed records can't be deleted, cancel workflows available, active field for archiving |

### ⚠️ PARTIALLY COVERED (14 stories — cần enhance)

| ID | Story | What Exists | Gap |
|----|-------|-------------|-----|
| US-005 | Tạo PO từ PR | purchase.order creation full-featured, RFQ wizard | Missing: PR→PO link since PR model doesn't exist. Direct PO creation works fine |
| US-007 | Theo dõi trạng thái PO | qty_received on order lines, receipt tracking | Missing: PARTIALLY_RECEIVED auto-status. PO stays in 'purchase' state. No progress bar per line |
| US-008 | Tạo GRN từ PO | stock.picking auto-created when PO confirmed (incoming receipt) | Missing: DRAFT→RECEIVING→COMPLETED explicit states. Odoo picking states differ (draft→confirmed→assigned→done) |
| US-011 | Complete GRN — Sinh tồn kho | stock.picking validation creates quant updates | Missing: device_instance concept. Odoo uses stock.quant not transaction-based inventory. Serial validation on complete exists |
| US-013 | Cảnh báo GRN quá lâu | stock.picking has scheduled_date, late picking counts on picking type dashboard | Missing: configurable 48h threshold alert. No background job for overdue notification |
| US-014 | Tạo Outbound Order | stock.picking outgoing works with picking types | Missing: 5 outbound types (PROJECT_OUT, POC_OUT, INTERNAL_USE, PARTNER_LOAN_OUT, MAINTENANCE_OUT). Only generic outgoing type exists |
| US-018 | Reserve thiết bị cho dự án | stock.quant.reserved_quantity exists, reservation at picking confirmation | Missing: project-level reservation of specific serials. Odoo reserves by product/qty not by serial+project |
| US-020 | Xem Device Detail & History | stock.lot: serial record with quant_ids, move history. stock.traceability.report | Missing: device lifecycle states (IN_STOCK/RESERVED/DEPLOYED etc.), status_history timeline, project/site fields |
| US-023 | Retire thiết bị | stock.scrap model exists for removing from inventory. maintenance.equipment.scrap_date | Missing: RETIRED status concept preserving serial record. Scrap removes from inventory, doesn't keep lifecycle |
| US-024 | Tạo Warranty Ticket | maintenance.request (corrective type), repair.order. maintenance.equipment.warranty_date | Missing: auto warranty_covered check from activation date. No link serial→equipment→warranty automatic. Device status→MAINTENANCE transition |
| US-025 | Xử lý bảo hành — Sửa chữa | repair.order: full repair workflow with parts add/remove/recycle | Missing: return device to original project. No project_id on repair. No auto-restore deployment status |
| US-026 | Xử lý bảo hành — Đổi thiết bị | repair.order exists but no swap/replace workflow | Missing: device replacement flow (old→RETIRED, new→DEPLOYED+same project). Needs custom wizard |
| US-030 | Truy xuất lịch sử serial | stock.traceability.report: lot movement history | Missing: full lifecycle timeline (PO→GRN→IN_STOCK→RESERVED→DEPLOYED→ACTIVATED). Only tracks stock moves, not device states |
| US-036 | Warehouse Dashboard | stock.picking.type kanban with count_picking_draft/ready/late | Missing: unified KPI dashboard with alerts, warranty expiry warnings, quick actions, recent transactions feed |

### ❌ NOT COVERED (13 stories — cần build mới)

| ID | Story | Gap Description | Effort |
|----|-------|----------------|--------|
| US-001 | Tạo Purchase Request | Không có PR model. purchase.requisition là Purchase Agreement (blanket order), hoàn toàn khác concept. Cần model mới purchase.request với DRAFT→SUBMITTED→APPROVED flow | Medium |
| US-002 | Submit PR để phê duyệt | Không có submission workflow cho PR. Cần state machine + field locking | Low |
| US-003 | Phê duyệt / Từ chối PR | Không có approval workflow cho PR. Cần approve/reject actions + rejection reason | Medium |
| US-004 | Xem danh sách PR | Không có PR model → không có list/kanban views. Cần tree/form/search views | Low |
| US-019 | Xem thiết bị reserved theo dự án | Không có project↔device relationship. Odoo reservation là product-level, không serial-level | Medium |
| US-021 | Cập nhật DEPLOYED status | Không có deployment tracking. stock.lot không có site, install_date, deployment status fields | Medium |
| US-022 | Kích hoạt AI (ACTIVATED) | Không có activation concept. Firmware version, AI license, warranty_start_date auto-calculation không tồn tại | Medium |
| US-027 | Xem warranty tickets + failure rate | maintenance.request list có nhưng thiếu failure rate calculation per model. Cần SQL report hoặc custom view | Medium |
| US-029 | Báo cáo serial theo dự án | Không có project link trên serial/lot. Cần project_id field trên stock.lot + custom report | Medium |
| US-031 | Báo cáo bảo hành | Không có warranty report. Failure rate by model, warranty expiry forecast không tồn tại | Medium |
| US-035 | Phân quyền theo Role | Odoo có groups (stock.group_stock_user/manager, purchase.group) nhưng thiếu Warehouse-specific roles: Warehouse Keeper, Procurement Staff, PM, Technician, Warranty Staff, Viewer | Medium |
| US-037 | Tích hợp PMS — Liên kết thiết bị với dự án | Không có cross-module link project.project ↔ stock.lot/device. Cần bridge module | High |
| US-038 | Reverse Transaction cho GRN | Return picking tồn tại nhưng khác concept. Cần REVERSED status + validation (chỉ reverse nếu devices vẫn IN_STOCK) + custom wizard | Medium |

---

## Key Architecture Differences: WMS vs Odoo

| WMS Concept | Odoo Equivalent | Compatibility |
|-------------|----------------|---------------|
| Purchase Request (PR) | purchase.requisition (Purchase Agreement) | ❌ Different concept — need new model |
| Purchase Order (PO) | purchase.order | ✅ Compatible — minor extensions |
| GRN (Goods Received Note) | stock.picking (incoming) | ⚠️ Similar workflow — different states |
| Outbound Order | stock.picking (outgoing) | ⚠️ Generic — need typed pickings |
| inventory_transaction | stock.quant (snapshot) + stock.move (changes) | ⚠️ Different pattern — Odoo uses quant-based not sum-of-transactions |
| device_instance | stock.lot + maintenance.equipment | ⚠️ Split across models — need unifying |
| device_status (lifecycle) | Không tồn tại | ❌ Need custom field + history |
| Warranty Ticket | maintenance.request + repair.order | ⚠️ Exists but separate — need linking |
| Project ↔ Device link | Không tồn tại | ❌ Need bridge model |

### Critical Design Decision: inventory_transaction vs stock.quant

WMS yêu cầu **transaction-based inventory**: `stock = SUM(inventory_transaction)`. Odoo sử dụng **snapshot-based**: `stock.quant` lưu current quantity trực tiếp, stock.move logs changes.

**Recommendation:** Sử dụng Odoo's native stock.quant system. Không cần custom inventory_transaction table vì:
- stock.move + stock.move.line đã log mọi movements (equivalent transactions)
- stock.quant cho query tồn kho nhanh hơn SUM()
- stock.traceability.report đã có traceability
- Backward-compatible với tất cả Odoo stock features (forecasting, reordering, etc.)

---

## Implementation Priority Matrix

### Tier 1: Foundation Models (Sprint 1-2, ~2 weeks)

| Feature | Stories | New/Extend | Effort |
|---------|---------|------------|--------|
| Purchase Request model | US-001, 002, 003, 004 | New model: `purchase.request` + `purchase.request.line` | 5 days |
| RBAC roles setup | US-035 | Extend Odoo groups with WMS-specific roles | 2 days |
| PO from PR link | US-005 (partial) | Extend purchase.order: `request_id` field | 1 day |

### Tier 2: Outbound Types & GRN Enhancement (Sprint 2-3, ~1.5 weeks)

| Feature | Stories | New/Extend | Effort |
|---------|---------|------------|--------|
| Typed outbound pickings | US-014 | 5 custom picking types + outbound_type field | 2 days |
| GRN state enhancement | US-008, 013 | Extend stock.picking: RECEIVING state, 48h alert cron | 3 days |
| PO tracking enhance | US-007 | Extend purchase.order: auto partial_received status + progress | 2 days |
| GRN reverse | US-038 | Custom wizard: validate IN_STOCK + reverse transactions | 2 days |

### Tier 3: Device Lifecycle (Sprint 3-4, ~2 weeks)

| Feature | Stories | New/Extend | Effort |
|---------|---------|------------|--------|
| Device lifecycle states | US-020, 021, 022, 023 | Extend stock.lot: device_status Selection field + status history model | 5 days |
| Project ↔ Device link | US-018, 019, 037 | New field: stock.lot.project_id + reservation wizard | 3 days |
| Device detail views | US-020 | Extend stock.lot form: lifecycle timeline, project info, warranty | 2 days |

### Tier 4: Warranty System (Sprint 4-5, ~1.5 weeks)

| Feature | Stories | New/Extend | Effort |
|---------|---------|------------|--------|
| Warranty ticket enhance | US-024, 025, 026, 027 | Extend repair.order: device serial link, warranty check, replace wizard | 5 days |
| Warranty reports | US-031 | SQL view: failure rate by model, expiry forecast | 2 days |

### Tier 5: Reports & Dashboard (Sprint 5-6, ~2 weeks)

| Feature | Stories | New/Extend | Effort |
|---------|---------|------------|--------|
| Project device report | US-029 | SQL view: serial list by project with status KPI | 2 days |
| Serial traceability enhance | US-030 | Extend stock.traceability: include device lifecycle states + linked docs | 3 days |
| Warehouse Dashboard | US-036 | Custom OWL component: KPI cards, alerts, quick actions | 5 days |

---

## Recommended Implementation Order

```
Phase 1 (Sprint 1-2): Foundation
├── US-035: RBAC roles (Warehouse Keeper, Procurement, PM, etc.)
├── US-001~004: Purchase Request model + CRUD + approval
├── US-005: PO from PR link
└── US-007: PO tracking enhancement

Phase 2 (Sprint 2-3): Core Warehouse Operations
├── US-008: GRN state enhancement (RECEIVING concept)
├── US-014: 5 outbound picking types
├── US-013: GRN overdue alert (cron job)
└── US-038: GRN reverse wizard

Phase 3 (Sprint 3-4): Device Lifecycle
├── US-020: Device detail (extend stock.lot)
├── US-021: DEPLOYED status + site info
├── US-022: ACTIVATED status + warranty auto-start
├── US-023: RETIRED status (soft-retire, keep serial)
├── US-018: Project-based device reservation
└── US-019: View reserved devices per project

Phase 4 (Sprint 4-5): Warranty & Maintenance
├── US-024: Warranty ticket with auto-warranty check
├── US-025: Repair + return to project flow
├── US-026: Device replacement wizard
└── US-027: Warranty ticket list + failure rate

Phase 5 (Sprint 5-6): Reports & Dashboard
├── US-028: (Already covered — verify)
├── US-029: Serial by project report
├── US-030: Enhanced serial traceability
├── US-031: Warranty report
├── US-036: Warehouse KPI Dashboard
└── US-037: PMS integration (Devices tab on project)
```

---

## Architecture Decision: Module Structure

**Recommendation:** Create 2 new modules:

### 1. `purchase_request` (standalone)
- New model: `purchase.request`, `purchase.request.line`
- Depends on: `purchase`
- Approval workflow: DRAFT → SUBMITTED → APPROVED/REJECTED
- Action: Create PO from approved PR

### 2. `warehouse_device_lifecycle` (main WMS module)
- Depends on: `stock`, `purchase`, `repair`, `maintenance`, `project`
- Extends: `stock.lot` (device status, project link, warranty dates)
- New models: `device.status.history`, `warehouse.outbound.type`
- Extends: `stock.picking` (GRN enhancements, outbound types)
- Extends: `repair.order` (warranty check, device replacement)
- Custom views: Device detail, Project devices tab, Dashboard
- SQL reports: failure rate, serial by project, warranty expiry

**Reasons:**
- Separate PR module = reusable across companies without WMS
- Device lifecycle module = core WMS functionality bundled together
- Both can install independently
- Clean dependency tree

---

## Comparison with PMS Gap Analysis

| Metric | PMS | WMS |
|--------|-----|-----|
| Total Stories | 38 | 38 |
| Fully Covered | 27 (71%) | 11 (29%) |
| Partially Covered | 6 (16%) | 14 (37%) |
| Gaps | 5 (13%) | 13 (34%) |
| Estimated Effort | ~4 sprints | ~6 sprints |
| New Models Needed | 1 (project.goal) | 3+ (purchase.request, device.status.history, etc.) |

**Conclusion:** WMS has significantly more gaps than PMS because the user stories are highly specialized for AI camera device lifecycle management. Odoo's stock module provides a solid foundation for inventory operations, but device lifecycle tracking, project-device linking, and the Purchase Request workflow all need to be built from scratch.

---

## Unresolved Questions

1. **inventory_transaction pattern**: Accept Odoo's stock.quant pattern or build custom transaction-based layer? (Recommendation: use stock.quant)
2. **stock.lot vs maintenance.equipment**: Unify device tracking on stock.lot or create bridge? (Recommendation: extend stock.lot, link to maintenance.equipment via serial_no match)
3. **Helpdesk module**: Odoo Enterprise has helpdesk — available? If so, warranty tickets could use helpdesk instead of maintenance.request
4. **Barcode module**: Is `stock_barcode` (Enterprise) available for serial scanning UI, or need custom barcode input?
5. **PMS integration depth**: How tightly coupled should project↔device be? Separate tab vs embedded views?
6. **Multi-warehouse**: WMS implies single warehouse — confirm? Odoo supports multi-warehouse natively

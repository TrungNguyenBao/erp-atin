

**ODOO 18 COMMUNITY**

**AGILE / SCRUM**

**PROJECT MANAGEMENT MODULE**

**KẾ HOẠCH PHÁT TRIỂN & ROADMAP CODING**

| Phiên bản: | Odoo 18 Community Edition |
| ----: | :---- |
| **Framework:** | Scrum (Sprint-based Agile) |
| **Tác giả:** | David |
| **Ngày:** | 20/03/2026 |
| **Trạng thái:** | Draft v1.0 |

# **MỤC LỤC**

# **1\. TỔNG QUAN DỰ ÁN (EXECUTIVE SUMMARY)**

## **1.1 Mục tiêu dự án**

Dự án nhằm xây dựng module mở rộng cho Odoo 18 Community Edition, bổ sung đầy đủ tính năng quản lý dự án theo mô hình Scrum/Agile. Module sẽ kế thừa (inherit) trực tiếp từ module Project có sẵn, giữ nguyên các tính năng hiện tại và bổ sung thêm các khái niệm Scrum cần thiết.

## **1.2 Phạm vi (Scope)**

* Sprint Management: Tạo, quản lý, theo dõi các Sprint với thời gian time-boxed (1–4 tuần)

* Product Backlog & Sprint Backlog: Phân loại, ưu tiên hóa và kéo thả task vào Sprint

* Story Points & Estimation: Đánh giá độ phức tạp bằng story points (Fibonacci)

* User Story & Epic: Phân cấp bậc Epic \> User Story \> Task \> Sub-task

* Scrum Roles: Phân quyền Scrum Master, Product Owner, Development Team

* Burndown Chart & Velocity: Biểu đồ theo dõi tiến độ Sprint và năng suất đội nhóm

* Scrum Ceremonies: Hỗ trợ Sprint Planning, Daily Standup, Sprint Review, Retrospective

* Agile Dashboard: Trang tổng quan thị giác hóa các chỉ số Agile

## **1.3 Ngoài phạm vi (Out of Scope)**

* Tích hợp với các công cụ CI/CD bên ngoài (Jenkins, GitLab CI)

* Mobile app riêng biệt (sử dụng responsive web)

* Module kế toán/tài chính dự án (sử dụng module hiện có)

## **1.4 Công nghệ sử dụng**

| Thành phần | Công nghệ | Mô tả |
| :---- | :---- | :---- |
| Backend | Python 3.10+, Odoo ORM | Models, controllers, business logic |
| Frontend | OWL Framework (Odoo 18\) | Reactive components, QWeb templates |
| Database | PostgreSQL 14+ | Odoo ORM tự quản lý schema |
| Views | XML (QWeb) | Form, Kanban, List, Graph views |
| Styles | SCSS | Custom styling cho Sprint Board |
| Charts | Chart.js / OWL | Burndown, Velocity charts |

# **2\. PHÂN TÍCH KHOANG CÁCH (GAP ANALYSIS)**

Bảng dưới đây so sánh giữa tính năng hiện có của module Project Odoo 18 và yêu cầu Scrum cần bổ sung:

| TÍnh năng | Odoo 18 hiện tại | Yêu cầu Scrum | Hành động |
| :---- | :---- | :---- | :---- |
| Kanban Board | ✅ Có sẵn | ✅ Đạt | Tái sử dụng, thêm group by Sprint |
| Task Stages | ✅ Có sẵn | ✅ Đạt | Giữ nguyên, bổ sung Scrum stages mặc định |
| Milestone | ✅ Có sẵn | ✅ Đạt | Map milestone \= Sprint goal |
| Sub-tasks | ✅ Có sẵn | ✅ Đạt | Sử dụng cho task breakdown |
| Sprint Management | ❌ Không có | ⚠️ Cần thiết | Tạo model project.sprint mới |
| Story Points | ❌ Không có | ⚠️ Cần thiết | Thêm field vào project.task |
| Product Backlog | ❌ Không có | ⚠️ Cần thiết | Task không gán sprint \= Backlog |
| Epic / User Story | ❌ Không có | ⚠️ Cần thiết | Tạo model project.epic mới |
| Burndown Chart | ❌ Không có | ⚠️ Cần thiết | OWL component \+ Chart.js |
| Velocity Tracking | ❌ Không có | ⚠️ Cần thiết | Computed fields \+ Graph view |
| Scrum Roles | ❌ Không có | ⚠️ Cần thiết | Security groups mới |
| Scrum Ceremonies | ❌ Không có | Nên có | Tạo model ceremony tracking |

# **3\. KIẾN TRÚC MODULE (ARCHITECTURE DESIGN)**

## **3.1 Cấu trúc thư mục module**

project\_scrum/  
├── \_\_init\_\_.py  
├── \_\_manifest\_\_.py  
├── models/  
│   ├── \_\_init\_\_.py  
│   ├── project\_sprint.py          \# Sprint model  
│   ├── project\_epic.py            \# Epic model  
│   ├── project\_task.py            \# Task inheritance (story points, sprint)  
│   ├── project\_project.py         \# Project inheritance (Scrum settings)  
│   ├── scrum\_ceremony.py          \# Ceremony tracking  
│   └── sprint\_velocity.py         \# Velocity computed model  
├── views/  
│   ├── project\_sprint\_views.xml   \# Sprint form/kanban/list  
│   ├── project\_epic\_views.xml     \# Epic views  
│   ├── project\_task\_views.xml     \# Task view inheritance  
│   ├── project\_project\_views.xml  \# Project view inheritance  
│   ├── scrum\_ceremony\_views.xml   \# Ceremony views  
│   ├── sprint\_dashboard.xml       \# Dashboard action  
│   └── menus.xml                  \# Menu items  
├── wizard/  
│   ├── \_\_init\_\_.py  
│   ├── sprint\_planning\_wizard.py  \# Sprint planning wizard  
│   └── sprint\_planning\_wizard.xml  
├── report/  
│   ├── sprint\_report.py           \# Sprint report data  
│   └── sprint\_report\_template.xml \# QWeb PDF template  
├── security/  
│   ├── security.xml               \# Security groups  
│   ├── ir.model.access.csv        \# Access rights  
│   └── ir\_rule.xml                \# Record rules  
├── static/  
│   └── src/  
│       ├── js/  
│       │   ├── sprint\_board.js        \# Sprint Board OWL component  
│       │   ├── burndown\_chart.js      \# Burndown Chart widget  
│       │   ├── velocity\_chart.js      \# Velocity Chart widget  
│       │   └── agile\_dashboard.js     \# Agile Dashboard  
│       ├── xml/  
│       │   ├── sprint\_board.xml       \# QWeb templates  
│       │   ├── burndown\_chart.xml  
│       │   └── agile\_dashboard.xml  
│       └── scss/  
│           └── sprint\_board.scss      \# Styles  
├── data/  
│   ├── project\_stage\_data.xml     \# Default Scrum stages  
│   └── scrum\_data.xml             \# Default data  
└── tests/  
    ├── \_\_init\_\_.py  
    ├── test\_sprint.py             \# Sprint unit tests  
    ├── test\_backlog.py            \# Backlog tests  
    └── test\_velocity.py           \# Velocity calculation tests

## **3.2 Data Models (Database Schema)**

Dưới đây là thiết kế chi tiết các model chính của module project\_scrum, bao gồm cả quan hệ giữa các model và các field cụ thể:

### **3.2.1 project.sprint (Sprint)**

Model chính đại diện cho một Sprint – chu kỳ làm việc cố định (thường 2 tuần).

| Field | Type | Required | Mô tả |
| :---- | :---- | ----- | :---- |
| **name** | Char | ✅ | Tên Sprint (VD: Sprint 1, Sprint 2\) |
| **project\_id** | Many2one (project.project) | ✅ | Dự án chứa Sprint |
| **state** | Selection | ✅ | draft / active / review / done / cancelled |
| **date\_start** | Date | ✅ | Ngày bắt đầu Sprint |
| **date\_end** | Date | ✅ | Ngày kết thúc Sprint |
| **goal** | Text |  | Mục tiêu Sprint (Sprint Goal) |
| **scrum\_master\_id** | Many2one (res.users) |  | Scrum Master phụ trách |
| **task\_ids** | One2many (project.task) |  | Danh sách task trong Sprint |
| **total\_story\_points** | Integer (computed) |  | Tổng story points của Sprint |
| **completed\_story\_points** | Integer (computed) |  | Story points đã hoàn thành |
| **velocity** | Float (computed) |  | Tỷ lệ hoàn thành \= completed/total |
| **burndown\_data** | Text (computed) |  | JSON data cho burndown chart |
| **daily\_log\_ids** | One2many |  | Log hàng ngày cho burndown |

### **3.2.2 project.epic (Epic)**

Epic là nhóm các User Story lớn, đại diện cho một tính năng lớn cần nhiều Sprint để hoàn thành.

| Field | Type | Required | Mô tả |
| :---- | :---- | ----- | :---- |
| **name** | Char | ✅ | Tên Epic |
| **description** | Html |  | Mô tả chi tiết |
| **project\_id** | Many2one (project.project) | ✅ | Dự án |
| **state** | Selection | ✅ | new / in\_progress / done |
| **owner\_id** | Many2one (res.users) |  | Product Owner sở hữu |
| **task\_ids** | One2many (project.task) |  | Danh sách User Story/Task |
| **color** | Integer |  | Màu hiển thị trên Kanban |
| **priority** | Selection |  | 0-3 (Low/Medium/High/Critical) |
| **progress** | Float (computed) |  | % hoàn thành dựa trên task |

### **3.2.3 project.task (Inherited – Mở rộng)**

Mở rộng model project.task có sẵn bằng cách thêm các field Scrum vào:

| Field mới | Type | Mô tả |
| :---- | :---- | :---- |
| **sprint\_id** | Many2one (project.sprint) | Sprint chứa task này (null \= Backlog) |
| **epic\_id** | Many2one (project.epic) | Epic cha của task |
| **story\_points** | Integer | Điểm câu chuyện (1, 2, 3, 5, 8, 13, 21\) |
| **task\_type** | Selection | epic / story / task / bug / improvement |
| **acceptance\_criteria** | Text | Tiêu chí chấp nhận (Definition of Done) |
| **is\_blocked** | Boolean | Task bị block bởi dependency |
| **blocked\_reason** | Text | Lý do bị block |
| **estimated\_hours** | Float | Giờ ước tính |
| **actual\_hours** | Float (computed) | Giờ thực tế (từ timesheet) |

### **3.2.4 scrum.ceremony (Scrum Ceremony)**

Model theo dõi các sự kiện Scrum: Sprint Planning, Daily Standup, Sprint Review, và Retrospective.

| Field | Type | Mô tả |
| :---- | :---- | :---- |
| **name** | Char | Tên buổi họp |
| **sprint\_id** | Many2one (project.sprint) | Sprint liên quan |
| **ceremony\_type** | Selection | planning / daily / review / retrospective |
| **date** | Datetime | Thời gian diễn ra |
| **duration** | Float | Thời lượng (giờ) |
| **attendee\_ids** | Many2many (res.users) | Người tham gia |
| **notes** | Html | Ghi chú buổi họp |
| **action\_items** | Text | Các hành động cần thực hiện |
| **went\_well** | Text | Retro: Điều gì tốt |
| **to\_improve** | Text | Retro: Cần cải thiện gì |

## **3.3 Entity Relationship (Quan hệ giữa các Model)**

Sơ đồ quan hệ giữa các model chính:

project.project  
    │  
    ├── 1:N ──► project.sprint  
    │              │  
    │              ├── 1:N ──► project.task (sprint\_id)  
    │              ├── 1:N ──► scrum.ceremony  
    │              └── 1:N ──► sprint.daily.log  
    │  
    ├── 1:N ──► project.epic  
    │              │  
    │              └── 1:N ──► project.task (epic\_id)  
    │  
    └── 1:N ──► project.task  (kế thừa Odoo gốc)  
                   │  
                   └── N:1 ──► res.users (assignee)

## **3.4 Security Groups**

Module sẽ tạo 3 nhóm quyền mới kế thừa từ các nhóm Project hiện có:

| Security Group | Quyền hạn | Kế thừa từ |
| :---- | :---- | :---- |
| **Scrum User** | Xem sprint, task, epic Tự assign task vào sprint Cập nhật story points, trạng thái task | project.group\_project\_user |
| **Scrum Master** | Tạo/sửa/xóa Sprint Quản lý ceremonies Xem burndown, velocity charts Di chuyển task giữa các sprint | project\_scrum.group\_scrum\_user |
| **Product Owner** | Quản lý Product Backlog Tạo/sửa Epic Ưu tiên hóa backlog Chấp nhận/từ chối User Story | project\_scrum.group\_scrum\_master |

# **4\. THIẾT KẾ CHỨC NĂNG (FUNCTIONAL DESIGN)**

## **4.1 Sprint Lifecycle (Vòng đời Sprint)**

Mỗi Sprint trải qua các trạng thái sau, được kiểm soát bằng state machine:

  \[draft\] ──► \[active\] ──► \[review\] ──► \[done\]  
    │                              │  
    └──── \[cancelled\] ◄─────────┘

* Draft: Sprint được tạo, chưa bắt đầu. Team kéo task từ Backlog vào.

* Active: Sprint đang chạy. Team làm việc trên các task. Burndown chart cập nhật hàng ngày.

* Review: Sprint kết thúc, đang review. Task chưa xong sẽ được chuyển về Backlog hoặc Sprint tiếp theo.

* Done: Sprint hoàn tất. Velocity được tính toán và lưu trữ.

* Cancelled: Sprint bị hủy (trường hợp đặc biệt). Task tự động quay về Backlog.

## **4.2 Sprint Board (Bảng Sprint)**

Sprint Board là giao diện chính để team theo dõi công việc hàng ngày. Được xây dựng bằng OWL component, bao gồm:

* Kanban columns: To Do | In Progress | In Review | Done

* Drag-and-drop task giữa các cột

* Hiển thị story points trên mỗi task card

* Sprint selector ở header

* Mini burndown chart ở sidebar

* WIP (Work In Progress) limit indicator

## **4.3 Product Backlog Management**

Product Backlog là danh sách tất cả các task/user story chưa được gán vào Sprint nào (sprint\_id \= null). Giao diện Backlog cho phép:

* Sắp xếp backlog theo priority (drag-and-drop reorder)

* Lọc theo Epic, Task Type, Story Points

* Bulk assign task vào Sprint (multi-select \+ wizard)

* Quick create User Story với inline form

* Hiển thị tổng story points của Backlog

## **4.4 Burndown Chart**

Burndown Chart hiển thị lượng công việc còn lại theo thời gian trong Sprint. Được xây dựng bằng OWL \+ Chart.js:

* Trục X: các ngày trong Sprint (date\_start → date\_end)

* Trục Y: Story points còn lại

* Đường lý tưởng (Ideal line): đường thẳng từ total\_sp xuống 0

* Đường thực tế (Actual line): từ dữ liệu sprint.daily.log

* Cập nhật tự động qua scheduled action (cron job hàng ngày)

## **4.5 Velocity Tracking**

Velocity là số story points hoàn thành trong mỗi Sprint. Module sẽ:

* Tự động tính velocity khi Sprint chuyển sang trạng thái Done

* Lưu lịch sử velocity theo từng Sprint

* Hiển thị bar chart so sánh velocity giữa các Sprint

* Tính Average Velocity cho dự báo planning Sprint tiếp theo

* Xuất báo cáo velocity PDF

# **5\. THIẾT KẾ API & CONTROLLER**

## **5.1 Python Methods chính (Business Logic)**

Các method quan trọng trong model project.sprint:

| Method | Trigger | Mô tả |
| :---- | :---- | :---- |
| **action\_start\_sprint()** | Button click | Chuyển state draft → active, validate dates |
| **action\_end\_sprint()** | Button click | Chuyển active → review, tạo summary |
| **action\_close\_sprint()** | Button click | Review → done, tính velocity, move undone tasks |
| **action\_cancel\_sprint()** | Button click | Hủy sprint, trả task về backlog |
| **\_compute\_burndown()** | Cron daily | Tính toán remaining SP cho burndown |
| **\_compute\_velocity()** | On close | Tính velocity \= completed\_sp / total\_sp |
| **move\_tasks\_to\_backlog()** | On cancel/close | Chuyển undone tasks về backlog |
| **get\_sprint\_statistics()** | RPC call | Trả về stats cho dashboard OWL |

## **5.2 OWL Component Architecture**

Các OWL component chính cần phát triển:

| Component | Dependencies | Chức năng |
| :---- | :---- | :---- |
| **SprintBoard** | useService('orm'), Sortable | Kanban board drag-drop cho Sprint |
| **BurndownChart** | Chart.js, useService('rpc') | Line chart burndown |
| **VelocityChart** | Chart.js, useService('rpc') | Bar chart velocity các Sprint |
| **BacklogPanel** | useService('orm'), Sortable | Backlog sortable list |
| **AgileDashboard** | All above components | Tổng hợp dashboard |
| **SprintSelector** | useService('orm') | Dropdown chọn Sprint hiện tại |

# **6\. ROADMAP CODING (KẾ HOẠCH CODING THEO SPRINT)**

Roadmap chia thành 6 Sprint phát triển, mỗi Sprint kéo dài 2 tuần. Tổng thời gian dự kiến: 12 tuần (3 tháng).

## **Sprint 1: Foundation & Core Models (Tuần 1–2)**

**Mục tiêu:** Xây dựng nền tảng module, các model cơ bản, và security framework.

| \# | Task | File chính | SP | Priority |
| ----- | :---- | :---- | ----- | ----- |
| 1 | Khởi tạo module: \_\_manifest\_\_.py, \_\_init\_\_.py | \_\_manifest\_\_.py | 2 | P0 |
| 2 | Tạo model project.sprint với các field cơ bản | project\_sprint.py | 5 | P0 |
| 3 | Tạo model project.epic | project\_epic.py | 3 | P0 |
| 4 | Mở rộng project.task (\_inherit) thêm Scrum fields | project\_task.py | 5 | P0 |
| 5 | Mở rộng project.project thêm Scrum settings | project\_project.py | 3 | P1 |
| 6 | Tạo security groups (Scrum User/Master/PO) | security.xml | 3 | P0 |
| 7 | Tạo access rights CSV | ir.model.access.csv | 2 | P0 |
| 8 | Tạo record rules | ir\_rule.xml | 3 | P1 |
| 9 | Unit tests cho Sprint model (create, state transitions) | test\_sprint.py | 5 | P1 |
| 10 | Default data: Scrum stages (To Do, In Progress, Done) | project\_stage\_data.xml | 2 | P2 |

**Tổng Story Points: 33**

## **Sprint 2: Views & UI Bản (Tuần 3–4)**

**Mục tiêu:** Tạo các view XML, menu, và giao diện cơ bản cho Sprint, Epic, và Backlog.

| \# | Task | File chính | SP | Priority |
| ----- | :---- | :---- | ----- | ----- |
| 1 | Sprint form view (create/edit Sprint) | project\_sprint\_views.xml | 5 | P0 |
| 2 | Sprint list view và kanban view | project\_sprint\_views.xml | 3 | P0 |
| 3 | Epic form/list/kanban views | project\_epic\_views.xml | 5 | P0 |
| 4 | Task view inheritance (thêm Scrum tab) | project\_task\_views.xml | 5 | P0 |
| 5 | Project view inheritance (Scrum settings page) | project\_project\_views.xml | 3 | P1 |
| 6 | Menu items và navigation | menus.xml | 2 | P0 |
| 7 | Search/Filter views: filter by Sprint, Epic, Task Type | search views | 3 | P1 |
| 8 | Sprint Planning Wizard (bulk move tasks) | sprint\_planning\_wizard.\* | 5 | P1 |
| 9 | Unit tests cho views và wizard | test\_views.py | 3 | P2 |

**Tổng Story Points: 34**

## **Sprint 3: Sprint Board OWL Component (Tuần 5–6)**

**Mục tiêu:** Xây dựng Sprint Board interactive với OWL framework, drag-and-drop, và real-time updates.

| \# | Task | File chính | SP | Priority |
| ----- | :---- | :---- | ----- | ----- |
| 1 | SprintBoard OWL component (layout, columns) | sprint\_board.js | 8 | P0 |
| 2 | SprintBoard QWeb template | sprint\_board.xml | 5 | P0 |
| 3 | Drag-and-drop task giữa columns (Sortable) | sprint\_board.js | 8 | P0 |
| 4 | Sprint selector dropdown component | sprint\_board.js | 3 | P1 |
| 5 | Task card component (story points, assignee, tags) | sprint\_board.js | 5 | P0 |
| 6 | SCSS styling cho Sprint Board | sprint\_board.scss | 3 | P1 |
| 7 | WIP (Work In Progress) limit indicator | sprint\_board.js | 3 | P2 |
| 8 | Register action cho Sprint Board menu | sprint\_dashboard.xml | 2 | P1 |

**Tổng Story Points: 37**

## **Sprint 4: Burndown & Velocity Charts (Tuần 7–8)**

**Mục tiêu:** Xây dựng hệ thống biểu đồ, cơ chế tính toán tự động, và cron job cập nhật hàng ngày.

| \# | Task | File chính | SP | Priority |
| ----- | :---- | :---- | ----- | ----- |
| 1 | Model sprint.daily.log (log remaining SP hàng ngày) | sprint\_velocity.py | 3 | P0 |
| 2 | Cron job tự động log burndown data | data/cron.xml | 5 | P0 |
| 3 | BurndownChart OWL component (Chart.js line chart) | burndown\_chart.js | 8 | P0 |
| 4 | BurndownChart QWeb template | burndown\_chart.xml | 3 | P0 |
| 5 | Velocity computation khi close Sprint | project\_sprint.py | 5 | P0 |
| 6 | VelocityChart OWL component (Chart.js bar chart) | velocity\_chart.js | 8 | P1 |
| 7 | API endpoint get\_burndown\_data(sprint\_id) | project\_sprint.py | 3 | P1 |
| 8 | Unit tests cho burndown và velocity | test\_velocity.py | 5 | P1 |

**Tổng Story Points: 40**

## **Sprint 5: Scrum Ceremonies & Dashboard (Tuần 9–10)**

**Mục tiêu:** Hoàn thiện tính năng quản lý các buổi Scrum và tạo trang Dashboard tổng hợp.

| \# | Task | File chính | SP | Priority |
| ----- | :---- | :---- | ----- | ----- |
| 1 | Model scrum.ceremony (CRUD hoàn chỉnh) | scrum\_ceremony.py | 5 | P0 |
| 2 | Ceremony views (form/list/calendar) | scrum\_ceremony\_views.xml | 5 | P0 |
| 3 | Retrospective template (went\_well, to\_improve) | scrum\_ceremony.py | 3 | P1 |
| 4 | Sprint Report (QWeb PDF template) | sprint\_report\_template.xml | 5 | P1 |
| 5 | AgileDashboard OWL component (tổng hợp) | agile\_dashboard.js | 8 | P0 |
| 6 | Dashboard QWeb template (layout, widgets) | agile\_dashboard.xml | 5 | P0 |
| 7 | Dashboard: current sprint status, team workload | agile\_dashboard.js | 5 | P1 |
| 8 | Dashboard: recent activity feed | agile\_dashboard.js | 3 | P2 |

**Tổng Story Points: 39**

## **Sprint 6: Testing, Polish & Release (Tuần 11–12)**

**Mục tiêu:** Kiểm thử toàn diện, sửa lỗi, tối ưu hiệu suất, viết tài liệu và release.

| \# | Task | File chính | SP | Priority |
| ----- | :---- | :---- | ----- | ----- |
| 1 | Integration tests (full sprint lifecycle) | test\_integration.py | 8 | P0 |
| 2 | Backlog management tests | test\_backlog.py | 5 | P0 |
| 3 | Performance optimization (query N+1, prefetch) | models/\*.py | 5 | P0 |
| 4 | UI/UX polish: responsive, accessibility | \*.scss, \*.xml | 5 | P1 |
| 5 | Tài liệu kỹ thuật (README, CHANGELOG) | README.md | 3 | P1 |
| 6 | Hướng dẫn sử dụng (User Guide) | doc/user\_guide.md | 3 | P1 |
| 7 | Migration script (nếu upgrade từ bản cũ) | migrations/ | 3 | P2 |
| 8 | Final QA, bug fixes, release preparation | All files | 5 | P0 |

**Tổng Story Points: 37**

# **7\. TỔNG HỢP ROADMAP TIMELINE**

| Sprint | Nội dung chính | Thời gian | SP | Milestone |
| ----- | :---- | :---- | ----- | :---- |
| **1** | Foundation & Core Models | Tuần 1–2 | 33 | **Module có thể install** |
| **2** | Views & UI cơ bản | Tuần 3–4 | 34 | **CRUD Sprint/Epic/Task** |
| **3** | Sprint Board OWL | Tuần 5–6 | 37 | **Sprint Board hoạt động** |
| **4** | Burndown & Velocity | Tuần 7–8 | 40 | **Charts hoàn chỉnh** |
| **5** | Ceremonies & Dashboard | Tuần 9–10 | 39 | **Dashboard live** |
| **6** | Testing & Release | Tuần 11–12 | 37 | **Release v1.0.0** |

**Tổng Story Points: 220 | Tổng thời gian: 12 tuần (3 tháng) | Average Velocity: \~37 SP/Sprint**

# **8\. MẪU CODE THAM KHẢO**

## **8.1 \_\_manifest\_\_.py**

{  
    'name': 'Project Scrum Management',  
    'version': '18.0.1.0.0',  
    'category': 'Project',  
    'summary': 'Agile/Scrum Project Management for Odoo 18',  
    'description': '''  
        Scrum module for Odoo 18 Community Edition.  
        Features: Sprint, Backlog, Story Points,  
        Burndown Chart, Velocity Tracking, Scrum Ceremonies.  
    ''',  
    'author': 'David',  
    'depends': \['project', 'web'\],  
    'data': \[  
        'security/security.xml',  
        'security/ir.model.access.csv',  
        'security/ir\_rule.xml',  
        'data/project\_stage\_data.xml',  
        'views/project\_sprint\_views.xml',  
        'views/project\_epic\_views.xml',  
        'views/project\_task\_views.xml',  
        'views/project\_project\_views.xml',  
        'views/scrum\_ceremony\_views.xml',  
        'views/sprint\_dashboard.xml',  
        'views/menus.xml',  
        'wizard/sprint\_planning\_wizard.xml',  
        'report/sprint\_report\_template.xml',  
    \],  
    'assets': {  
        'web.assets\_backend': \[  
            'project\_scrum/static/src/js/\*.js',  
            'project\_scrum/static/src/xml/\*.xml',  
            'project\_scrum/static/src/scss/\*.scss',  
        \],  
    },  
    'installable': True,  
    'application': True,  
    'license': 'LGPL-3',  
}

## **8.2 project\_sprint.py (Model chính)**

from odoo import models, fields, api, \_  
from odoo.exceptions import ValidationError  
from datetime import timedelta  
import json

class ProjectSprint(models.Model):  
    \_name \= 'project.sprint'  
    \_description \= 'Project Sprint'  
    \_order \= 'date\_start desc'

    name \= fields.Char('Sprint Name', required=True)  
    project\_id \= fields.Many2one(  
        'project.project', 'Project',  
        required=True, ondelete='cascade')  
    state \= fields.Selection(\[  
        ('draft', 'Draft'),  
        ('active', 'Active'),  
        ('review', 'In Review'),  
        ('done', 'Done'),  
        ('cancelled', 'Cancelled'),  
    \], default='draft', tracking=True)  
    date\_start \= fields.Date('Start Date', required=True)  
    date\_end \= fields.Date('End Date', required=True)  
    goal \= fields.Text('Sprint Goal')  
    scrum\_master\_id \= fields.Many2one(  
        'res.users', 'Scrum Master')  
    task\_ids \= fields.One2many(  
        'project.task', 'sprint\_id', 'Tasks')

    total\_story\_points \= fields.Integer(  
        compute='\_compute\_story\_points', store=True)  
    completed\_story\_points \= fields.Integer(  
        compute='\_compute\_story\_points', store=True)  
    velocity \= fields.Float(  
        compute='\_compute\_velocity')

    @api.depends('task\_ids.story\_points',  
                 'task\_ids.stage\_id.is\_closed')  
    def \_compute\_story\_points(self):  
        for sprint in self:  
            sprint.total\_story\_points \= sum(  
                sprint.task\_ids.mapped('story\_points'))  
            sprint.completed\_story\_points \= sum(  
                sprint.task\_ids.filtered(  
                    lambda t: t.stage\_id.is\_closed  
                ).mapped('story\_points'))

    @api.depends('total\_story\_points',  
                 'completed\_story\_points')  
    def \_compute\_velocity(self):  
        for sprint in self:  
            if sprint.total\_story\_points:  
                sprint.velocity \= (  
                    sprint.completed\_story\_points /  
                    sprint.total\_story\_points \* 100\)  
            else:  
                sprint.velocity \= 0.0

    def action\_start\_sprint(self):  
        self.ensure\_one()  
        if not self.task\_ids:  
            raise ValidationError(  
                \_('Cannot start empty Sprint.'))  
        active \= self.search(\[  
            ('project\_id', '=', self.project\_id.id),  
            ('state', '=', 'active')\])  
        if active:  
            raise ValidationError(  
                \_('Project already has an active Sprint.'))  
        self.state \= 'active'

    def action\_end\_sprint(self):  
        self.ensure\_one()  
        self.state \= 'review'

    def action\_close\_sprint(self):  
        self.ensure\_one()  
        undone \= self.task\_ids.filtered(  
            lambda t: not t.stage\_id.is\_closed)  
        undone.write({'sprint\_id': False})  
        self.state \= 'done'

## **8.3 project\_task.py (Inherit)**

from odoo import models, fields

class ProjectTask(models.Model):  
    \_inherit \= 'project.task'

    sprint\_id \= fields.Many2one(  
        'project.sprint', 'Sprint',  
        index=True, tracking=True)  
    epic\_id \= fields.Many2one(  
        'project.epic', 'Epic',  
        index=True, tracking=True)  
    story\_points \= fields.Integer(  
        'Story Points', default=0)  
    task\_type \= fields.Selection(\[  
        ('story', 'User Story'),  
        ('task', 'Task'),  
        ('bug', 'Bug'),  
        ('improvement', 'Improvement'),  
    \], default='task', string='Type')  
    acceptance\_criteria \= fields.Text(  
        'Acceptance Criteria')  
    is\_blocked \= fields.Boolean('Blocked')  
    blocked\_reason \= fields.Text('Block Reason')

# **9\. RỦI RO & BIỆN PHÁP GIẢM THIỂU**

| Rủi ro | Mức độ | Tác động | Biện pháp |
| :---- | ----- | :---- | :---- |
| **OWL framework thay đổi API** | Cao | Component phải viết lại | Theo dõi changelog Odoo 18, viết abstraction layer |
| **Hiệu suất với dữ liệu lớn** | Trung bình | Sprint Board load chậm | Sử dụng prefetch, limit records, lazy load |
| **Xung đột với module khác** | Trung bình | Field/view bị ghi đè | Sử dụng prefix project\_scrum\_ cho XML IDs |
| **Team chưa quen Scrum** | Thấp | Sử dụng không hiệu quả | Viết user guide, training session |
| **Upgrade Odoo trong tương lai** | Thấp | Module không tương thích | Viết migration scripts sẵn |

# **10\. DEFINITION OF DONE (Tiêu chí hoàn thành)**

Mỗi task/user story được coi là "Done" khi đáp ứng tất cả các tiêu chí sau:

* Code đã được review bởi ít nhất 1 thành viên khác trong team

* Unit tests đạt 100% (không có test fail)

* Code tuân thủ Odoo Coding Guidelines (PEP8, XML schema)

* Không có lỗi lint (flake8, pylint-odoo)

* Module có thể install/uninstall sạch trên database mới

* Tài liệu kỹ thuật đã cập nhật (docstrings, README)

* Security access rights đã được kiểm tra

* Không có SQL injection hoặc XSS vulnerability

* Performance: không có N+1 query vấn đề

* UI hoạt động đúng trên Chrome, Firefox, Edge

# **11\. CÁC BƯỚC TIẾP THEO**

## **11.1 Giai đoạn tiếp theo (v2.0)**

* Tích hợp Kanban Metrics (Cumulative Flow Diagram, Lead Time, Cycle Time)

* Advanced Reporting (xuất báo cáo Excel với pivot tables)

* Calendar integration với Scrum ceremonies

* Email notifications cho Sprint events

* Mobile-optimized Sprint Board

* AI-assisted story point estimation (dựa trên lịch sử)

## **11.2 Hành động ngay**

* **Bước 1:** Review và phê duyệt tài liệu này với các stakeholders

* **Bước 2:** Setup môi trường phát triển Odoo 18 Community với PostgreSQL

* **Bước 3:** Tạo repository Git, branch strategy (main / develop / feature/\*)

* **Bước 4:** Bắt đầu Sprint 1 – Foundation & Core Models
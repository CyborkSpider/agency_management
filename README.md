# Agency Management (Odoo 19)

[🇬🇧 English](#english) | [🇸🇦 العربية](#arabic)

---

<a name="english"></a>
## 🇬🇧 English

**Agency & Freelance ERP with Auto Team Assignment**

A comprehensive Odoo 19 module designed to manage agency teams, projects, timesheets, financials, ratings, and deadline monitoring. It features an intelligent **Automatic Team Assignment Engine** that evaluates teams based on skills, availability, capacity, performance, and cost efficiency.

### 🌟 Key Features

* **Intelligent Auto-Assignment Engine:** Automatically assigns the most suitable team to a project based on a scoring algorithm evaluating:
  * Skill Match (25%)
  * Availability (25%)
  * Capacity (20%)
  * Performance Rating (15%)
  * On-Time Delivery Rate (10%)
  * Cost Efficiency (5%)
* **Comprehensive Project Management:** Track project status, deadlines, priorities, and required skills. 
* **Financial Tracking:** Monitor client budgets (revenue), actual costs (based on team internal rates), gross profit, and profit margins in real-time.
* **Team & Resource Management:** Manage teams by track/specialization, track their current load, capacity, and overall availability.
* **Deadline Monitoring:** Automated computation of deadline statuses (e.g., Upcoming, Due Soon, Overdue) and Risk Levels (On Track, At Risk, Critical).
* **Performance Ratings:** Post-project evaluation and rating system to maintain a high quality of service.
* **Admin Dashboard:** Aggregated metrics and insights into agency performance and financials.

### 📦 Dependencies

This module relies on the following standard Odoo apps:
* `project`
* `hr`
* `hr_skills`
* `hr_timesheet`
* `sale`
* `account`
* `mail`

### 🏗️ Models & Architecture

* `agency.project`: Core model handling project requirements, dates, financials, and the auto-assignment logic.
* `agency.team`: Defines agency teams, their tracks, rates (billing/internal), and performance metrics.
* `agency.team.member`: Associates HR employees with agency teams.
* `agency.track`: Categorizes teams and projects by specialization (e.g., Web Development, Design).
* `agency.project.rating`: Handles client or internal feedback for completed projects.
* `agency.assignment.history`: Audit log for team assignments and re-assignments.
* `agency.dashboard`: Provides centralized analytical metrics.

### 👨‍💻 Authors & Credits

* **Lead Developer & Architect:** Ziad Elgohary ([Portfolio](https://cyborkspider.github.io/en/))
* **Contributing Developer:** Omar Bahnasy

### 📜 License

This software is released under the **MIT** License.
*© 2026 Ziad Elgohary & Omar Bahnasy. All rights reserved.* 
*(Note: Refer to `__manifest__.py` for specific proprietary terms and conditions.)*

---

<a name="arabic"></a>
## 🇸🇦 العربية

**إدارة الوكالات والعمل الحر مع تعيين تلقائي للفرق**

نظام Odoo 19 متكامل مصمم لإدارة فرق الوكالات، والمشاريع، والجداول الزمنية، والماليات، والتقييمات، ومراقبة المواعيد النهائية. يتميز بـ **محرك تعيين تلقائي للفرق** ذكي يقوم بتقييم الفرق بناءً على المهارات، التوافر، السعة، الأداء، وكفاءة التكلفة.

### 🌟 الميزات الرئيسية

* **محرك التعيين التلقائي الذكي:** يقوم تلقائيًا بتعيين الفريق الأنسب للمشروع بناءً على خوارزمية تسجل وتقيم:
  * توافق المهارات (25%)
  * التوافر (25%)
  * السعة (20%)
  * تقييم الأداء (15%)
  * معدل التسليم في الوقت (10%)
  * كفاءة التكلفة (5%)
* **إدارة شاملة للمشاريع:** تتبع حالة المشروع، والمواعيد النهائية، والأولويات، والمهارات المطلوبة.
* **تتبع الماليات:** مراقبة ميزانيات العملاء (الإيرادات)، والتكاليف الفعلية (بناءً على الأسعار الداخلية للفريق)، وإجمالي الربح، وهوامش الربح في الوقت الفعلي.
* **إدارة الفرق والموارد:** إدارة الفرق حسب المسار/التخصص، وتتبع عبء العمل الحالي، والسعة، والتوافر الإجمالي.
* **مراقبة المواعيد النهائية:** حساب آلي لحالات المواعيد النهائية (مثل: قادم، مستحق قريباً، متأخر) ومستويات المخاطر (على المسار، في خطر، حرج).
* **تقييمات الأداء:** نظام تقييم ما بعد المشروع للحفاظ على جودة خدمة عالية.
* **لوحة تحكم الإدارة (Dashboard):** مقاييس ورؤى مجمعة حول أداء الوكالة والماليات.

### 📦 التبعيات (Dependencies)

يعتمد هذا النظام على تطبيقات Odoo القياسية التالية:
* `project`
* `hr`
* `hr_skills`
* `hr_timesheet`
* `sale`
* `account`
* `mail`

### 🏗️ النماذج والهيكلية (Models & Architecture)

* `agency.project`: النموذج الأساسي الذي يعالج متطلبات المشروع، والتواريخ، والماليات، ومنطق التعيين التلقائي.
* `agency.team`: يحدد فرق الوكالة، ومساراتهم، وأسعارهم (الفوترة/الأسعار الداخلية)، ومقاييس الأداء.
* `agency.team.member`: يربط موظفي الموارد البشرية بفرق الوكالة.
* `agency.track`: يصنف الفرق والمشاريع حسب التخصص (مثل: تطوير الويب، التصميم).
* `agency.project.rating`: يعالج ملاحظات العميل أو التقييم الداخلي للمشاريع المكتملة.
* `agency.assignment.history`: سجل تدقيق لتعيينات الفرق وإعادة التعيين.
* `agency.dashboard`: يوفر مقاييس تحليلية مركزية.

### 👨‍💻 المؤلفون والاعتمادات

* **المطور الرئيسي والمهندس المعماري:** زياد الجوهري ([معرض الأعمال](https://cyborkspider.github.io/en/))
* **المطور المشارك:** عمر بهنسي

### 📜 الترخيص

تم إصدار هذا البرنامج بموجب ترخيص **Ziad Elgohary**.
*© 2026 زياد الجوهري وعمر بهنسي. جميع الحقوق محفوظة.* 
*(ملاحظة: راجع `__manifest__.py` للاطلاع على الشروط والأحكام الخاصة.)*

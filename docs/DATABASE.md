# Lumina V3 — Database Documentation

## Entity Relationship Overview

### Core Entities
- **School** — Multi-tenant root entity. All data is scoped to a school.
- **User** — Base user with telegram_id, role, and school association.
- **Admin/Teacher/Student/Parent** — Role-specific profiles linked 1:1 to User.
- **StudentParent** — M:N link between Student and Parent.

### Academic Entities
- **Class** — School class (e.g., "9A"). Has grade_level, section, homeroom teacher.
- **Subject** — School subject with code, color, icon.
- **TeacherAssignment** — Links Teacher↔Subject↔Class for an academic year.
- **AcademicYear** — Named period (e.g., "2025-2026") with start/end dates.
- **Term** — Sub-period within academic year (quarters, semesters).
- **Schedule** — Recurring lesson slot (day, time, subject, teacher, class).
- **Lesson** — Concrete lesson instance on a specific date.

### Grading Entities
- **GradingSystem** — Scale definition (5-pt, 12-pt, 100-pt, A-F, custom).
- **GradeType** — Category of grade (homework, exam, etc.) with weight.
- **Grade** — Individual grade record. NEVER physically deleted (soft-delete only).
  - Supports Second Chance (correction grades linked to originals).
  - Full audit trail via AuditLog.
- **Attendance** — Per-student, per-lesson status (present/absent/late/excused).

### Homework Entities
- **Homework** — Assignment with title, class, subject, due date, attachments.
- **HomeworkSubmission** — Student's submission with content and status tracking.

### Gamification Entities
- **Achievement** — Defined achievement with trigger conditions and XP reward.
- **UserAchievement** — M:N: student earned achievement.
- **Title** — Display title unlockable by level/achievement.
- **XPTransaction** — Immutable XP ledger (never edit, only append).
- **Skill** — Node in skill tree with prerequisites and subject link.
- **StudentSkill** — Student's progress on a skill.

### Communication Entities
- **Notification** — In-app/bot notification with type and read status.
- **NotificationPreference** — Per-user, per-type preference settings.
- **TeacherNote** — Private teacher notes on students (strict auth).
- **StudentVibe** — Student mood tracking (private by default).
- **SchoolAnnouncement** — School-wide announcements with role targeting.

### System Entities
- **Invite** — Cryptographic invitation token with expiration and usage limits.
- **AuditLog** — Immutable audit record of sensitive operations.
- **FlashcardSet/Flashcard** — Student study flashcards with review tracking.
- **FileAsset** — Secure file storage for Digital Backpack.
- **FeatureFlag** — Per-school feature toggles.
- **DashboardLayout** — Student's customizable dashboard widget layout.
- **Consent** — Parent consent records (data processing, photos, AI, etc.).

## Key Design Decisions

### UUID Primary Keys
All tables use UUID v4 primary keys for security (non-enumerable) and distributed system compatibility.

### Multi-Tenant Isolation
Every tenant-scoped table includes an indexed `school_id` column. All queries MUST filter by this column using the authenticated user's school_id.

### Soft Delete
Critical records (grades, users) use `SoftDeleteMixin` with `is_deleted`, `deleted_at`, `deleted_by` columns. Physical deletion is prohibited for data integrity.

### Timestamps
All tables include `created_at` and `updated_at` with server-side defaults via `TimestampMixin`.

### XP Ledger
XP transactions are append-only (immutable). The student's `xp` field is the running total, maintained transactionally with each XPTransaction insert.

## Migrations
Managed via Alembic with async PostgreSQL support. Migration files in `backend/migrations/versions/`.

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

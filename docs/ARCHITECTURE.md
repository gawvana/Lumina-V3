# Lumina V3 — Architecture

## Overview

Lumina V3 is a three-tier application:
1. **Frontend**: React 18 + TypeScript + Vite (Telegram Mini App)
2. **Backend**: FastAPI + SQLAlchemy 2.x (async) + PostgreSQL
3. **Bot**: aiogram 3.x (Telegram Bot API)

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Telegram Platform                     │
│  ┌──────────────┐                 ┌──────────────────┐  │
│  │   Bot API    │                 │   Web App API    │  │
│  └──────┬───────┘                 └────────┬─────────┘  │
└─────────┼──────────────────────────────────┼────────────┘
          │                                  │
          ▼                                  ▼
┌──────────────────┐              ┌──────────────────────┐
│  aiogram 3.x     │              │  React Mini App      │
│  - Routers       │              │  - Components        │
│  - Middleware     │─────────────►│  - Zustand stores    │
│  - Keyboards     │              │  - react-query       │
│  - FSM           │              │  - i18n (RU/UZ)      │
└────────┬─────────┘              └──────────┬───────────┘
         │                                   │
         └──────────────┬────────────────────┘
                        ▼
              ┌──────────────────┐
              │    FastAPI       │
              │  ┌────────────┐ │
              │  │ Auth/RBAC  │ │
              │  ├────────────┤ │
              │  │ API Routes │ │
              │  ├────────────┤ │
              │  │ Services   │ │
              │  ├────────────┤ │
              │  │ Models     │ │
              │  └────────────┘ │
              └───┬──────┬──────┘
                  │      │
         ┌────────┘      └────────┐
         ▼                        ▼
┌──────────────┐          ┌──────────────┐
│ PostgreSQL   │          │    Redis     │
│ - 35+ tables │          │ - Sessions   │
│ - Migrations │          │ - Cache      │
│ - Audit logs │          │ - Job queues │
└──────────────┘          └──────────────┘
```

## Backend Architecture

### Layer Separation
```
app/
├── api/        → HTTP layer (FastAPI routers, request/response handling)
├── core/       → Cross-cutting concerns (config, security, middleware, errors)
├── models/     → Data layer (SQLAlchemy ORM models)
├── schemas/    → Validation layer (Pydantic v2 schemas)
├── services/   → Business logic layer
└── workers/    → Background job definitions
```

### Key Patterns

#### Multi-Tenant Isolation
Every tenant-scoped query filters by `school_id`:
```python
class TenantMixin:
    school_id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=False, index=True)
```

#### Soft Delete
Grades and critical records are never physically deleted:
```python
class SoftDeleteMixin:
    is_deleted: Mapped[bool] = mapped_column(default=False)
    deleted_at: Mapped[datetime | None]
    deleted_by: Mapped[str | None]
```

#### RBAC
Centralized role checking via FastAPI dependencies:
```python
admin_dep = require_role(UserRole.ADMIN)
teacher_dep = require_role(UserRole.TEACHER, UserRole.ADMIN)
```

#### Audit Trail
All sensitive operations logged:
```python
AuditLog(action=AuditAction.GRADE_UPDATE, old_value={...}, new_value={...})
```

## Frontend Architecture

### Tech Stack
- React 18 with TypeScript strict mode
- Vite for build and development
- Zustand for state management
- @tanstack/react-query for server state
- Tailwind CSS for styling
- framer-motion for animations
- i18next for RU/UZ localization

### Component Architecture
```
src/
├── components/
│   ├── ui/         → Design system primitives (Button, Card, Modal, etc.)
│   └── Layout.tsx  → Role-aware shell with navigation
├── pages/
│   ├── admin/      → Admin-specific pages
│   ├── teacher/    → Teacher-specific pages
│   ├── student/    → Student-specific pages
│   └── parent/     → Parent-specific pages
├── stores/         → Zustand stores (auth, theme)
├── hooks/          → Custom hooks (useTelegram, useApi)
├── api/            → Typed API client
├── i18n/           → Localization setup and catalogs
└── theme/          → Design tokens and Telegram theme
```

## Database Architecture

See [DATABASE.md](DATABASE.md) for complete schema.

### Entity Groups
1. **Core**: School, User, Admin, Teacher, Student, Parent, StudentParent
2. **Academic**: Class, Subject, TeacherAssignment, AcademicYear, Term, Schedule, Lesson
3. **Grading**: Grade, GradeType, GradingSystem, Attendance
4. **Homework**: Homework, HomeworkSubmission
5. **Gamification**: Achievement, UserAchievement, Title, XPTransaction, Skill, StudentSkill
6. **Communication**: Notification, NotificationPreference, TeacherNote, StudentVibe, SchoolAnnouncement
7. **System**: Invite, AuditLog, FlashcardSet, Flashcard, FileAsset, FeatureFlag, DashboardLayout, Consent

## Security Architecture

See [SECURITY.md](SECURITY.md) for full details.

### Authentication Flow
1. Telegram Web App sends `initData` to backend
2. Backend verifies HMAC signature with bot token
3. Backend checks `auth_date` for replay protection
4. Backend looks up user, issues JWT
5. JWT contains: user_id, school_id, role, telegram_id

### Authorization
- Server-side RBAC on every endpoint
- Multi-tenant filtering on every query
- No client-side trust for role/school_id/student_id

# Lumina V3 — Product Requirements

## Vision
Lumina is a school management platform delivered via Telegram, combining an electronic journal, diary, schedule, analytics, and gamification into a single cohesive experience.

## Target Users

### Admin
School administrators who manage the institution's configuration.
- Create and manage schools, classes, subjects, teachers, students
- Configure grading systems (5-pt, 12-pt, 100-pt, A-F, custom)
- Manage academic years and terms
- Issue and manage invitation links
- View audit logs and analytics
- Manage feature flags and school settings
- Create announcements

### Teacher  
Educators who interact with students daily.
- Mark attendance (bulk and individual, per lesson)
- Create and manage grades with full audit trail
- Quick grading, swipe grading, voice grading modes
- Assign and track homework
- Manage interactive seating charts
- Random student selection (fair, configurable)
- Private notes on students
- Class analytics

### Student
Learners who track their academic journey.
- View grades, GPA, schedule, homework
- XP system with levels and streaks
- Achievement system with hidden and rare achievements
- Skill tree with prerequisites and mastery
- Flashcard study system
- Vibe (mood) tracking
- Profile customization (skins, frames, aura, title)
- Digital Backpack (file storage)
- Customizable dashboard layout
- Second Chance (grade correction window)

### Parent
Guardians who monitor their children's progress.
- Link to one or more children
- View grades, attendance, homework for each child
- Submit absence requests
- Manage notification preferences
- Receive weekly smart summaries (real data only)
- View school announcements
- Manage consent settings
- Download PDF portfolio

## Non-Functional Requirements
- **Security**: Server-side Telegram initData verification, RBAC, multi-tenant isolation
- **Localization**: Russian and Uzbek from launch, no hardcoded strings
- **Performance**: Paginated collections, N+1 query prevention, background workers
- **Observability**: Structured logging, request IDs, health/ready endpoints
- **Accessibility**: WCAG 2.1 AA compliance where applicable

## Grading Systems
Multiple systems supported per school:
- 5-point (1-5)
- 12-point (1-12)
- 100-point (0-100)
- Letter (A-F)
- Custom (configurable by school)

GPA calculation uses weighted averages across grade types.

## Attendance
Statuses: Present, Absent, Late (with minutes), Excused.
Bulk marking per class, individual corrections with audit trail.

## Homework Lifecycle
Create → Edit → Archive (teacher side)
Pending → Submitted → Late → Graded → Returned (student side)
Automatic overdue tracking, reminders, file attachments.

## Gamification
- **XP**: Earned from grades, attendance, homework, streaks. Immutable ledger.
- **Levels**: Deterministic calculation from XP total. Level N requires N×100 XP.
- **Streaks**: Timezone-aware daily activity tracking.
- **Achievements**: Automatic trigger engine with configurable conditions.
- **Titles**: Unlockable display titles tied to levels and achievements.
- **Skill Tree**: Subject-linked skills with prerequisites and mastery levels.

## Notifications
Types: grade, homework, attendance, achievement, announcement, summary.
Per-user configurable preferences. Delivered via bot and in-app.

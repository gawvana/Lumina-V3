# Lumina V3 — Testing Documentation

## Test Architecture

### Test Types
| Type | Directory | Purpose | Tool |
|------|-----------|---------|------|
| Unit | `tests/test_*.py` | Individual functions/methods | pytest |
| Integration | `tests/test_*.py` | API endpoints with DB | pytest + httpx |
| Security | `tests/test_security.py` | RBAC and tenant isolation | pytest |
| E2E | `tests/e2e/` | Full user flows | Playwright |
| Frontend | `frontend/src/**/*.test.tsx` | Components and pages | Vitest |
| Load | `tests/load/` | Performance under stress | Locust |

### Running Tests

```bash
# All backend tests
cd backend && python -m pytest -v

# With coverage
python -m pytest -v --cov=app --cov-report=term-missing --cov-report=html

# Security tests only
python -m pytest tests/test_security.py -v

# Frontend tests
cd frontend && npm run test

# Type checking
cd backend && mypy app/
cd frontend && npm run typecheck

# Lint
cd backend && ruff check .
cd frontend && npm run lint
```

## Test Fixtures (conftest.py)

### Available Fixtures
- `db_session` — Async database session (isolated per test)
- `client` — httpx AsyncClient configured with test app
- `test_school` — Pre-created School record
- `admin_user` / `admin_token` — Admin user with JWT token
- `teacher_user` / `teacher_token` — Teacher user with JWT token
- `student_user` / `student_token` — Student user with JWT token
- `parent_user` / `parent_token` — Parent user with JWT token

## Security Test Matrix (§13.4)

| Test | Source | Target | Expected |
|------|--------|--------|----------|
| `test_student_a_cannot_access_student_b_grades` | Student A | Student B grades | 403 |
| `test_student_cannot_access_teacher_endpoints` | Student | Teacher API | 403 |
| `test_student_cannot_access_admin_endpoints` | Student | Admin API | 403 |
| `test_teacher_cannot_access_admin_endpoints` | Teacher | Admin API | 403 |
| `test_teacher_cannot_access_other_class` | Teacher | Unassigned class | 403 |
| `test_parent_cannot_access_other_child` | Parent | Unlinked child | 403 |
| `test_school_a_cannot_access_school_b` | School A user | School B data | 403 |
| `test_unauthenticated_access_denied` | No token | Protected API | 401 |
| `test_invalid_token_denied` | Bad token | Protected API | 401 |
| `test_role_escalation_prevented` | Student | Admin role | 403 |

## E2E Scenarios

### Admin Flow
1. Login → Dashboard
2. Create school → Create class → Create subject
3. Create teacher via invite → Assign to class+subject
4. Create student via invite → Assign to class
5. Configure schedule → Set up grading system
6. View audit log → Verify all actions logged

### Teacher Flow
1. Login → Today view
2. Select class → View students
3. Interactive seating → Drag-drop arrangement
4. Mark attendance (bulk)
5. Create grade → Verify audit trail → Undo grade
6. Create homework → Set due date
7. Create private note

### Student Flow
1. Login → Dashboard → Check today's schedule
2. View grades → Check GPA
3. Submit homework → Get XP
4. Check achievements → Equip title
5. Create flashcard set → Review cards
6. Log vibe

### Parent Flow
1. Login → Link child (invite)
2. View child grades → Check GPA
3. View attendance → Submit absence request
4. View homework status
5. Check weekly summary
6. Manage notification preferences

## Load Tests

### Scenarios
- 100 concurrent students viewing dashboard
- Teacher grading entire class (30 students, rapid)
- Notification burst (200 notifications simultaneously)
- 50 concurrent API requests per school

### Running Load Tests
```bash
cd backend
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

## CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    steps:
      - Format check (ruff format --check)
      - Lint (ruff check)
      - Type check (mypy)
      - Backend tests (pytest)
      - Security tests (pytest tests/test_security.py)
      - Frontend lint (npm run lint)
      - Frontend typecheck (npm run typecheck)
      - Frontend tests (npm run test)
      - Frontend build (npm run build)
      - Migration check (alembic check)
```

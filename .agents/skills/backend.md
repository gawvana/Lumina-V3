# Lumina Backend Skill

## Core Principles
- Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.0 async with asyncpg.
- Multi-Tenancy: Universal `TenantMixin` with `school_id` foreign key (`schools.id`) and indexed filtering in every query.
- Security: Telegram initData HMAC-SHA256 signature verification + 24-hour replay protection.
- Roles: `ADMIN`, `TEACHER`, `STUDENT`, `PARENT`.
- Error handling: Uniform format (§13.7):
  ```json
  {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {},
    "request_id": "uuid"
  }
  ```
- Soft-delete for grades and sensitive records (`is_deleted`, `deleted_at`, `deleted_by`).
- Immutable audit log for all critical changes.

# Lumina Security & RBAC Skill

## Security Requirements
- Server-side verification of Telegram `initData` via HMAC-SHA256 (`WebAppData` key).
- Reject expired `auth_date` (> 86400 seconds).
- JWT issuance (HS256) with role and tenant claims.
- Never trust client-provided `school_id`, `role`, or `user_id`.
- Tenant isolation: Query filters must always scope by `school_id = current_user.school_id`.
- Security Matrix (§13.4):
  - Student A -> Student B: 403 / filtered
  - Student -> Teacher: 403
  - Student -> Admin: 403
  - Teacher -> Admin: 403
  - Teacher -> Foreign Class: 404 / 403
  - Parent -> Foreign Child: 403
  - School A -> School B: 404 / 403
  - Unauthenticated: 401
  - Invalid Token: 401
  - Role Escalation: 403

# Lumina V3 — Security

## Authentication

### Telegram initData Verification
Server-side HMAC-SHA256 verification of Telegram Web App initData:

1. Parse query string from `Telegram.WebApp.initData`
2. Extract and remove `hash` parameter
3. Sort remaining parameters alphabetically
4. Build data-check-string: `key=value\n` pairs
5. Compute secret: `HMAC-SHA256("WebAppData", bot_token)`
6. Compute hash: `HMAC-SHA256(secret, data_check_string)`
7. Compare with provided hash (constant-time comparison)
8. Check `auth_date` within 5-minute window (replay protection)

### JWT Tokens
- Algorithm: HS256
- Expiry: 24 hours (configurable)
- Payload: user_id, school_id, role, telegram_id, jti (unique ID)
- Secret: app_secret_key from environment

### Session Security
- Tokens are not stored in localStorage (vulnerable to XSS)
- Backend validates user exists and is active on protected routes
- Token refresh not implemented (re-authentication via initData)

## Authorization (RBAC)

### Role Hierarchy
```
ADMIN → Full access within their school
TEACHER → Class/subject access based on assignments
STUDENT → Own data only
PARENT → Linked children's data only
```

### Enforcement Points
1. **API middleware**: `require_role()` dependency on every protected endpoint
2. **Query filtering**: `school_id` filter on every tenant-scoped query
3. **Relationship verification**: Parent↔Student link checked before access
4. **Teacher assignment check**: Teacher verified against class assignment before access

### Critical Rules
- Role/school_id/student_id NEVER taken from frontend as source of truth
- Every mutation endpoint verifies authorization server-side
- Teacher private notes visible only to authoring teacher
- Student vibes private by default

## Multi-Tenant Isolation

### Design
- Every tenant-scoped table has `school_id` column (indexed)
- All queries filter by `school_id` from authenticated session
- No cross-school data access under any circumstance

### Testing
Dedicated test suite verifies:
- School A user cannot access School B data
- Applies to all entity types: classes, grades, students, etc.

## Security Test Matrix

| Test Case | Expected | Critical |
|---|---|---|
| Student A → Student B grades | 403 | YES |
| Student → Teacher endpoints | 403 | YES |
| Student → Admin endpoints | 403 | YES |
| Teacher → Admin endpoints | 403 | YES |
| Teacher → Other class data | 403 | YES |
| Parent → Unlinked child | 403 | YES |
| School A → School B data | 403 | YES |
| Unauthenticated access | 401 | YES |
| Invalid token | 401 | YES |
| Role escalation attempt | 403 | YES |

## Infrastructure Security

### Secrets Management
- All secrets via environment variables
- `.env` file excluded from version control
- `.env.example` contains only placeholder values
- No tokens/keys/passwords in source code

### Network Security
- CORS restricted to known origins
- Security headers on all responses:
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  - Referrer-Policy: strict-origin-when-cross-origin
  - Content-Security-Policy: default-src 'self'
  - Permissions-Policy: camera=(), microphone=(), geolocation=()

### Rate Limiting
- Per-user rate limiting on API endpoints
- Bot throttle middleware to prevent abuse
- Configurable limits per endpoint type

### File Security
- File type validation on upload
- File size limits enforced
- Files stored outside web root
- Served through authenticated API endpoint
- Unique filenames (UUID) to prevent path traversal

### Webhook Security
- Telegram webhook verified via secret token
- Webhook URL only accepts POST from Telegram IPs
- Idempotent update processing

## Incident Response
- Structured logging with request IDs for audit trail
- AuditLog table for all sensitive operations
- Health and readiness endpoints for monitoring
- Documented disaster recovery procedure

# Lumina V3 — Operations Guide

## Service Architecture

### Processes
| Service | Port | Description |
|---------|------|-------------|
| Backend API | 8000 | FastAPI application |
| Bot | - | aiogram Telegram bot (webhook or polling) |
| Frontend | 5173 (dev) | Vite dev server / static files in production |
| PostgreSQL | 5432 | Primary database |
| Redis | 6379 | Cache, sessions, job queues |

## Monitoring

### Health Checks
- `GET /health` — Liveness probe (always 200 if process alive)
- `GET /ready` — Readiness probe (checks DB connectivity)

### Structured Logging
All services use structlog for structured JSON logging:
```json
{
  "event": "http_request",
  "method": "POST",
  "path": "/api/v1/teacher/grades",
  "status": 201,
  "duration_ms": 45.2,
  "request_id": "abc-123-def",
  "timestamp": "2025-09-13T10:00:00Z",
  "level": "info"
}
```

### Request Tracing
Every request gets a unique `X-Request-ID` header (generated or forwarded).
This ID appears in:
- Response headers
- Log entries
- Error responses
- Audit log entries

## Maintenance

### Database Maintenance
```bash
# Vacuum analyze (weekly)
docker exec lumina-postgres psql -U lumina -c "VACUUM ANALYZE;"

# Check table sizes
docker exec lumina-postgres psql -U lumina -c "
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 20;"
```

### Log Rotation
Configure log rotation in production. Docker handles this with `--log-opt max-size=10m --log-opt max-file=3`.

### Redis Maintenance
```bash
# Check memory usage
redis-cli INFO memory

# Clear cache (non-destructive to sessions)
redis-cli FLUSHDB
```

## Troubleshooting

### Common Issues

| Symptom | Likely Cause | Solution |
|---------|-------------|----------|
| 401 on all API calls | Expired/invalid JWT | Re-authenticate via initData |
| 500 on startup | DB not reachable | Check DATABASE_URL, pg_isready |
| Bot not responding | Webhook misconfigured | Check TELEGRAM_WEBHOOK_URL |
| Mini App blank | Frontend build failed | Run `npm run build`, check logs |
| Slow queries | Missing indexes or N+1 | Check query logs, add indexes |

### Emergency Procedures
1. **Service Down**: Check Docker containers, restart failed service
2. **Database Corruption**: Restore from latest backup (see DISASTER_RECOVERY.md)
3. **Security Breach**: Rotate all secrets, invalidate all JWT tokens, check audit logs

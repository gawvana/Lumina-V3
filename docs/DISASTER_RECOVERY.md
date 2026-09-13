# Lumina V3 — Disaster Recovery

## Backup Strategy

### PostgreSQL Automated Backups

#### Daily Backup Script
```bash
#!/bin/bash
# scripts/backup.sh
set -euo pipefail

BACKUP_DIR="/var/backups/lumina"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/lumina_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR"

# Create compressed backup
pg_dump -h localhost -U lumina -d lumina \
  --format=custom \
  --compress=9 \
  --file="${BACKUP_FILE}"

echo "Backup created: ${BACKUP_FILE}"
echo "Size: $(du -h ${BACKUP_FILE} | cut -f1)"

# Cleanup old backups
find "$BACKUP_DIR" -name "lumina_*.sql.gz" -mtime +${RETENTION_DAYS} -delete
echo "Cleaned backups older than ${RETENTION_DAYS} days"

# Verify backup integrity
pg_restore --list "${BACKUP_FILE}" > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "✅ Backup verified successfully"
else
  echo "❌ Backup verification FAILED"
  exit 1
fi
```

#### Schedule (cron)
```
# Daily at 3 AM
0 3 * * * /opt/lumina/scripts/backup.sh >> /var/log/lumina/backup.log 2>&1
```

### Restore Procedure

```bash
#!/bin/bash
# scripts/restore.sh
set -euo pipefail

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: ./restore.sh <backup_file>"
  exit 1
fi

echo "⚠️  This will REPLACE the current database!"
echo "Restoring from: $BACKUP_FILE"

# Stop services
docker compose stop backend bot

# Drop and recreate database
psql -h localhost -U lumina -d postgres -c "DROP DATABASE IF EXISTS lumina;"
psql -h localhost -U lumina -d postgres -c "CREATE DATABASE lumina;"

# Restore
pg_restore -h localhost -U lumina -d lumina \
  --format=custom \
  --clean \
  --if-exists \
  "$BACKUP_FILE"

echo "✅ Database restored"

# Run any pending migrations
cd /opt/lumina/backend && alembic upgrade head

# Restart services
docker compose start backend bot

echo "✅ Services restarted"
```

### Restore Verification
After every restore:
1. Check table counts: `SELECT relname, n_live_tup FROM pg_stat_user_tables;`
2. Verify a known record exists
3. Run health check: `curl http://localhost:8000/ready`
4. Run core test suite: `pytest tests/test_health.py tests/test_auth.py`

## Redis Recovery

Redis data is ephemeral (cache, sessions). On Redis failure:
1. Users will need to re-authenticate (sessions lost)
2. Cache will rebuild automatically
3. No data loss (all persistent data in PostgreSQL)

## Disaster Scenarios

### Scenario 1: Database Server Failure
1. Identify latest valid backup
2. Provision new PostgreSQL instance
3. Run restore script
4. Update DATABASE_URL in environment
5. Restart all services
6. Verify with health checks

### Scenario 2: Complete Server Loss
1. Provision new server
2. Clone repository
3. Configure environment (.env)
4. Start infrastructure (Docker Compose)
5. Restore database from backup
6. Configure Telegram webhook
7. Verify all services operational

### Scenario 3: Data Corruption
1. Stop affected services immediately
2. Identify corruption scope from audit logs
3. If localized: fix data manually using audit log (old_value/new_value)
4. If widespread: restore from last known good backup
5. Cross-reference audit logs to replay any valid changes made after backup

### Scenario 4: Security Breach
1. Rotate ALL secrets (APP_SECRET_KEY, TELEGRAM_BOT_TOKEN, DB passwords)
2. Invalidate all JWT tokens (by changing APP_SECRET_KEY)
3. Review audit logs for unauthorized actions
4. Check for data exfiltration
5. Patch vulnerability
6. Notify affected users

## Recovery Time Objectives
- **RTO** (Recovery Time Objective): < 1 hour
- **RPO** (Recovery Point Objective): < 24 hours (daily backups)

## Testing Recovery
Monthly drill:
1. Create a test backup
2. Restore to a separate database
3. Verify data integrity
4. Document results

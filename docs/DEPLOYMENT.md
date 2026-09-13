# Lumina V3 — Deployment Guide

## Prerequisites
- Docker 24+ & Docker Compose v2
- PostgreSQL 16+ (or use Docker)
- Redis 7+ (or use Docker)
- Domain with SSL certificate (for Telegram webhook)
- Telegram Bot token from @BotFather

## Environment Configuration

Copy `.env.example` to `.env` and configure all values:

```bash
cp .env.example .env
```

### Critical settings for production:
```
APP_ENV=production
APP_DEBUG=false
APP_SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
TELEGRAM_BOT_TOKEN=<from @BotFather>
TELEGRAM_WEBHOOK_SECRET=<generate with: python -c "import secrets; print(secrets.token_hex(16))">
TELEGRAM_WEBHOOK_URL=https://your-domain.com/bot/webhook
TELEGRAM_MINI_APP_URL=https://your-domain.com
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/lumina
REDIS_URL=redis://host:6379/0
```

## Docker Compose Deployment

### Development
```bash
docker compose up -d
```

### Production
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Manual Deployment

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
alembic upgrade head
uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --workers 4
```

### Bot
```bash
cd bot
python -m venv .venv
source .venv/bin/activate
pip install -e .
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run build
# Serve dist/ with nginx or similar
```

## Database Migrations

```bash
# Apply all pending migrations
cd backend && alembic upgrade head

# Create new migration after model changes
alembic revision --autogenerate -m "description"

# Rollback last migration
alembic downgrade -1

# Show current revision
alembic current
```

## Telegram Bot Setup

1. Create bot via @BotFather
2. Set commands:
   ```
   start - Start Lumina
   app - Open Mini App
   grades - View grades
   homework - View homework
   schedule - View schedule
   profile - View profile
   settings - Settings
   language - Change language
   help - Help
   ```
3. Configure Mini App URL via @BotFather → Edit Bot → Bot Settings → Menu Button
4. Set webhook URL (production): `TELEGRAM_WEBHOOK_URL`

## Health Checks

- Liveness: `GET /health` → `{"status": "ok"}`
- Readiness: `GET /ready` → `{"status": "ready", "database": true}`

## Nginx Configuration (Production)

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/ssl/your-domain.com.crt;
    ssl_certificate_key /etc/ssl/your-domain.com.key;

    # Frontend (Mini App)
    location / {
        root /var/www/lumina/frontend/dist;
        try_files $uri /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Request-ID $request_id;
    }

    # Bot webhook
    location /bot/webhook {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }

    # Health checks
    location /health {
        proxy_pass http://localhost:8000;
    }
}
```

# Lumina V3 — Telegram School OS

Electronic journal + diary + schedule + analytics + gamification for schools, delivered as Telegram Bot + Mini App.

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (recommended)

### Development Setup

```bash
# Clone & setup
cp .env.example .env
# Edit .env with your Telegram bot token and database credentials

# Start with Docker Compose
docker compose up -d

# Or run individually:

# Backend
cd backend
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:create_app --factory --reload

# Bot
cd bot
pip install -e "."
python main.py

# Frontend
cd frontend
npm install
npm run dev
```

### Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Telegram    │    │   Frontend   │    │  Telegram    │
│  Bot API     │◄──►│  Mini App    │    │  Web App     │
└──────┬───────┘    └──────┬───────┘    └──────────────┘
       │                   │
       ▼                   ▼
┌──────────────┐    ┌──────────────┐
│  aiogram 3.x │    │  FastAPI     │
│  Bot Server  │───►│  API Server  │
└──────────────┘    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
       ┌──────────┐ ┌──────────┐ ┌──────────┐
       │PostgreSQL│ │  Redis   │ │ Workers  │
       │   16     │ │    7     │ │  (ARQ)   │
       └──────────┘ └──────────┘ └──────────┘
```

### Roles
- **Admin**: Full school management, analytics, settings
- **Teacher**: Grades, attendance, homework, seating, notes
- **Student**: Dashboard, XP, achievements, skill tree, flashcards
- **Parent**: Child monitoring, absence requests, weekly summaries

### API Documentation
Available at `http://localhost:8000/docs` (development mode only).

### Localization
- Russian (RU) — default
- Uzbek (UZ) — full support

### Documentation
See `docs/` for detailed documentation:
- [Architecture](docs/ARCHITECTURE.md)
- [Security](docs/SECURITY.md)
- [Database](docs/DATABASE.md)
- [Deployment](docs/DEPLOYMENT.md)

## License
Proprietary — All rights reserved.

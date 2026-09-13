# Lumina Bot Skill

## Core Principles
- aiogram 3.x, Python 3.12 async.
- Strict middleware pipeline: Logging -> Throttling -> Auth -> i18n.
- Handlers: Routers with Telegram Web App launch button (`WebAppInfo`).
- Notifications: Centralized push dispatcher respecting `NotificationPreference`.
- Idempotency for Telegram updates.

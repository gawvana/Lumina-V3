import asyncio
import logging
import sys

import structlog
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from redis.asyncio import Redis

from config import config
from handlers.app import router as app_router
from handlers.grades import router as grades_router
from handlers.help import router as help_router
from handlers.homework import router as homework_router
from handlers.profile import router as profile_router
from handlers.schedule import router as schedule_router
from handlers.settings import router as settings_router

# Handlers
from handlers.start import router as start_router

# Middlewares
from middlewares.auth import AuthMiddleware
from middlewares.i18n import I18nMiddleware
from middlewares.logging import LoggingMiddleware
from middlewares.throttle import ThrottleMiddleware
from services.api_client import ApiClient

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
logger = structlog.get_logger()

async def on_startup(bot: Bot, base_url: str):
    logger.info("bot_startup")
    if config.WEBHOOK_URL:
        await bot.set_webhook(
            f"{config.WEBHOOK_URL}{config.WEBHOOK_SECRET}",
            secret_token=config.WEBHOOK_SECRET,
            allowed_updates=["message", "callback_query"]
        )

async def on_shutdown(bot: Bot):
    logger.info("bot_shutdown")
    if config.WEBHOOK_URL:
        await bot.delete_webhook()
    await bot.session.close()

def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    redis = Redis.from_url(config.REDIS_URL)
    api_client = ApiClient(config.API_BASE_URL)

    # Register Middlewares
    dp.update.outer_middleware(LoggingMiddleware())
    dp.message.middleware(ThrottleMiddleware(redis, rate_limit=1))

    auth_mw = AuthMiddleware(api_client)
    i18n_mw = I18nMiddleware()

    for router in [start_router, app_router, grades_router, homework_router,
                  schedule_router, profile_router, settings_router, help_router]:
        router.message.middleware(auth_mw)
        router.callback_query.middleware(auth_mw)
        router.message.middleware(i18n_mw)
        router.callback_query.middleware(i18n_mw)
        dp.include_router(router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    if config.WEBHOOK_URL:
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=config.WEBHOOK_SECRET
        )
        webhook_requests_handler.register(app, path=f"/{config.WEBHOOK_SECRET}")
        setup_application(app, dp, bot=bot)
        web.run_app(app, host="0.0.0.0", port=8000)
    else:
        asyncio.run(dp.start_polling(bot, api_client=api_client))

if __name__ == "__main__":
    main()

import uuid
from typing import Any, Awaitable, Callable, Dict

import structlog
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

logger = structlog.get_logger()

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        request_id = str(uuid.uuid4())
        data["request_id"] = request_id

        user_id = None
        if hasattr(event, "from_user") and event.from_user:
            user_id = event.from_user.id
        elif hasattr(event, "message") and event.message and event.message.from_user:
            user_id = event.message.from_user.id

        logger.info("update_received", request_id=request_id, update_type=type(event).__name__, user_id=user_id)

        try:
            result = await handler(event, data)
            logger.info("update_processed", request_id=request_id, update_type=type(event).__name__)
            return result
        except Exception as e:
            logger.error("update_failed", request_id=request_id, error=str(e), exc_info=True)
            raise

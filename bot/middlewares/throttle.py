import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from redis.asyncio import Redis


class ThrottleMiddleware(BaseMiddleware):
    def __init__(self, redis: Redis, rate_limit: int = 1):
        self.redis = redis
        self.rate_limit = rate_limit

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        user_id = event.from_user.id
        key = f"throttle:{user_id}"

        current_time = time.time()

        last_request = await self.redis.get(key)
        if last_request and current_time - float(last_request) < self.rate_limit:
            # Drop the request if it's too fast
            return None

        await self.redis.set(key, current_time, ex=self.rate_limit * 2)

        return await handler(event, data)

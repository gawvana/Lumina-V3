from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from services.api_client import ApiClient


class AuthMiddleware(BaseMiddleware):
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user_id = None
        if hasattr(event, "from_user") and event.from_user:
            user_id = event.from_user.id
        elif hasattr(event, "message") and event.message and event.message.from_user:
            user_id = event.message.from_user.id

        if user_id:
            user_data = await self.api_client.get_user(user_id)
            data["db_user"] = user_data

        return await handler(event, data)

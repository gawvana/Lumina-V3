from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from locales.ru import RU
from locales.uz import UZ


class I18nMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Default to RU if user not fetched or lang not set
        lang = "ru"
        user_data = data.get("db_user")

        if user_data and "language" in user_data:
            lang = user_data["language"]
        elif hasattr(event, "from_user") and event.from_user and event.from_user.language_code:
            lang = "uz" if event.from_user.language_code == "uz" else "ru"

        data["locale"] = UZ if lang == "uz" else RU
        data["lang_code"] = lang

        return await handler(event, data)

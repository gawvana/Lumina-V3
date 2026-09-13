from typing import Any, Dict

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import config
from keyboards.common import mini_app_button

router = Router(name="app")

@router.message(Command("app"))
async def app_handler(message: Message, locale: Dict[str, str], db_user: Dict[str, Any] | None):
    if not db_user:
        await message.answer(locale["not_registered"])
        return

    await message.answer(
        locale["app_button"],
        reply_markup=mini_app_button(config.MINI_APP_URL, locale["app_button"])
    )

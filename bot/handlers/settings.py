from typing import Any, Dict

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from keyboards.common import language_keyboard

# If we need to update language in backend we'd use api_client

router = Router(name="settings")

@router.message(Command("settings"))
@router.message(Command("language"))
async def settings_handler(message: Message, locale: Dict[str, str], db_user: Dict[str, Any] | None):
    if not db_user:
        await message.answer(locale["not_registered"])
        return

    await message.answer(locale["settings_title"] + "\n" + locale["welcome"], reply_markup=language_keyboard())

@router.callback_query(F.data.startswith("lang_"))
async def language_callback(callback: CallbackQuery, locale: Dict[str, str], db_user: Dict[str, Any] | None, api_client: Any = None):
    lang = callback.data.split("_")[1]
    if db_user and api_client:
        user_id = str(db_user.get("id"))
        await api_client.update_user_language(user_id, lang)

    msg = "Язык изменен на русский." if lang == "ru" else "Til o'zbek tiliga o'zgartirildi."
    await callback.message.edit_text(msg)
    await callback.answer()

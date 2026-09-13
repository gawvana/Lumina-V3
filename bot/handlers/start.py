from typing import Any, Dict

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.common import language_keyboard, main_menu_keyboard

router = Router(name="start")

@router.message(CommandStart())
async def start_handler(message: Message, locale: Dict[str, str], db_user: Dict[str, Any] | None):
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []

    if not db_user:
        # User not found in backend API
        # Handle invite logic here if args are present
        if args:
            invite_token = args[0]
            # TODO: Call API to register with invite token
            pass

        await message.answer(locale["welcome"], reply_markup=language_keyboard())
        return

    # User exists
    role = db_user.get("role", "student")
    welcome_text = f"{locale['main_menu']} - {locale.get(f'role_{role}', role)}"

    await message.answer(welcome_text, reply_markup=main_menu_keyboard(role))

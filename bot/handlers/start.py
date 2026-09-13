from typing import Any, Dict

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.common import language_keyboard, main_menu_keyboard

router = Router(name="start")

@router.message(CommandStart())
async def start_handler(message: Message, locale: Dict[str, str], db_user: Dict[str, Any] | None, api_client: Any = None):
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []

    if not db_user:
        if args and api_client and message.from_user:
            invite_token = args[0]
            await api_client.accept_invite(
                invite_token,
                message.from_user.id,
                message.from_user.full_name
            )
            # Re-fetch user if registered
            db_user = await api_client.get_user(message.from_user.id)
            if db_user:
                role = db_user.get("role", "student")
                welcome_text = f"{locale['main_menu']} - {locale.get(f'role_{role}', role)}"
                await message.answer(welcome_text, reply_markup=main_menu_keyboard(role))
                return

        await message.answer(locale["welcome"], reply_markup=language_keyboard())
        return

    # User exists
    role = db_user.get("role", "student")
    welcome_text = f"{locale['main_menu']} - {locale.get(f'role_{role}', role)}"

    await message.answer(welcome_text, reply_markup=main_menu_keyboard(role))

from typing import Any, Dict

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from services.api_client import ApiClient

router = Router(name="grades")

@router.message(Command("grades"))
async def grades_command(message: Message, locale: Dict[str, str], db_user: Dict[str, Any] | None, api_client: ApiClient):
    if not db_user:
        await message.answer(locale["not_registered"])
        return

    await _show_grades(message, locale, db_user, api_client)

@router.callback_query(F.data == "menu_grades")
async def grades_callback(callback: CallbackQuery, locale: Dict[str, str], db_user: Dict[str, Any] | None, api_client: ApiClient):
    if not db_user:
        await callback.answer(locale["not_registered"], show_alert=True)
        return

    await _show_grades(callback.message, locale, db_user, api_client)
    await callback.answer()

async def _show_grades(message: Message, locale: Dict[str, str], db_user: Dict[str, Any], api_client: ApiClient):
    user_id = db_user["id"]

    # If parent, get child's grades (simplification: getting first child for now)
    if db_user.get("role") == "parent" and db_user.get("children"):
        user_id = db_user["children"][0]["id"]

    grades = await api_client.get_grades(user_id)

    if not grades:
        await message.answer(locale["grades_empty"])
        return

    text = f"{locale['grades_title']}\n\n"
    for g in grades[:5]: # Show last 5
        text += f"• {g.get('subject')}: {g.get('value')} ({g.get('date')})\n"

    await message.answer(text)

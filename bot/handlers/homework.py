from typing import Any, Dict

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from services.api_client import ApiClient

router = Router(name="homework")

@router.message(Command("homework"))
async def homework_command(message: Message, locale: Dict[str, str], db_user: Dict[str, Any] | None, api_client: ApiClient):
    if not db_user:
        await message.answer(locale["not_registered"])
        return
    await _show_homework(message, locale, db_user, api_client)

@router.callback_query(F.data == "menu_homework")
async def homework_callback(callback: CallbackQuery, locale: Dict[str, str], db_user: Dict[str, Any] | None, api_client: ApiClient):
    if not db_user:
        await callback.answer(locale["not_registered"], show_alert=True)
        return
    await _show_homework(callback.message, locale, db_user, api_client)
    await callback.answer()

async def _show_homework(message: Message, locale: Dict[str, str], db_user: Dict[str, Any], api_client: ApiClient):
    class_id = db_user.get("class_id")
    if db_user.get("role") == "parent" and db_user.get("children"):
        class_id = db_user["children"][0].get("class_id")

    if not class_id:
        await message.answer(locale["homework_empty"])
        return

    hw = await api_client.get_homework(class_id)

    if not hw:
        await message.answer(locale["homework_empty"])
        return

    text = f"{locale['homework_title']}\n\n"
    for h in hw[:5]:
        status = "🔴" if h.get("is_overdue") else ("🟡" if h.get("due_soon") else "🟢")
        text += f"{status} {h.get('subject')}: {h.get('title')} (Due: {h.get('deadline')})\n"

    await message.answer(text)

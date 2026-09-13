import datetime
from typing import Any, Dict

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from services.api_client import ApiClient

router = Router(name="schedule")

def schedule_keyboard() -> InlineKeyboardMarkup:
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="Today", callback_data="sched_today")
    builder.button(text="Tomorrow", callback_data="sched_tomorrow")
    builder.adjust(2)
    return builder.as_markup()

@router.message(Command("schedule"))
async def schedule_command(message: Message, locale: Dict[str, str], db_user: Dict[str, Any] | None, api_client: ApiClient):
    if not db_user:
        await message.answer(locale["not_registered"])
        return
    await _show_schedule(message, "today", locale, db_user, api_client)

@router.callback_query(F.data == "menu_schedule")
async def schedule_menu_callback(callback: CallbackQuery, locale: Dict[str, str], db_user: Dict[str, Any] | None, api_client: ApiClient):
    if not db_user:
        await callback.answer(locale["not_registered"], show_alert=True)
        return
    await _show_schedule(callback.message, "today", locale, db_user, api_client)
    await callback.answer()

@router.callback_query(F.data.startswith("sched_"))
async def schedule_day_callback(callback: CallbackQuery, locale: Dict[str, str], db_user: Dict[str, Any] | None, api_client: ApiClient):
    if not db_user:
        await callback.answer(locale["not_registered"], show_alert=True)
        return

    day = callback.data.split("_")[1]
    await _show_schedule(callback.message, day, locale, db_user, api_client, edit_msg=True)
    await callback.answer()

async def _show_schedule(message: Message, day: str, locale: Dict[str, str], db_user: Dict[str, Any], api_client: ApiClient, edit_msg: bool = False):
    class_id = db_user.get("class_id")
    if db_user.get("role") == "parent" and db_user.get("children"):
        class_id = db_user["children"][0].get("class_id")

    if not class_id:
        text = locale["schedule_empty"]
    else:
        date_str = datetime.date.today().isoformat() if day == "today" else (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
        sched = await api_client.get_schedule(class_id, date_str)

        if not sched:
            text = locale["schedule_empty"]
        else:
            title = locale["schedule_today"] if day == "today" else locale["schedule_tomorrow"]
            text = f"{title}\n\n"
            for idx, s in enumerate(sched, 1):
                text += f"{idx}. {s.get('subject')} ({s.get('time')}) - {s.get('teacher')}\n"

    if edit_msg:
        await message.edit_text(text, reply_markup=schedule_keyboard())
    else:
        await message.answer(text, reply_markup=schedule_keyboard())

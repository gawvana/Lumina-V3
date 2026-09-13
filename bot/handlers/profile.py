from typing import Any, Dict

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="profile")

@router.message(Command("profile"))
async def profile_handler(message: Message, locale: Dict[str, str], db_user: Dict[str, Any] | None):
    if not db_user:
        await message.answer(locale["not_registered"])
        return

    role = locale.get(f"role_{db_user.get('role', 'student')}", db_user.get('role', 'student'))
    school = db_user.get("school_name", "N/A")
    level = db_user.get("level", 1)
    xp = db_user.get("xp", 0)
    streak = db_user.get("streak", 0)

    text = locale["profile_info"].format(
        role=role, school=school, level=level, xp=xp, streak=streak
    )

    await message.answer(text)

from typing import Dict

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="help")

@router.message(Command("help"))
async def help_handler(message: Message, locale: Dict[str, str]):
    await message.answer(locale["help_text"])

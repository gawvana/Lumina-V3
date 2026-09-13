from typing import Any, Dict

import structlog
from aiogram import Bot

logger = structlog.get_logger()

async def send_notification(bot: Bot, telegram_id: int, notification_type: str, data: Dict[str, Any], locale_dict: Dict[str, str]):
    try:
        text = ""
        if notification_type == "grade":
            text = locale_dict["notification_grade"].format(subject=data.get("subject"), grade=data.get("grade"))
        elif notification_type == "homework":
            text = locale_dict["notification_homework"].format(subject=data.get("subject"), title=data.get("title"))
        elif notification_type == "attendance":
            text = locale_dict["notification_attendance"].format(status=data.get("status"))
        elif notification_type == "achievement":
            text = locale_dict["notification_achievement"].format(title=data.get("title"))
        elif notification_type == "announcement":
            text = locale_dict["notification_announcement"].format(text=data.get("text"))
        else:
            text = f"New notification: {data}"

        await bot.send_message(chat_id=telegram_id, text=text)
    except Exception as e:
        logger.error("failed_send_notification", telegram_id=telegram_id, type=notification_type, error=str(e))

from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard(role: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if role == "student":
        builder.button(text="Grades", callback_data="menu_grades")
        builder.button(text="Homework", callback_data="menu_homework")
        builder.button(text="Schedule", callback_data="menu_schedule")
    builder.adjust(2)
    return builder.as_markup()

def language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🇷🇺 Русский", callback_data="lang_ru")
    builder.button(text="🇺🇿 O'zbekcha", callback_data="lang_uz")
    builder.adjust(2)
    return builder.as_markup()

def confirmation_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Yes", callback_data="confirm_yes")
    builder.button(text="No", callback_data="confirm_no")
    builder.adjust(2)
    return builder.as_markup()

def mini_app_button(url: str, text: str = "Open App") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=text, web_app=WebAppInfo(url=url))
    return builder.as_markup()

def back_button(callback_data: str = "back_main") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Back", callback_data=callback_data)
    return builder.as_markup()

def pagination_keyboard(page: int, total_pages: int, callback_prefix: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if page > 1:
        builder.button(text="⬅️", callback_data=f"{callback_prefix}_{page-1}")

    builder.button(text=f"{page}/{total_pages}", callback_data="ignore")

    if page < total_pages:
        builder.button(text="➡️", callback_data=f"{callback_prefix}_{page+1}")

    builder.adjust(3 if (page > 1 and page < total_pages) else 2)
    return builder.as_markup()

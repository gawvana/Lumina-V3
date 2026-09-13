"""Backend i18n — Russian and Uzbek translation catalogs."""

from __future__ import annotations

RU = {
    # Common
    "error.not_found": "Не найдено",
    "error.forbidden": "Доступ запрещён",
    "error.unauthorized": "Требуется авторизация",
    "error.validation": "Ошибка валидации",
    "error.conflict": "Конфликт данных",
    "error.rate_limited": "Слишком много запросов",
    "error.internal": "Внутренняя ошибка сервера",
    "success.created": "Успешно создано",
    "success.updated": "Успешно обновлено",
    "success.deleted": "Успешно удалено",

    # Auth
    "auth.invalid_init_data": "Неверные данные инициализации",
    "auth.expired": "Сессия истекла",
    "auth.user_not_found": "Пользователь не найден",

    # Grades
    "grade.created": "Оценка выставлена",
    "grade.updated": "Оценка обновлена",
    "grade.deleted": "Оценка удалена",
    "grade.restored": "Оценка восстановлена",
    "grade.new_notification": "Новая оценка по {subject}: {value}/{max_value}",

    # Attendance
    "attendance.marked": "Посещаемость отмечена",
    "attendance.present": "Присутствует",
    "attendance.absent": "Отсутствует",
    "attendance.late": "Опоздал(а)",
    "attendance.excused": "Уважительная причина",

    # Homework
    "homework.created": "Домашнее задание создано",
    "homework.due_soon": "Срок сдачи: {date}",
    "homework.overdue": "Просрочено!",
    "homework.submitted": "Домашнее задание сдано",

    # Notifications
    "notification.grade": "Новая оценка",
    "notification.homework": "Новое домашнее задание",
    "notification.attendance": "Посещаемость",
    "notification.achievement": "Достижение!",
    "notification.announcement": "Объявление",
    "notification.summary": "Еженедельная сводка",

    # Gamification
    "xp.earned": "+{amount} XP",
    "level.up": "Новый уровень: {level}!",
    "achievement.earned": "Получено достижение: {name}",
    "streak.continued": "Серия: {days} дней!",
}

UZ = {
    # Common
    "error.not_found": "Topilmadi",
    "error.forbidden": "Ruxsat berilmagan",
    "error.unauthorized": "Avtorizatsiya talab qilinadi",
    "error.validation": "Tekshirish xatosi",
    "error.conflict": "Ma'lumotlar ziddiyati",
    "error.rate_limited": "Juda ko'p so'rov",
    "error.internal": "Ichki server xatosi",
    "success.created": "Muvaffaqiyatli yaratildi",
    "success.updated": "Muvaffaqiyatli yangilandi",
    "success.deleted": "Muvaffaqiyatli o'chirildi",

    # Auth
    "auth.invalid_init_data": "Noto'g'ri boshlash ma'lumotlari",
    "auth.expired": "Sessiya muddati tugagan",
    "auth.user_not_found": "Foydalanuvchi topilmadi",

    # Grades
    "grade.created": "Baho qo'yildi",
    "grade.updated": "Baho yangilandi",
    "grade.deleted": "Baho o'chirildi",
    "grade.restored": "Baho tiklandi",
    "grade.new_notification": "{subject} fanidan yangi baho: {value}/{max_value}",

    # Attendance
    "attendance.marked": "Davomat belgilandi",
    "attendance.present": "Keldi",
    "attendance.absent": "Kelmadi",
    "attendance.late": "Kechikdi",
    "attendance.excused": "Sababli",

    # Homework
    "homework.created": "Uy vazifasi yaratildi",
    "homework.due_soon": "Topshirish muddati: {date}",
    "homework.overdue": "Muddati o'tgan!",
    "homework.submitted": "Uy vazifasi topshirildi",

    # Notifications
    "notification.grade": "Yangi baho",
    "notification.homework": "Yangi uy vazifasi",
    "notification.attendance": "Davomat",
    "notification.achievement": "Yutuq!",
    "notification.announcement": "E'lon",
    "notification.summary": "Haftalik hisobot",

    # Gamification
    "xp.earned": "+{amount} XP",
    "level.up": "Yangi daraja: {level}!",
    "achievement.earned": "Yutuq olindi: {name}",
    "streak.continued": "Seriya: {days} kun!",
}


def get_translations(language: str = "ru") -> dict[str, str]:
    """Get translation catalog by language code."""
    if language == "uz":
        return UZ
    return RU


def t(key: str, language: str = "ru", **kwargs: str) -> str:
    """Translate a key with optional string formatting."""
    catalog = get_translations(language)
    template = catalog.get(key, key)
    if kwargs:
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError):
            return template
    return template

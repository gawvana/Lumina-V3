"""Notification service — creates and delivers notifications across channels."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Notification,
    NotificationPreference,
    NotificationType,
)


async def send_notification(
    db: AsyncSession,
    *,
    school_id: uuid.UUID,
    user_id: uuid.UUID,
    notification_type: NotificationType,
    title: str,
    body: str,
    data: dict | None = None,
) -> Notification | None:
    """
    Create a notification, respecting user preferences.
    Returns None if user has disabled this notification type.
    """
    # Check preferences
    pref_result = await db.execute(
        select(NotificationPreference).where(
            NotificationPreference.user_id == user_id,
            NotificationPreference.notification_type == notification_type,
        )
    )
    pref = pref_result.scalar_one_or_none()

    if pref and not pref.enabled:
        return None

    notification = Notification(
        school_id=school_id,
        user_id=user_id,
        type=notification_type,
        title=title,
        body=body,
        data=data,
    )
    db.add(notification)
    await db.flush()
    return notification


async def send_grade_notification(
    db: AsyncSession,
    *,
    school_id: uuid.UUID,
    student_user_id: uuid.UUID,
    parent_user_ids: list[uuid.UUID],
    subject_name: str,
    grade_value: float,
    grade_max: float,
) -> None:
    """Send grade notification to student and their parents."""
    body = f"Новая оценка по {subject_name}: {grade_value}/{grade_max}"

    # To student
    await send_notification(
        db,
        school_id=school_id,
        user_id=student_user_id,
        notification_type=NotificationType.GRADE,
        title="Новая оценка",
        body=body,
        data={"subject": subject_name, "value": grade_value, "max_value": grade_max},
    )

    # To parents
    for parent_id in parent_user_ids:
        await send_notification(
            db,
            school_id=school_id,
            user_id=parent_id,
            notification_type=NotificationType.GRADE,
            title="Оценка ребёнка",
            body=body,
            data={"subject": subject_name, "value": grade_value, "max_value": grade_max},
        )


async def send_homework_notification(
    db: AsyncSession,
    *,
    school_id: uuid.UUID,
    user_ids: list[uuid.UUID],
    homework_title: str,
    due_date: str,
) -> None:
    """Send homework notification to all students in a class."""
    for user_id in user_ids:
        await send_notification(
            db,
            school_id=school_id,
            user_id=user_id,
            notification_type=NotificationType.HOMEWORK,
            title="Новое домашнее задание",
            body=f"{homework_title} — до {due_date}",
            data={"title": homework_title, "due_date": due_date},
        )


async def send_attendance_notification(
    db: AsyncSession,
    *,
    school_id: uuid.UUID,
    parent_user_ids: list[uuid.UUID],
    student_name: str,
    status: str,
    date: str,
) -> None:
    """Send attendance notification to parents."""
    status_labels = {
        "absent": "отсутствует",
        "late": "опоздал(а)",
        "excused": "отсутствует (уважит.)",
    }
    label = status_labels.get(status, status)

    for parent_id in parent_user_ids:
        await send_notification(
            db,
            school_id=school_id,
            user_id=parent_id,
            notification_type=NotificationType.ATTENDANCE,
            title="Посещаемость",
            body=f"{student_name} — {label} ({date})",
            data={"student_name": student_name, "status": status, "date": date},
        )

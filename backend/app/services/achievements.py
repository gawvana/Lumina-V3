"""Achievement engine — automatically checks and awards achievements to students."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Achievement,
    Attendance,
    AttendanceStatus,
    Grade,
    Student,
    UserAchievement,
    XPSource,
    XPTransaction,
)


async def check_and_award_achievements(
    db: AsyncSession,
    student_id: uuid.UUID,
    school_id: uuid.UUID,
) -> list[Achievement]:
    """
    Check all achievement trigger conditions for a student
    and award any newly earned achievements.
    Returns list of newly awarded achievements.
    """
    # Get all achievements for this school
    result = await db.execute(
        select(Achievement).where(Achievement.school_id == school_id)
    )
    all_achievements = result.scalars().all()

    # Get already earned
    earned_result = await db.execute(
        select(UserAchievement.achievement_id).where(
            UserAchievement.student_id == student_id
        )
    )
    earned_ids = {row for row in earned_result.scalars().all()}

    # Get student
    student = (await db.execute(
        select(Student).where(Student.id == student_id)
    )).scalar_one()

    newly_awarded: list[Achievement] = []

    for achievement in all_achievements:
        if achievement.id in earned_ids:
            continue

        if not achievement.trigger_condition:
            continue

        condition = achievement.trigger_condition
        triggered = await _check_condition(db, student, school_id, condition)

        if triggered:
            # Award achievement
            db.add(UserAchievement(
                school_id=school_id,
                student_id=student_id,
                achievement_id=achievement.id,
                earned_at=datetime.now(UTC),
            ))

            # Award XP
            if achievement.xp_reward > 0:
                student.xp += achievement.xp_reward
                db.add(XPTransaction(
                    school_id=school_id,
                    student_id=student_id,
                    amount=achievement.xp_reward,
                    source=XPSource.ACHIEVEMENT,
                    source_id=achievement.id,
                    description=f"Achievement: {achievement.name}",
                    balance_after=student.xp,
                ))

            newly_awarded.append(achievement)

    # Update level based on XP
    _update_level(student)

    return newly_awarded


async def _check_condition(
    db: AsyncSession,
    student: Student,
    school_id: uuid.UUID,
    condition: dict,
) -> bool:
    """Evaluate a single trigger condition."""
    ctype = condition.get("type")

    if ctype == "grade_count":
        # e.g., {"type": "grade_count", "threshold": 10, "min_value": 4}
        threshold = condition.get("threshold", 0)
        min_value = condition.get("min_value", 0)
        count = (await db.execute(
            select(func.count()).where(
                Grade.student_id == student.id,
                Grade.school_id == school_id,
                Grade.value >= min_value,
                Grade.is_deleted == False,
            )
        )).scalar() or 0
        return count >= threshold

    elif ctype == "streak":
        threshold = condition.get("threshold", 0)
        return student.streak_days >= threshold

    elif ctype == "attendance_perfect":
        # No absences in last N days
        days = condition.get("days", 30)
        absent_count = (await db.execute(
            select(func.count()).where(
                Attendance.student_id == student.id,
                Attendance.status == AttendanceStatus.ABSENT,
            )
        )).scalar() or 0
        return absent_count == 0

    elif ctype == "level":
        threshold = condition.get("threshold", 0)
        return student.level >= threshold

    elif ctype == "xp":
        threshold = condition.get("threshold", 0)
        return student.xp >= threshold

    return False


def _update_level(student: Student) -> None:
    """Deterministic level calculation: level N requires N*100 total XP."""
    new_level = 1
    xp_needed = 100
    remaining_xp = student.xp

    while remaining_xp >= xp_needed:
        remaining_xp -= xp_needed
        new_level += 1
        xp_needed = new_level * 100

    student.level = new_level

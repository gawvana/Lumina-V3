"""Parent API — child linking, grades/attendance view, absence requests, summaries."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from datetime import date as dt_date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.errors import ForbiddenError, NotFoundError
from app.core.security import CurrentUser, require_role
from app.models import (
    Attendance,
    Consent,
    ConsentType,
    Grade,
    Homework,
    HomeworkSubmission,
    Notification,
    NotificationPreference,
    NotificationType,
    Parent,
    SchoolAnnouncement,
    Student,
    StudentParent,
    UserRole,
)
from app.schemas import IDResponse, SuccessResponse

router = APIRouter()

parent_dep = require_role(UserRole.PARENT)


async def _get_parent(current_user: CurrentUser, db: AsyncSession) -> Parent:
    result = await db.execute(select(Parent).where(Parent.user_id == current_user.user_id))
    parent = result.scalar_one_or_none()
    if not parent:
        raise ForbiddenError("Parent profile not found")
    return parent


async def _verify_child_access(parent: Parent, student_id: uuid.UUID, db: AsyncSession) -> Student:
    """Verify parent has linked access to this student."""
    result = await db.execute(select(StudentParent).where(
        StudentParent.parent_id == parent.id,
        StudentParent.student_id == student_id,
    ))
    link = result.scalar_one_or_none()
    if not link:
        raise ForbiddenError("No access to this student")

    student_result = await db.execute(select(Student).where(Student.id == student_id))
    return student_result.scalar_one()


# ── Children ────────────────────────────────────────────────────────

@router.get("/children")
async def list_children(
    current_user: CurrentUser = Depends(parent_dep),
    db: AsyncSession = Depends(get_db),
):
    parent = await _get_parent(current_user, db)

    result = await db.execute(
        select(StudentParent, Student).join(Student, StudentParent.student_id == Student.id)
        .where(StudentParent.parent_id == parent.id)
    )
    links = result.all()

    children = []
    for link, student in links:
        children.append({
            "id": str(student.id),
            "student_id": str(student.id),
            "user_id": str(student.user_id),
            "class_id": str(student.class_id) if student.class_id else None,
            "relationship_type": link.relationship_type,
            "is_primary": link.is_primary,
        })

    return children


# ── Grades ──────────────────────────────────────────────────────────

@router.get("/children/{student_id}/grades")
async def get_child_grades(
    student_id: str,
    subject_id: str | None = None,
    current_user: CurrentUser = Depends(parent_dep),
    db: AsyncSession = Depends(get_db),
):
    parent = await _get_parent(current_user, db)
    student = await _verify_child_access(parent, uuid.UUID(student_id), db)

    q = select(Grade).where(
        Grade.student_id == student.id,
        Grade.school_id == current_user.school_id,
        Grade.is_deleted == False,
    )
    if subject_id:
        q = q.where(Grade.subject_id == uuid.UUID(subject_id))

    result = await db.execute(q.order_by(Grade.date.desc()))
    grades = result.scalars().all()

    return [{
        "id": str(g.id), "value": g.value, "max_value": g.max_value,
        "subject_id": str(g.subject_id), "date": g.date.isoformat(),
        "comment": g.comment,
    } for g in grades]


# ── Attendance ──────────────────────────────────────────────────────

@router.get("/children/{student_id}/attendance")
async def get_child_attendance(
    student_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
    current_user: CurrentUser = Depends(parent_dep),
    db: AsyncSession = Depends(get_db),
):
    parent = await _get_parent(current_user, db)
    student = await _verify_child_access(parent, uuid.UUID(student_id), db)

    q = select(Attendance).where(
        Attendance.student_id == student.id,
        Attendance.school_id == current_user.school_id,
    )
    if start_date:
        q = q.where(Attendance.date >= dt_date.fromisoformat(start_date))
    if end_date:
        q = q.where(Attendance.date <= dt_date.fromisoformat(end_date))

    result = await db.execute(q.order_by(Attendance.date.desc()))
    records = result.scalars().all()

    return [{
        "id": str(a.id), "date": a.date.isoformat(), "status": a.status.value,
        "subject_id": str(a.subject_id), "note": a.note,
        "late_minutes": a.late_minutes,
    } for a in records]


# ── Homework ────────────────────────────────────────────────────────

@router.get("/children/{student_id}/homework")
async def get_child_homework(
    student_id: str,
    current_user: CurrentUser = Depends(parent_dep),
    db: AsyncSession = Depends(get_db),
):
    parent = await _get_parent(current_user, db)
    student = await _verify_child_access(parent, uuid.UUID(student_id), db)

    # Get homework for child's class
    q = select(Homework).where(
        Homework.school_id == current_user.school_id,
        Homework.class_id == student.class_id,
    ).order_by(Homework.due_date.desc())

    result = await db.execute(q)
    homeworks = result.scalars().all()

    # Get submissions
    sub_result = await db.execute(select(HomeworkSubmission).where(
        HomeworkSubmission.student_id == student.id,
    ))
    submissions = {str(s.homework_id): s for s in sub_result.scalars().all()}

    return [{
        "id": str(hw.id), "title": hw.title, "due_date": hw.due_date.isoformat(),
        "subject_id": str(hw.subject_id), "status": hw.status.value,
        "submitted": str(hw.id) in submissions,
        "submission_status": submissions.get(str(hw.id)) and submissions[str(hw.id)].status.value,
    } for hw in homeworks]


# ── Absence Requests ───────────────────────────────────────────────

@router.post("/children/{student_id}/absence-request", response_model=IDResponse, status_code=201)
async def create_absence_request(
    student_id: str,
    date: str,
    reason: str,
    current_user: CurrentUser = Depends(parent_dep),
    db: AsyncSession = Depends(get_db),
):
    parent = await _get_parent(current_user, db)
    student = await _verify_child_access(parent, uuid.UUID(student_id), db)

    # Create notification to admin/teachers
    notification = Notification(
        school_id=current_user.school_id,
        user_id=current_user.user_id,  # Will be rerouted to admins
        type=NotificationType.ATTENDANCE,
        title="Absence Request",
        body=f"Parent requests excused absence for {date}: {reason}",
        data={"student_id": student_id, "date": date, "reason": reason},
    )
    db.add(notification)
    await db.flush()

    return IDResponse(id=str(notification.id))


# ── Notifications ──────────────────────────────────────────────────

@router.get("/notifications")
async def get_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(parent_dep),
    db: AsyncSession = Depends(get_db),
):
    q = select(Notification).where(
        Notification.user_id == current_user.user_id,
        Notification.school_id == current_user.school_id,
    ).order_by(Notification.created_at.desc())

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0
    result = await db.execute(q.offset((page - 1) * per_page).limit(per_page))
    notifications = result.scalars().all()

    return {
        "items": [{
            "id": str(n.id), "type": n.type.value, "title": n.title,
            "body": n.body, "is_read": n.is_read, "data": n.data,
            "created_at": n.created_at.isoformat(),
        } for n in notifications],
        "total": total, "page": page, "per_page": per_page,
    }


@router.put("/notifications/{notification_id}/read", response_model=SuccessResponse)
async def mark_notification_read(
    notification_id: str,
    current_user: CurrentUser = Depends(parent_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Notification).where(
        Notification.id == uuid.UUID(notification_id),
        Notification.user_id == current_user.user_id,
    ))
    notif = result.scalar_one_or_none()
    if not notif:
        raise NotFoundError("Notification", notification_id)

    notif.is_read = True
    notif.read_at = datetime.now(UTC)
    return SuccessResponse(message="Marked as read")


# ── Notification Preferences ──────────────────────────────────────

@router.get("/notification-preferences")
async def get_notification_preferences(
    current_user: CurrentUser = Depends(parent_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(NotificationPreference).where(
        NotificationPreference.user_id == current_user.user_id,
    ))
    prefs = result.scalars().all()
    return [{
        "type": p.notification_type.value, "enabled": p.enabled,
        "bot_enabled": p.bot_enabled, "digest_only": p.digest_only,
    } for p in prefs]


# ── Consent ─────────────────────────────────────────────────────────

@router.get("/children/{student_id}/consents")
async def get_consents(
    student_id: str,
    current_user: CurrentUser = Depends(parent_dep),
    db: AsyncSession = Depends(get_db),
):
    parent = await _get_parent(current_user, db)
    await _verify_child_access(parent, uuid.UUID(student_id), db)

    result = await db.execute(select(Consent).where(
        Consent.parent_id == parent.id,
        Consent.student_id == uuid.UUID(student_id),
    ))
    consents = result.scalars().all()

    return [{
        "id": str(c.id), "type": c.consent_type.value,
        "granted": c.granted, "details": c.details,
        "granted_at": c.granted_at.isoformat() if c.granted_at else None,
    } for c in consents]


@router.put("/children/{student_id}/consents/{consent_type}", response_model=SuccessResponse)
async def update_consent(
    student_id: str,
    consent_type: str,
    granted: bool,
    current_user: CurrentUser = Depends(parent_dep),
    db: AsyncSession = Depends(get_db),
):
    parent = await _get_parent(current_user, db)
    await _verify_child_access(parent, uuid.UUID(student_id), db)

    ct = ConsentType(consent_type)

    result = await db.execute(select(Consent).where(
        Consent.parent_id == parent.id,
        Consent.student_id == uuid.UUID(student_id),
        Consent.consent_type == ct,
    ))
    consent = result.scalar_one_or_none()

    if consent:
        consent.granted = granted
        if granted:
            consent.granted_at = datetime.now(UTC)
            consent.revoked_at = None
        else:
            consent.revoked_at = datetime.now(UTC)
    else:
        db.add(Consent(
            school_id=current_user.school_id,
            parent_id=parent.id,
            student_id=uuid.UUID(student_id),
            consent_type=ct,
            granted=granted,
            granted_at=datetime.now(UTC) if granted else None,
        ))

    return SuccessResponse(message="Consent updated")


# ── Announcements ──────────────────────────────────────────────────

@router.get("/announcements")
async def get_announcements(
    current_user: CurrentUser = Depends(parent_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(SchoolAnnouncement).where(
        SchoolAnnouncement.school_id == current_user.school_id,
    ).order_by(SchoolAnnouncement.created_at.desc()).limit(50))
    anns = result.scalars().all()

    return [{
        "id": str(a.id), "title": a.title, "content": a.content,
        "is_pinned": a.is_pinned, "created_at": a.created_at.isoformat(),
    } for a in anns if "parent" in (a.target_roles or [])]


# ── Weekly Summary ──────────────────────────────────────────────────

@router.get("/children/{student_id}/weekly-summary")
async def get_weekly_summary(
    student_id: str,
    current_user: CurrentUser = Depends(parent_dep),
    db: AsyncSession = Depends(get_db),
):
    """Generate weekly summary from REAL data only — no AI hallucinations."""
    parent = await _get_parent(current_user, db)
    student = await _verify_child_access(parent, uuid.UUID(student_id), db)

    from datetime import timedelta

    today = dt_date.today()
    week_start = today - timedelta(days=today.weekday())

    # Grades this week
    grades = (await db.execute(select(Grade).where(
        Grade.student_id == student.id,
        Grade.school_id == current_user.school_id,
        Grade.date >= week_start,
        Grade.is_deleted == False,
    ))).scalars().all()

    # Attendance this week
    attendance = (await db.execute(select(Attendance).where(
        Attendance.student_id == student.id,
        Attendance.date >= week_start,
    ))).scalars().all()

    # Homework due this week
    homeworks = (await db.execute(select(Homework).where(
        Homework.class_id == student.class_id,
        Homework.due_date >= week_start,
        Homework.due_date <= today + timedelta(days=7 - today.weekday()),
    ))).scalars().all()

    avg_grade = sum(g.value / g.max_value for g in grades) / len(grades) * 100 if grades else None
    absent_count = sum(1 for a in attendance if a.status.value in ("absent",))
    late_count = sum(1 for a in attendance if a.status.value in ("late",))

    return {
        "week_start": week_start.isoformat(),
        "grades_count": len(grades),
        "average_grade": round(avg_grade, 1) if avg_grade else None,
        "attendance": {
            "present": sum(1 for a in attendance if a.status.value == "present"),
            "absent": absent_count,
            "late": late_count,
            "excused": sum(1 for a in attendance if a.status.value == "excused"),
        },
        "homework_total": len(homeworks),
        "xp": student.xp,
        "level": student.level,
        "streak": student.streak_days,
    }

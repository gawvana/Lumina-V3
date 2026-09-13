"""Student API — dashboard, grades, GPA, homework, XP, achievements, skills, flashcards, vibes."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.errors import ForbiddenError, NotFoundError
from app.core.security import CurrentUser, require_role
from app.models import (
    Achievement,
    DashboardLayout,
    Flashcard,
    FlashcardSet,
    FlashcardStatus,
    Grade,
    Homework,
    HomeworkSubmission,
    Schedule,
    Skill,
    Student,
    StudentSkill,
    StudentVibe,
    Title,
    UserAchievement,
    UserRole,
    VibeType,
    XPSource,
    XPTransaction,
)
from app.schemas import IDResponse, SuccessResponse

router = APIRouter()

student_dep = require_role(UserRole.STUDENT)


async def _get_student(current_user: CurrentUser, db: AsyncSession) -> Student:
    result = await db.execute(select(Student).where(
        Student.user_id == current_user.user_id,
    ))
    student = result.scalar_one_or_none()
    if not student:
        raise ForbiddenError("Student profile not found")
    return student


def _update_streak(student: Student) -> bool:
    now = datetime.now(UTC)
    today = now.date()
    if not student.streak_last_date:
        student.streak_days = 1
        student.streak_last_date = now
        return True
    last_date = student.streak_last_date.date() if hasattr(student.streak_last_date, "date") else student.streak_last_date
    delta = (today - last_date).days
    if delta == 1:
        student.streak_days += 1
        student.streak_last_date = now
        return True
    elif delta > 1:
        student.streak_days = 1
        student.streak_last_date = now
        return True
    return False


# ── Dashboard ───────────────────────────────────────────────────────

@router.get("/dashboard")
async def get_dashboard(
    current_user: CurrentUser = Depends(student_dep),
    db: AsyncSession = Depends(get_db),
):
    student = await _get_student(current_user, db)
    if _update_streak(student):
        await db.commit()
        await db.refresh(student)


    # Recent grades
    grades_result = await db.execute(
        select(Grade).where(
            Grade.student_id == student.id,
            Grade.school_id == current_user.school_id,
            Grade.is_deleted == False,
        ).order_by(Grade.date.desc()).limit(10)
    )
    recent_grades = grades_result.scalars().all()

    # Today's schedule
    from datetime import date

    today_dow = date.today().isoweekday()
    schedule_result = await db.execute(
        select(Schedule).where(
            Schedule.school_id == current_user.school_id,
            Schedule.class_id == student.class_id,
            Schedule.day_of_week == today_dow,
            Schedule.is_active == True,
        ).order_by(Schedule.slot_number)
    )
    today_schedule = schedule_result.scalars().all()

    # Pending homework
    hw_result = await db.execute(
        select(Homework).where(
            Homework.school_id == current_user.school_id,
            Homework.class_id == student.class_id,
            Homework.due_date >= date.today(),
            Homework.status == "active",
        ).order_by(Homework.due_date)
    )
    pending_hw = hw_result.scalars().all()

    # Recent achievements
    ach_result = await db.execute(
        select(UserAchievement).where(
            UserAchievement.student_id == student.id,
        ).order_by(UserAchievement.earned_at.desc()).limit(5)
    )
    recent_achievements = ach_result.scalars().all()

    return {
        "student": {
            "id": str(student.id),
            "xp": student.xp,
            "level": student.level,
            "streak_days": student.streak_days,
            "profile_skin": student.profile_skin,
            "profile_frame": student.profile_frame,
            "profile_aura": student.profile_aura,
        },
        "recent_grades": [{
            "id": str(g.id), "value": g.value, "max_value": g.max_value,
            "date": g.date.isoformat(), "subject_id": str(g.subject_id),
        } for g in recent_grades],
        "today_schedule": [{
            "id": str(s.id), "subject_id": str(s.subject_id),
            "start_time": s.start_time.isoformat(), "end_time": s.end_time.isoformat(),
            "room": s.room, "slot_number": s.slot_number,
        } for s in today_schedule],
        "pending_homework": [{
            "id": str(hw.id), "title": hw.title, "due_date": hw.due_date.isoformat(),
            "subject_id": str(hw.subject_id),
        } for hw in pending_hw],
        "recent_achievements": [{
            "id": str(a.id), "achievement_id": str(a.achievement_id),
            "earned_at": a.earned_at.isoformat(),
        } for a in recent_achievements],
    }


# ── Grades & GPA ────────────────────────────────────────────────────

@router.get("/grades")
async def get_grades(
    subject_id: str | None = None,
    term_id: str | None = None,
    current_user: CurrentUser = Depends(student_dep),
    db: AsyncSession = Depends(get_db),
):
    student = await _get_student(current_user, db)

    q = select(Grade).where(
        Grade.student_id == student.id,
        Grade.school_id == current_user.school_id,
        Grade.is_deleted == False,
    )
    if subject_id:
        q = q.where(Grade.subject_id == uuid.UUID(subject_id))
    if term_id:
        q = q.where(Grade.term_id == uuid.UUID(term_id))

    result = await db.execute(q.order_by(Grade.date.desc()))
    grades = result.scalars().all()

    return [{
        "id": str(g.id), "value": g.value, "max_value": g.max_value,
        "subject_id": str(g.subject_id), "date": g.date.isoformat(),
        "comment": g.comment, "tags": g.tags,
        "is_correction": g.is_correction,
    } for g in grades]


@router.get("/gpa")
async def get_gpa(
    term_id: str | None = None,
    current_user: CurrentUser = Depends(student_dep),
    db: AsyncSession = Depends(get_db),
):
    student = await _get_student(current_user, db)

    q = select(Grade).where(
        Grade.student_id == student.id,
        Grade.school_id == current_user.school_id,
        Grade.is_deleted == False,
    )
    if term_id:
        q = q.where(Grade.term_id == uuid.UUID(term_id))

    result = await db.execute(q)
    grades = result.scalars().all()

    if not grades:
        return {"gpa": 0.0, "total_grades": 0, "by_subject": {}}

    # Calculate weighted GPA by subject
    by_subject: dict[str, list] = {}
    for g in grades:
        sid = str(g.subject_id)
        if sid not in by_subject:
            by_subject[sid] = []
        by_subject[sid].append(g.value / g.max_value if g.max_value > 0 else 0)

    subject_averages = {sid: sum(vals) / len(vals) for sid, vals in by_subject.items()}
    overall_gpa = sum(subject_averages.values()) / len(subject_averages) if subject_averages else 0

    return {
        "gpa": round(overall_gpa * 100, 2),
        "total_grades": len(grades),
        "by_subject": {sid: round(avg * 100, 2) for sid, avg in subject_averages.items()},
    }


# ── XP & Levels ─────────────────────────────────────────────────────

@router.get("/xp")
async def get_xp(
    current_user: CurrentUser = Depends(student_dep),
    db: AsyncSession = Depends(get_db),
):
    student = await _get_student(current_user, db)

    # Level thresholds: level N requires N*100 XP (deterministic)
    current_level_xp = student.level * 100
    next_level_xp = (student.level + 1) * 100
    progress = (student.xp - (student.level * (student.level - 1) * 50)) / (next_level_xp - current_level_xp + 100)

    # Recent transactions
    tx_result = await db.execute(
        select(XPTransaction).where(
            XPTransaction.student_id == student.id,
        ).order_by(XPTransaction.created_at.desc()).limit(20)
    )
    transactions = tx_result.scalars().all()

    return {
        "xp": student.xp,
        "level": student.level,
        "next_level_xp": next_level_xp,
        "progress": min(max(progress, 0), 1.0),
        "streak_days": student.streak_days,
        "transactions": [{
            "id": str(t.id), "amount": t.amount, "source": t.source.value,
            "description": t.description, "balance_after": t.balance_after,
            "created_at": t.created_at.isoformat(),
        } for t in transactions],
    }


# ── Achievements ────────────────────────────────────────────────────

@router.get("/achievements")
async def get_achievements(
    current_user: CurrentUser = Depends(student_dep),
    db: AsyncSession = Depends(get_db),
):
    student = await _get_student(current_user, db)

    # All available achievements
    all_ach = (await db.execute(
        select(Achievement).where(Achievement.school_id == current_user.school_id)
    )).scalars().all()

    # Earned achievements
    earned = (await db.execute(
        select(UserAchievement).where(UserAchievement.student_id == student.id)
    )).scalars().all()
    earned_ids = {str(e.achievement_id) for e in earned}

    return {
        "achievements": [{
            "id": str(a.id), "name": a.name, "description": a.description,
            "icon": a.icon, "category": a.category.value, "rarity": a.rarity,
            "xp_reward": a.xp_reward, "earned": str(a.id) in earned_ids,
            "is_hidden": a.is_hidden and str(a.id) not in earned_ids,
        } for a in all_ach if not a.is_hidden or str(a.id) in earned_ids],
        "total_earned": len(earned),
        "total_available": len(all_ach),
    }


# ── Titles ──────────────────────────────────────────────────────────

@router.get("/titles")
async def get_titles(
    current_user: CurrentUser = Depends(student_dep),
    db: AsyncSession = Depends(get_db),
):
    student = await _get_student(current_user, db)

    titles = (await db.execute(
        select(Title).where(
            Title.school_id == current_user.school_id,
            Title.min_level <= student.level,
        )
    )).scalars().all()

    return [{
        "id": str(t.id), "name": t.name, "description": t.description,
        "color": t.color, "icon": t.icon, "rarity": t.rarity,
        "is_active": student.active_title_id == t.id,
    } for t in titles]


@router.put("/titles/{title_id}/equip", response_model=SuccessResponse)
async def equip_title(
    title_id: str,
    current_user: CurrentUser = Depends(student_dep),
    db: AsyncSession = Depends(get_db),
):
    student = await _get_student(current_user, db)
    student.active_title_id = uuid.UUID(title_id)
    return SuccessResponse(message="Title equipped")


# ── Vibe Tracking ───────────────────────────────────────────────────

@router.post("/vibes", response_model=IDResponse, status_code=201)
async def log_vibe(
    vibe: str,
    note: str | None = None,
    current_user: CurrentUser = Depends(student_dep),
    db: AsyncSession = Depends(get_db),
):
    student = await _get_student(current_user, db)

    sv = StudentVibe(
        school_id=current_user.school_id,
        student_id=student.id,
        vibe=VibeType(vibe),
        note=note,
        is_private=True,  # Private by default
    )
    db.add(sv)
    await db.flush()
    return IDResponse(id=str(sv.id))


@router.get("/vibes")
async def get_vibes(
    limit: int = Query(30, ge=1, le=100),
    current_user: CurrentUser = Depends(student_dep),
    db: AsyncSession = Depends(get_db),
):
    student = await _get_student(current_user, db)

    result = await db.execute(
        select(StudentVibe).where(
            StudentVibe.student_id == student.id,
        ).order_by(StudentVibe.created_at.desc()).limit(limit)
    )
    vibes = result.scalars().all()

    return [{
        "id": str(v.id), "vibe": v.vibe.value, "note": v.note,
        "created_at": v.created_at.isoformat(),
    } for v in vibes]


# ── Skill Tree ──────────────────────────────────────────────────────

@router.get("/skills")
async def get_skill_tree(
    current_user: CurrentUser = Depends(student_dep),
    db: AsyncSession = Depends(get_db),
):
    student = await _get_student(current_user, db)

    skills = (await db.execute(
        select(Skill).where(Skill.school_id == current_user.school_id)
    )).scalars().all()

    student_skills = (await db.execute(
        select(StudentSkill).where(StudentSkill.student_id == student.id)
    )).scalars().all()
    ss_map = {str(ss.skill_id): ss for ss in student_skills}

    return [{
        "id": str(s.id), "name": s.name, "description": s.description,
        "category": s.category.value, "max_level": s.max_level,
        "prerequisites": s.prerequisites,
        "tree_x": s.tree_x, "tree_y": s.tree_y,
        "current_level": (ss_map.get(str(s.id)) and ss_map[str(s.id)].current_level) or 0,
        "progress": (ss_map.get(str(s.id)) and ss_map[str(s.id)].progress) or 0.0,
        "mastered": bool(ss_map.get(str(s.id)) and ss_map[str(s.id)].mastered_at),
    } for s in skills]


# ── Flashcards ──────────────────────────────────────────────────────

@router.get("/flashcards")
async def list_flashcard_sets(
    current_user: CurrentUser = Depends(student_dep),
    db: AsyncSession = Depends(get_db),
):
    student = await _get_student(current_user, db)

    sets = (await db.execute(
        select(FlashcardSet).where(FlashcardSet.student_id == student.id)
        .order_by(FlashcardSet.updated_at.desc())
    )).scalars().all()

    return [{
        "id": str(s.id), "title": s.title, "description": s.description,
        "card_count": s.card_count, "last_reviewed_at": s.last_reviewed_at.isoformat() if s.last_reviewed_at else None,
    } for s in sets]


@router.post("/flashcards", response_model=IDResponse, status_code=201)
async def create_flashcard_set(
    title: str,
    description: str | None = None,
    subject_id: str | None = None,
    current_user: CurrentUser = Depends(student_dep),
    db: AsyncSession = Depends(get_db),
):
    student = await _get_student(current_user, db)

    fs = FlashcardSet(
        school_id=current_user.school_id,
        student_id=student.id,
        title=title,
        description=description,
        subject_id=uuid.UUID(subject_id) if subject_id else None,
    )
    db.add(fs)
    await db.flush()
    return IDResponse(id=str(fs.id))


@router.post("/flashcards/{set_id}/cards", response_model=IDResponse, status_code=201)
async def add_flashcard(
    set_id: str,
    front: str,
    back: str,
    current_user: CurrentUser = Depends(student_dep),
    db: AsyncSession = Depends(get_db),
):
    student = await _get_student(current_user, db)

    # Verify ownership
    fs_result = await db.execute(select(FlashcardSet).where(
        FlashcardSet.id == uuid.UUID(set_id),
        FlashcardSet.student_id == student.id,
    ))
    fs = fs_result.scalar_one_or_none()
    if not fs:
        raise NotFoundError("FlashcardSet", set_id)

    card = Flashcard(
        school_id=current_user.school_id,
        flashcard_set_id=fs.id,
        front=front,
        back=back,
        order=fs.card_count,
    )
    db.add(card)
    fs.card_count += 1
    await db.flush()
    return IDResponse(id=str(card.id))


@router.put("/flashcards/cards/{card_id}/review", response_model=SuccessResponse)
async def review_flashcard(
    card_id: str,
    status: str,  # "known", "hard", "repeat"
    current_user: CurrentUser = Depends(student_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Flashcard).where(
        Flashcard.id == uuid.UUID(card_id),
        Flashcard.school_id == current_user.school_id,
    ))
    card = result.scalar_one_or_none()
    if not card:
        raise NotFoundError("Flashcard", card_id)

    card.status = FlashcardStatus(status if status != "repeat" else "learning")
    card.review_count += 1
    return SuccessResponse(message="Card reviewed")


# ── Profile Customization ──────────────────────────────────────────

@router.put("/profile/customize", response_model=SuccessResponse)
async def customize_profile(
    skin: str | None = None,
    frame: str | None = None,
    aura: str | None = None,
    theme: str | None = None,
    current_user: CurrentUser = Depends(student_dep),
    db: AsyncSession = Depends(get_db),
):
    student = await _get_student(current_user, db)
    if skin is not None:
        student.profile_skin = skin
    if frame is not None:
        student.profile_frame = frame
    if aura is not None:
        student.profile_aura = aura
    if theme is not None:
        student.profile_theme = theme
    return SuccessResponse(message="Profile updated")


# ── Dashboard Layout ───────────────────────────────────────────────

@router.get("/dashboard/layout")
async def get_dashboard_layout(
    current_user: CurrentUser = Depends(student_dep),
    db: AsyncSession = Depends(get_db),
):
    student = await _get_student(current_user, db)

    result = await db.execute(select(DashboardLayout).where(
        DashboardLayout.student_id == student.id,
        DashboardLayout.is_active == True,
    ))
    layout = result.scalar_one_or_none()
    return {"layout": layout.layout if layout else None}


@router.put("/dashboard/layout", response_model=SuccessResponse)
async def save_dashboard_layout(
    layout: dict,
    current_user: CurrentUser = Depends(student_dep),
    db: AsyncSession = Depends(get_db),
):
    student = await _get_student(current_user, db)

    # Upsert
    result = await db.execute(select(DashboardLayout).where(
        DashboardLayout.student_id == student.id,
        DashboardLayout.is_active == True,
    ))
    existing = result.scalar_one_or_none()

    if existing:
        existing.layout = layout
    else:
        db.add(DashboardLayout(
            school_id=current_user.school_id,
            student_id=student.id,
            layout=layout,
        ))

    return SuccessResponse(message="Layout saved")


# ── Homework Submissions ───────────────────────────────────────────

@router.post("/homework/{homework_id}/submit", response_model=IDResponse, status_code=201)
async def submit_homework(
    homework_id: str,
    content: str | None = None,
    current_user: CurrentUser = Depends(student_dep),
    db: AsyncSession = Depends(get_db),
):
    student = await _get_student(current_user, db)

    hw = (await db.execute(select(Homework).where(
        Homework.id == uuid.UUID(homework_id),
        Homework.school_id == current_user.school_id,
    ))).scalar_one_or_none()
    if not hw:
        raise NotFoundError("Homework", homework_id)

    from app.models import SubmissionStatus

    submission = HomeworkSubmission(
        school_id=current_user.school_id,
        homework_id=hw.id,
        student_id=student.id,
        content=content,
        status=SubmissionStatus.SUBMITTED,
        submitted_at=datetime.now(UTC),
    )
    db.add(submission)
    await db.flush()

    # XP for submission
    student.xp += 5
    db.add(XPTransaction(
        school_id=current_user.school_id,
        student_id=student.id,
        amount=5,
        source=XPSource.HOMEWORK,
        source_id=hw.id,
        description=f"Submitted: {hw.title}",
        balance_after=student.xp,
    ))

    return IDResponse(id=str(submission.id))

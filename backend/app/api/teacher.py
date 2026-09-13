"""Teacher API — grades, attendance, homework, seating, random student, notes."""

from __future__ import annotations

import random
import uuid
from datetime import UTC, datetime
from datetime import date as dt_date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.errors import ForbiddenError, NotFoundError, ValidationError
from app.core.security import CurrentUser, require_role
from app.models import (
    Attendance,
    AttendanceStatus,
    AuditAction,
    AuditLog,
    Class,
    Grade,
    Homework,
    HomeworkStatus,
    Student,
    Teacher,
    TeacherAssignment,
    TeacherNote,
    UserRole,
    XPSource,
    XPTransaction,
)
from app.schemas import (
    AttendanceBulk,
    GradeCreate,
    GradeResponse,
    GradeUpdate,
    HomeworkCreate,
    HomeworkResponse,
    IDResponse,
    SuccessResponse,
)

router = APIRouter()

teacher_dep = require_role(UserRole.TEACHER, UserRole.ADMIN)


async def _get_teacher(current_user: CurrentUser, db: AsyncSession) -> Teacher:
    result = await db.execute(select(Teacher).join(Teacher.user).where(
        Teacher.user.has(id=current_user.user_id),
    ))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise ForbiddenError("Teacher profile not found")
    return teacher


async def _verify_class_access(teacher: Teacher, class_id: uuid.UUID, db: AsyncSession) -> None:
    """Verify teacher has assignment for the given class."""
    result = await db.execute(select(TeacherAssignment).where(
        TeacherAssignment.teacher_id == teacher.id,
        TeacherAssignment.class_id == class_id,
        TeacherAssignment.is_active == True,
    ))
    if not result.scalar_one_or_none():
        # Also check if homeroom teacher
        result2 = await db.execute(select(Class).where(
            Class.id == class_id,
            Class.homeroom_teacher_id == teacher.id,
        ))
        if not result2.scalar_one_or_none():
            raise ForbiddenError("No access to this class")


# ── Grades ──────────────────────────────────────────────────────────

@router.post("/grades", response_model=GradeResponse, status_code=201)
async def create_grade(
    body: GradeCreate,
    current_user: CurrentUser = Depends(teacher_dep),
    db: AsyncSession = Depends(get_db),
):
    teacher = await _get_teacher(current_user, db)

    grade = Grade(
        school_id=current_user.school_id,
        student_id=uuid.UUID(body.student_id),
        subject_id=uuid.UUID(body.subject_id),
        teacher_id=teacher.id,
        grading_system_id=uuid.UUID(body.grading_system_id),
        value=body.value,
        max_value=body.max_value,
        comment=body.comment,
        tags=body.tags,
        date=body.date,
        is_correction=body.is_correction,
    )
    if body.lesson_id:
        grade.lesson_id = uuid.UUID(body.lesson_id)
    if body.grade_type_id:
        grade.grade_type_id = uuid.UUID(body.grade_type_id)
    if body.term_id:
        grade.term_id = uuid.UUID(body.term_id)
    if body.original_grade_id:
        grade.original_grade_id = uuid.UUID(body.original_grade_id)

    db.add(grade)
    await db.flush()

    # Audit
    db.add(AuditLog(
        school_id=current_user.school_id, user_id=current_user.user_id,
        action=AuditAction.GRADE_CREATE, entity_type="grade", entity_id=grade.id,
        new_value={"student_id": body.student_id, "value": body.value, "max_value": body.max_value},
    ))

    # XP reward for student
    student_result = await db.execute(select(Student).where(Student.id == uuid.UUID(body.student_id)))
    student = student_result.scalar_one_or_none()
    if student:
        xp_amount = int(body.value / body.max_value * 10) if body.max_value > 0 else 0
        if xp_amount > 0:
            student.xp += xp_amount
            db.add(XPTransaction(
                school_id=current_user.school_id,
                student_id=student.id,
                amount=xp_amount,
                source=XPSource.GRADE,
                source_id=grade.id,
                description=f"Grade: {body.value}/{body.max_value}",
                balance_after=student.xp,
            ))

    return GradeResponse(
        id=str(grade.id), student_id=str(grade.student_id),
        subject_id=str(grade.subject_id), teacher_id=str(grade.teacher_id),
        value=grade.value, max_value=grade.max_value,
        comment=grade.comment, tags=grade.tags, date=grade.date,
        is_correction=grade.is_correction, is_deleted=grade.is_deleted,
        created_at=grade.created_at, updated_at=grade.updated_at,
    )


@router.put("/grades/{grade_id}", response_model=GradeResponse)
async def update_grade(
    grade_id: str,
    body: GradeUpdate,
    current_user: CurrentUser = Depends(teacher_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Grade).where(
        Grade.id == uuid.UUID(grade_id),
        Grade.school_id == current_user.school_id,
        Grade.is_deleted == False,
    ))
    grade = result.scalar_one_or_none()
    if not grade:
        raise NotFoundError("Grade", grade_id)

    old_value = {"value": grade.value, "comment": grade.comment, "tags": grade.tags}

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(grade, field, value)

    db.add(AuditLog(
        school_id=current_user.school_id, user_id=current_user.user_id,
        action=AuditAction.GRADE_UPDATE, entity_type="grade", entity_id=grade.id,
        old_value=old_value,
        new_value=body.model_dump(exclude_unset=True),
    ))

    return GradeResponse(
        id=str(grade.id), student_id=str(grade.student_id),
        subject_id=str(grade.subject_id), teacher_id=str(grade.teacher_id),
        value=grade.value, max_value=grade.max_value,
        comment=grade.comment, tags=grade.tags, date=grade.date,
        is_correction=grade.is_correction, is_deleted=grade.is_deleted,
        created_at=grade.created_at, updated_at=grade.updated_at,
    )


@router.delete("/grades/{grade_id}", response_model=SuccessResponse)
async def delete_grade(
    grade_id: str,
    current_user: CurrentUser = Depends(teacher_dep),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete only — grade history is never physically removed."""
    result = await db.execute(select(Grade).where(
        Grade.id == uuid.UUID(grade_id),
        Grade.school_id == current_user.school_id,
        Grade.is_deleted == False,
    ))
    grade = result.scalar_one_or_none()
    if not grade:
        raise NotFoundError("Grade", grade_id)

    grade.is_deleted = True
    grade.deleted_at = datetime.now(UTC)
    grade.deleted_by = str(current_user.user_id)

    db.add(AuditLog(
        school_id=current_user.school_id, user_id=current_user.user_id,
        action=AuditAction.GRADE_DELETE, entity_type="grade", entity_id=grade.id,
        old_value={"value": grade.value},
    ))

    return SuccessResponse(message="Grade soft-deleted")


@router.post("/grades/{grade_id}/undo", response_model=SuccessResponse)
async def undo_delete_grade(
    grade_id: str,
    current_user: CurrentUser = Depends(teacher_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Grade).where(
        Grade.id == uuid.UUID(grade_id),
        Grade.school_id == current_user.school_id,
        Grade.is_deleted == True,
    ))
    grade = result.scalar_one_or_none()
    if not grade:
        raise NotFoundError("Grade", grade_id)

    grade.is_deleted = False
    grade.deleted_at = None
    grade.deleted_by = None

    return SuccessResponse(message="Grade restored")


# ── Attendance ──────────────────────────────────────────────────────

@router.post("/attendance/bulk", response_model=SuccessResponse)
async def bulk_mark_attendance(
    body: AttendanceBulk,
    current_user: CurrentUser = Depends(teacher_dep),
    db: AsyncSession = Depends(get_db),
):
    for record in body.records:
        attendance = Attendance(
            school_id=current_user.school_id,
            student_id=uuid.UUID(record.student_id),
            subject_id=uuid.UUID(body.subject_id),
            class_id=uuid.UUID(body.class_id),
            lesson_id=uuid.UUID(body.lesson_id) if body.lesson_id else None,
            date=body.date,
            status=AttendanceStatus(record.status),
            note=record.note,
            marked_by=current_user.user_id,
            late_minutes=record.late_minutes,
        )
        db.add(attendance)

        db.add(AuditLog(
            school_id=current_user.school_id, user_id=current_user.user_id,
            action=AuditAction.ATTENDANCE_CREATE, entity_type="attendance",
            new_value={"student_id": record.student_id, "status": record.status},
        ))

    return SuccessResponse(message=f"Attendance marked for {len(body.records)} students")


@router.get("/attendance")
async def get_attendance(
    class_id: str,
    date: str,
    subject_id: str | None = None,
    current_user: CurrentUser = Depends(teacher_dep),
    db: AsyncSession = Depends(get_db),
):
    q = select(Attendance).where(
        Attendance.school_id == current_user.school_id,
        Attendance.class_id == uuid.UUID(class_id),
        Attendance.date == dt_date.fromisoformat(date),
    )
    if subject_id:
        q = q.where(Attendance.subject_id == uuid.UUID(subject_id))

    result = await db.execute(q)
    records = result.scalars().all()

    return [{
        "id": str(a.id), "student_id": str(a.student_id), "date": a.date.isoformat(),
        "status": a.status.value, "note": a.note, "late_minutes": a.late_minutes,
    } for a in records]


# ── Homework ────────────────────────────────────────────────────────

@router.post("/homework", response_model=HomeworkResponse, status_code=201)
async def create_homework(
    body: HomeworkCreate,
    current_user: CurrentUser = Depends(teacher_dep),
    db: AsyncSession = Depends(get_db),
):
    teacher = await _get_teacher(current_user, db)

    hw = Homework(
        school_id=current_user.school_id,
        title=body.title,
        description=body.description,
        class_id=uuid.UUID(body.class_id),
        subject_id=uuid.UUID(body.subject_id),
        teacher_id=teacher.id,
        assigned_date=body.assigned_date,
        due_date=body.due_date,
        max_score=body.max_score,
        allow_late_submission=body.allow_late_submission,
    )
    db.add(hw)
    await db.flush()

    return HomeworkResponse(
        id=str(hw.id), title=hw.title, description=hw.description,
        class_id=str(hw.class_id), subject_id=str(hw.subject_id),
        assigned_date=hw.assigned_date, due_date=hw.due_date,
        max_score=hw.max_score, status=hw.status.value,
        created_at=hw.created_at,
    )


@router.get("/homework", response_model=list[HomeworkResponse])
async def list_homework(
    class_id: str | None = None,
    subject_id: str | None = None,
    current_user: CurrentUser = Depends(teacher_dep),
    db: AsyncSession = Depends(get_db),
):
    q = select(Homework).where(
        Homework.school_id == current_user.school_id,
        Homework.status == HomeworkStatus.ACTIVE,
    )
    if class_id:
        q = q.where(Homework.class_id == uuid.UUID(class_id))
    if subject_id:
        q = q.where(Homework.subject_id == uuid.UUID(subject_id))

    result = await db.execute(q.order_by(Homework.due_date.desc()))
    hws = result.scalars().all()

    return [HomeworkResponse(
        id=str(hw.id), title=hw.title, description=hw.description,
        class_id=str(hw.class_id), subject_id=str(hw.subject_id),
        assigned_date=hw.assigned_date, due_date=hw.due_date,
        max_score=hw.max_score, status=hw.status.value,
        created_at=hw.created_at,
    ) for hw in hws]


# ── Seating Chart ───────────────────────────────────────────────────

@router.get("/classes/{class_id}/seating")
async def get_seating(
    class_id: str,
    current_user: CurrentUser = Depends(teacher_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Class).where(
        Class.id == uuid.UUID(class_id),
        Class.school_id == current_user.school_id,
    ))
    cls = result.scalar_one_or_none()
    if not cls:
        raise NotFoundError("Class", class_id)
    return {"class_id": class_id, "seating_chart": cls.seating_chart or {}}


@router.put("/classes/{class_id}/seating", response_model=SuccessResponse)
async def update_seating(
    class_id: str,
    seating_chart: dict,
    current_user: CurrentUser = Depends(teacher_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Class).where(
        Class.id == uuid.UUID(class_id),
        Class.school_id == current_user.school_id,
    ))
    cls = result.scalar_one_or_none()
    if not cls:
        raise NotFoundError("Class", class_id)
    cls.seating_chart = seating_chart
    return SuccessResponse(message="Seating chart updated")


# ── Random Student ──────────────────────────────────────────────────

@router.get("/classes/{class_id}/random-student")
async def random_student(
    class_id: str,
    mode: str = Query("all", enum=["all", "present", "exclude_recent"]),
    exclude_ids: str | None = None,
    current_user: CurrentUser = Depends(teacher_dep),
    db: AsyncSession = Depends(get_db),
):
    q = select(Student).where(
        Student.class_id == uuid.UUID(class_id),
    )
    result = await db.execute(q)
    students = list(result.scalars().all())

    if not students:
        raise NotFoundError("Students in class")

    if exclude_ids:
        exclude_set = set(exclude_ids.split(","))
        students = [s for s in students if str(s.id) not in exclude_set]

    if not students:
        raise ValidationError("No eligible students remaining")

    chosen = random.choice(students)
    user_result = await db.execute(select(Student).where(Student.id == chosen.id))

    return {"student_id": str(chosen.id), "user_id": str(chosen.user_id)}


# ── Teacher Notes ───────────────────────────────────────────────────

@router.post("/notes", response_model=IDResponse, status_code=201)
async def create_note(
    student_id: str,
    content: str,
    current_user: CurrentUser = Depends(teacher_dep),
    db: AsyncSession = Depends(get_db),
):
    teacher = await _get_teacher(current_user, db)

    note = TeacherNote(
        school_id=current_user.school_id,
        teacher_id=teacher.id,
        student_id=uuid.UUID(student_id),
        content=content,
    )
    db.add(note)
    await db.flush()
    return IDResponse(id=str(note.id))


@router.get("/notes")
async def list_notes(
    student_id: str | None = None,
    current_user: CurrentUser = Depends(teacher_dep),
    db: AsyncSession = Depends(get_db),
):
    teacher = await _get_teacher(current_user, db)

    q = select(TeacherNote).where(
        TeacherNote.school_id == current_user.school_id,
        TeacherNote.teacher_id == teacher.id,  # Strict: only own notes
    )
    if student_id:
        q = q.where(TeacherNote.student_id == uuid.UUID(student_id))

    result = await db.execute(q.order_by(TeacherNote.created_at.desc()))
    notes = result.scalars().all()

    return [{
        "id": str(n.id), "student_id": str(n.student_id), "content": n.content,
        "tags": n.tags, "is_pinned": n.is_pinned, "created_at": n.created_at.isoformat(),
    } for n in notes]


# ── Quick Grading (batch) ──────────────────────────────────────────

@router.post("/grades/batch", response_model=SuccessResponse)
async def batch_create_grades(
    grades: list[GradeCreate],
    current_user: CurrentUser = Depends(teacher_dep),
    db: AsyncSession = Depends(get_db),
):
    teacher = await _get_teacher(current_user, db)

    for body in grades:
        grade = Grade(
            school_id=current_user.school_id,
            student_id=uuid.UUID(body.student_id),
            subject_id=uuid.UUID(body.subject_id),
            teacher_id=teacher.id,
            grading_system_id=uuid.UUID(body.grading_system_id),
            value=body.value,
            max_value=body.max_value,
            comment=body.comment,
            tags=body.tags,
            date=body.date,
        )
        if body.lesson_id:
            grade.lesson_id = uuid.UUID(body.lesson_id)
        if body.grade_type_id:
            grade.grade_type_id = uuid.UUID(body.grade_type_id)
        if body.term_id:
            grade.term_id = uuid.UUID(body.term_id)
        db.add(grade)

        db.add(AuditLog(
            school_id=current_user.school_id, user_id=current_user.user_id,
            action=AuditAction.GRADE_CREATE, entity_type="grade",
            new_value={"student_id": body.student_id, "value": body.value},
        ))

    return SuccessResponse(message=f"Created {len(grades)} grades")

"""Grade & Attendance models with full audit trail and soft-delete."""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin

# ── Grading System ──────────────────────────────────────────────────

class GradingScaleType(str, enum.Enum):
    FIVE_POINT = "five_point"
    TWELVE_POINT = "twelve_point"
    HUNDRED_POINT = "hundred_point"
    LETTER_AF = "letter_af"
    CUSTOM = "custom"


class GradingSystem(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "grading_systems"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    scale_type: Mapped[GradingScaleType] = mapped_column(Enum(GradingScaleType), nullable=False)
    min_value: Mapped[float] = mapped_column(Float, nullable=False)
    max_value: Mapped[float] = mapped_column(Float, nullable=False)
    passing_value: Mapped[float] = mapped_column(Float, nullable=False)
    # For custom scales: [{\"label\": \"A+\", \"value\": 12, \"gpa\": 4.0}, ...]
    custom_scale: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    school: Mapped[School] = relationship("School", back_populates="grading_systems")


class GradeType(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    """Type of grade: homework, classwork, exam, test, project, etc."""

    __tablename__ = "grade_types"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)

    school: Mapped[School] = relationship("School")


class Grade(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, TenantMixin):
    """Individual grade record — never physically deleted, only soft-deleted."""

    __tablename__ = "grades"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False, index=True
    )
    lesson_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=True
    )
    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=False
    )
    grade_type_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grade_types.id"), nullable=True
    )
    grading_system_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grading_systems.id"), nullable=False
    )
    term_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("terms.id"), nullable=True
    )

    value: Mapped[float] = mapped_column(Float, nullable=False)
    max_value: Mapped[float] = mapped_column(Float, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)  # ["classwork", "excellent"]
    date: Mapped[date] = mapped_column(Date, nullable=False)

    # Second Chance tracking
    is_correction: Mapped[bool] = mapped_column(Boolean, default=False)
    original_grade_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grades.id"), nullable=True
    )
    correction_deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    student: Mapped[Student] = relationship("Student", back_populates="grades")
    subject: Mapped[Subject] = relationship("Subject")
    lesson: Mapped[Lesson | None] = relationship("Lesson", back_populates="grades")
    teacher: Mapped[Teacher] = relationship("Teacher")
    grade_type: Mapped[GradeType | None] = relationship("GradeType")
    grading_system: Mapped[GradingSystem] = relationship("GradingSystem")
    original_grade: Mapped[Grade | None] = relationship("Grade", remote_side="Grade.id")


# ── Attendance ──────────────────────────────────────────────────────

class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class Attendance(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "attendances"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True
    )
    lesson_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=True
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False
    )
    class_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[AttendanceStatus] = mapped_column(Enum(AttendanceStatus), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    marked_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    late_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    student: Mapped[Student] = relationship("Student", back_populates="attendances")
    lesson: Mapped[Lesson | None] = relationship("Lesson", back_populates="attendances")
    subject: Mapped[Subject] = relationship("Subject")
    class_: Mapped[Class] = relationship("Class")

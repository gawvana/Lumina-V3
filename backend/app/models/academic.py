"""Academic models: Class, Subject, TeacherAssignment, AcademicYear, Term, Schedule, Lesson."""

from __future__ import annotations

import enum
import uuid
from datetime import date, time

from sqlalchemy import (
    Boolean,
    Date,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Class(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "classes"

    name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "9A"
    grade_level: Mapped[int] = mapped_column(Integer, nullable=False)  # e.g. 9
    section: Mapped[str | None] = mapped_column(String(10), nullable=True)  # e.g. "A"
    academic_year_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("academic_years.id"), nullable=True
    )
    homeroom_teacher_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=True
    )
    max_students: Mapped[int] = mapped_column(Integer, default=35)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    seating_chart: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    school: Mapped[School] = relationship("School", back_populates="classes")
    academic_year: Mapped[AcademicYear | None] = relationship("AcademicYear")
    homeroom_teacher: Mapped[Teacher | None] = relationship("Teacher")
    students: Mapped[list] = relationship("Student", back_populates="student_class")
    schedules: Mapped[list] = relationship("Schedule", back_populates="class_")
    homeworks: Mapped[list] = relationship("Homework", back_populates="class_")


class Subject(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "subjects"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)  # hex color
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    school: Mapped[School] = relationship("School", back_populates="subjects")
    assignments: Mapped[list] = relationship("TeacherAssignment", back_populates="subject")


class TeacherAssignment(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    """Links a teacher to a subject+class for a given academic year."""

    __tablename__ = "teacher_assignments"
    __table_args__ = (
        UniqueConstraint(
            "teacher_id", "subject_id", "class_id", "academic_year_id",
            name="uq_teacher_assignment",
        ),
    )

    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=False
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False
    )
    class_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False
    )
    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("academic_years.id"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    teacher: Mapped[Teacher] = relationship("Teacher", back_populates="assignments")
    subject: Mapped[Subject] = relationship("Subject", back_populates="assignments")
    class_: Mapped[Class] = relationship("Class")
    academic_year: Mapped[AcademicYear] = relationship("AcademicYear")


class AcademicYear(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "academic_years"

    name: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "2025-2026"
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)

    school: Mapped[School] = relationship("School", back_populates="academic_years")
    terms: Mapped[list[Term]] = relationship("Term", back_populates="academic_year")


class Term(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "terms"

    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("academic_years.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "Quarter 1"
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    academic_year: Mapped[AcademicYear] = relationship("AcademicYear", back_populates="terms")


class DayOfWeek(int, enum.Enum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class Schedule(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    """Recurring schedule slot: day of week + time + subject + teacher + class."""

    __tablename__ = "schedules"

    class_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False
    )
    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=False
    )
    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("academic_years.id"), nullable=False
    )
    day_of_week: Mapped[DayOfWeek] = mapped_column(Enum(DayOfWeek), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    room: Mapped[str | None] = mapped_column(String(50), nullable=True)
    slot_number: Mapped[int] = mapped_column(Integer, nullable=False)  # period number
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    class_: Mapped[Class] = relationship("Class", back_populates="schedules")
    subject: Mapped[Subject] = relationship("Subject")
    teacher: Mapped[Teacher] = relationship("Teacher")
    lessons: Mapped[list[Lesson]] = relationship("Lesson", back_populates="schedule")


class Lesson(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    """Concrete lesson instance on a specific date."""

    __tablename__ = "lessons"

    schedule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("schedules.id"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    topic: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_cancelled: Mapped[bool] = mapped_column(Boolean, default=False)
    cancellation_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    schedule: Mapped[Schedule] = relationship("Schedule", back_populates="lessons")
    grades: Mapped[list] = relationship("Grade", back_populates="lesson")
    attendances: Mapped[list] = relationship("Attendance", back_populates="lesson")

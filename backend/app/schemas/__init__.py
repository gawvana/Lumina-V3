"""Pydantic v2 schemas — shared pagination, filtering, and common types."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int
    pages: int


class IDResponse(BaseModel):
    id: str


class SuccessResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"


# ── School Schemas ──────────────────────────────────────────────────

class SchoolCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=50)
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    timezone: str = "Asia/Tashkent"
    language: str = "ru"


class SchoolUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    timezone: str | None = None
    language: str | None = None
    settings: dict[str, Any] | None = None


class SchoolResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    code: str
    address: str | None
    phone: str | None
    email: str | None
    timezone: str
    language: str
    is_active: bool
    logo_url: str | None
    created_at: datetime


# ── Class Schemas ───────────────────────────────────────────────────

class ClassCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    grade_level: int = Field(ge=1, le=12)
    section: str | None = None
    academic_year_id: str | None = None
    homeroom_teacher_id: str | None = None
    max_students: int = 35


class ClassUpdate(BaseModel):
    name: str | None = None
    grade_level: int | None = None
    section: str | None = None
    homeroom_teacher_id: str | None = None
    max_students: int | None = None


class ClassResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    grade_level: int
    section: str | None
    max_students: int
    is_active: bool
    student_count: int = 0
    created_at: datetime


# ── Subject Schemas ─────────────────────────────────────────────────

class SubjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    code: str = Field(min_length=1, max_length=20)
    description: str | None = None
    color: str | None = None
    icon: str | None = None


class SubjectUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    description: str | None = None
    color: str | None = None
    icon: str | None = None


class SubjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    code: str
    description: str | None
    color: str | None
    icon: str | None
    is_active: bool
    created_at: datetime


# ── User Schemas ────────────────────────────────────────────────────

class UserCreate(BaseModel):
    telegram_id: int
    first_name: str = Field(min_length=1, max_length=150)
    last_name: str = Field(min_length=1, max_length=150)
    middle_name: str | None = None
    role: str
    phone: str | None = None
    email: str | None = None
    class_id: str | None = None  # for students


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    telegram_id: int
    role: str
    first_name: str
    last_name: str
    middle_name: str | None
    username: str | None
    phone: str | None
    email: str | None
    avatar_url: str | None
    language: str
    is_active: bool
    last_login: datetime | None
    created_at: datetime


# ── Grade Schemas ───────────────────────────────────────────────────

class GradeCreate(BaseModel):
    student_id: str
    subject_id: str
    lesson_id: str | None = None
    grade_type_id: str | None = None
    grading_system_id: str
    term_id: str | None = None
    value: float
    max_value: float
    comment: str | None = None
    tags: list[str] | None = None
    date: date
    is_correction: bool = False
    original_grade_id: str | None = None


class GradeUpdate(BaseModel):
    value: float | None = None
    comment: str | None = None
    tags: list[str] | None = None


class GradeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    student_id: str
    subject_id: str
    teacher_id: str
    value: float
    max_value: float
    comment: str | None
    tags: list[str] | None
    date: date
    is_correction: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


# ── Attendance Schemas ──────────────────────────────────────────────

class AttendanceMark(BaseModel):
    student_id: str
    status: str  # AttendanceStatus value
    note: str | None = None
    late_minutes: int | None = None


class AttendanceBulk(BaseModel):
    class_id: str
    subject_id: str
    lesson_id: str | None = None
    date: date
    records: list[AttendanceMark]


class AttendanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    student_id: str
    subject_id: str
    date: date
    status: str
    note: str | None
    late_minutes: int | None
    created_at: datetime


# ── Homework Schemas ────────────────────────────────────────────────

class HomeworkCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    description: str | None = None
    class_id: str
    subject_id: str
    assigned_date: date
    due_date: date
    max_score: float | None = None
    allow_late_submission: bool = False


class HomeworkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str | None
    class_id: str
    subject_id: str
    assigned_date: date
    due_date: date
    max_score: float | None
    status: str
    submission_count: int = 0
    created_at: datetime


# ── Invite Schemas ──────────────────────────────────────────────────

class InviteCreate(BaseModel):
    role: str
    class_id: str | None = None
    max_uses: int = Field(default=1, ge=1)
    expires_in_hours: int = Field(default=72, ge=1, le=720)


class InviteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    token: str
    role: str
    class_id: str | None
    max_uses: int
    use_count: int
    is_revoked: bool
    expires_at: datetime
    created_at: datetime


# ── Notification Schemas ────────────────────────────────────────────

class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str
    title: str
    body: str
    data: dict[str, Any] | None
    is_read: bool
    created_at: datetime

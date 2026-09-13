"""Core models: School, User, Admin, Teacher, Student, Parent, StudentParent."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"


class School(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "schools"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Tashkent")
    language: Mapped[str] = mapped_column(String(5), default="ru")
    settings: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    users: Mapped[list[User]] = relationship("User", back_populates="school")
    classes: Mapped[list] = relationship("Class", back_populates="school")
    subjects: Mapped[list] = relationship("Subject", back_populates="school")
    academic_years: Mapped[list] = relationship("AcademicYear", back_populates="school")
    grading_systems: Mapped[list] = relationship("GradingSystem", back_populates="school")
    invites: Mapped[list] = relationship("Invite", back_populates="school")
    announcements: Mapped[list] = relationship("SchoolAnnouncement", back_populates="school")
    feature_flags: Mapped[list] = relationship("FeatureFlag", back_populates="school")


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    school_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True
    )
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(150), nullable=False)
    last_name: Mapped[str] = mapped_column(String(150), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    language: Mapped[str] = mapped_column(String(5), default="ru")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    settings: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    school: Mapped[School] = relationship("School", back_populates="users")
    admin_profile: Mapped[Admin | None] = relationship("Admin", back_populates="user", uselist=False)
    teacher_profile: Mapped[Teacher | None] = relationship(
        "Teacher", back_populates="user", uselist=False
    )
    student_profile: Mapped[Student | None] = relationship(
        "Student", back_populates="user", uselist=False
    )
    parent_profile: Mapped[Parent | None] = relationship(
        "Parent", back_populates="user", uselist=False
    )
    notifications: Mapped[list] = relationship("Notification", back_populates="user")
    notification_preferences: Mapped[list] = relationship(
        "NotificationPreference", back_populates="user"
    )
    audit_logs: Mapped[list] = relationship("AuditLog", back_populates="user")

    @property
    def full_name(self) -> str:
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)


class Admin(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "admins"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    is_super: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped[User] = relationship("User", back_populates="admin_profile")


class Teacher(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "teachers"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    specialization: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user: Mapped[User] = relationship("User", back_populates="teacher_profile")
    assignments: Mapped[list] = relationship("TeacherAssignment", back_populates="teacher")
    notes: Mapped[list] = relationship("TeacherNote", back_populates="teacher")


class Student(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "students"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    class_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("classes.id"), nullable=True, index=True
    )
    student_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    date_of_birth: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    streak_last_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    active_title_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("titles.id"), nullable=True
    )
    profile_skin: Mapped[str | None] = mapped_column(String(100), nullable=True)
    profile_frame: Mapped[str | None] = mapped_column(String(100), nullable=True)
    profile_aura: Mapped[str | None] = mapped_column(String(100), nullable=True)
    profile_theme: Mapped[str | None] = mapped_column(String(100), nullable=True)

    user: Mapped[User] = relationship("User", back_populates="student_profile")
    student_class: Mapped[Class | None] = relationship("Class", back_populates="students")
    active_title: Mapped[Title | None] = relationship("Title", foreign_keys=[active_title_id])
    grades: Mapped[list] = relationship("Grade", back_populates="student")
    attendances: Mapped[list] = relationship("Attendance", back_populates="student")
    homework_submissions: Mapped[list] = relationship("HomeworkSubmission", back_populates="student")
    achievements: Mapped[list] = relationship("UserAchievement", back_populates="student")
    xp_transactions: Mapped[list] = relationship("XPTransaction", back_populates="student")
    vibes: Mapped[list] = relationship("StudentVibe", back_populates="student")
    skills: Mapped[list] = relationship("StudentSkill", back_populates="student")
    flashcard_sets: Mapped[list] = relationship("FlashcardSet", back_populates="student")
    files: Mapped[list] = relationship("FileAsset", back_populates="student")
    dashboard_layouts: Mapped[list] = relationship("DashboardLayout", back_populates="student")
    parent_links: Mapped[list[StudentParent]] = relationship(
        "StudentParent", back_populates="student"
    )


class Parent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "parents"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )

    user: Mapped[User] = relationship("User", back_populates="parent_profile")
    children: Mapped[list[StudentParent]] = relationship("StudentParent", back_populates="parent")
    consents: Mapped[list] = relationship("Consent", back_populates="parent")


class StudentParent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Many-to-many: a parent can have multiple children, a student can have multiple parents."""

    __tablename__ = "student_parents"
    __table_args__ = (
        UniqueConstraint("student_id", "parent_id", name="uq_student_parent"),
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id"), nullable=False
    )
    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("parents.id"), nullable=False
    )
    relationship_type: Mapped[str] = mapped_column(
        String(50), default="parent"
    )  # parent, guardian, etc.
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    student: Mapped[Student] = relationship("Student", back_populates="parent_links")
    parent: Mapped[Parent] = relationship("Parent", back_populates="children")

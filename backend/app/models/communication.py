"""Communication models: Notification, NotificationPreference, TeacherNote, StudentVibe, SchoolAnnouncement."""

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
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin


class NotificationType(str, enum.Enum):
    GRADE = "grade"
    HOMEWORK = "homework"
    ATTENDANCE = "attendance"
    ACHIEVEMENT = "achievement"
    ANNOUNCEMENT = "announcement"
    SUMMARY = "summary"
    SYSTEM = "system"


class Notification(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_via_bot: Mapped[bool] = mapped_column(Boolean, default=False)
    bot_message_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user: Mapped[User] = relationship("User", back_populates="notifications")


class NotificationPreference(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "notification_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    notification_type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType), nullable=False
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    bot_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    digest_only: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped[User] = relationship("User", back_populates="notification_preferences")


class TeacherNote(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    """Private teacher notes — strictly authorized, only the authoring teacher can see."""

    __tablename__ = "teacher_notes"

    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=False, index=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)

    teacher: Mapped[Teacher] = relationship("Teacher", back_populates="notes")
    student: Mapped[Student] = relationship("Student")


class VibeType(str, enum.Enum):
    HAPPY = "happy"
    NEUTRAL = "neutral"
    SAD = "sad"
    STRESSED = "stressed"
    EXCITED = "excited"
    TIRED = "tired"
    FOCUSED = "focused"
    CONFUSED = "confused"


class StudentVibe(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    """Student mood/vibe tracking — private by default."""

    __tablename__ = "student_vibes"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True
    )
    vibe: Mapped[VibeType] = mapped_column(Enum(VibeType), nullable=False)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_private: Mapped[bool] = mapped_column(Boolean, default=True)

    student: Mapped[Student] = relationship("Student", back_populates="vibes")


class SchoolAnnouncement(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "school_announcements"

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    target_roles: Mapped[list] = mapped_column(JSON, nullable=False)  # ["student", "parent"]
    target_classes: Mapped[list | None] = mapped_column(JSON, nullable=True)  # class IDs
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attachments: Mapped[list | None] = mapped_column(JSON, nullable=True)

    school: Mapped[School] = relationship("School", back_populates="announcements")
    author: Mapped[User] = relationship("User")

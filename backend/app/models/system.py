"""System models: Invite, AuditLog, FlashcardSet, Flashcard, FileAsset, FeatureFlag, DashboardLayout, Consent."""

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

# ── Invites ─────────────────────────────────────────────────────────

class Invite(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "invites"

    token: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # UserRole value
    class_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("classes.id"), nullable=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    max_uses: Mapped[int] = mapped_column(Integer, default=1)
    use_count: Mapped[int] = mapped_column(Integer, default=0)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    school: Mapped[School] = relationship("School", back_populates="invites")
    creator: Mapped[User] = relationship("User", foreign_keys=[created_by])


# ── Audit Log ───────────────────────────────────────────────────────

class AuditAction(str, enum.Enum):
    GRADE_CREATE = "grade_create"
    GRADE_UPDATE = "grade_update"
    GRADE_DELETE = "grade_delete"
    ATTENDANCE_CREATE = "attendance_create"
    ATTENDANCE_UPDATE = "attendance_update"
    INVITE_CREATE = "invite_create"
    INVITE_USE = "invite_use"
    INVITE_REVOKE = "invite_revoke"
    ROLE_CHANGE = "role_change"
    USER_CREATE = "user_create"
    USER_DELETE = "user_delete"
    SCHOOL_CREATE = "school_create"
    SCHOOL_UPDATE = "school_update"
    CLASS_CREATE = "class_create"
    CLASS_DELETE = "class_delete"
    SETTINGS_UPDATE = "settings_update"


class AuditLog(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "audit_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "grade", "invite", etc.
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    old_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped[User] = relationship("User", back_populates="audit_logs")


# ── Flashcards ──────────────────────────────────────────────────────

class FlashcardSet(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "flashcard_sets"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True
    )
    subject_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    card_count: Mapped[int] = mapped_column(Integer, default=0)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    student: Mapped[Student] = relationship("Student", back_populates="flashcard_sets")
    cards: Mapped[list[Flashcard]] = relationship("Flashcard", back_populates="flashcard_set")


class FlashcardStatus(str, enum.Enum):
    NEW = "new"
    LEARNING = "learning"
    KNOWN = "known"
    HARD = "hard"


class Flashcard(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "flashcards"

    flashcard_set_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("flashcard_sets.id"), nullable=False, index=True
    )
    front: Mapped[str] = mapped_column(Text, nullable=False)
    back: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[FlashcardStatus] = mapped_column(
        Enum(FlashcardStatus), default=FlashcardStatus.NEW
    )
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    next_review_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    order: Mapped[int] = mapped_column(Integer, default=0)

    flashcard_set: Mapped[FlashcardSet] = relationship(
        "FlashcardSet", back_populates="cards"
    )


# ── File Assets (Digital Backpack) ──────────────────────────────────

class FileAsset(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "file_assets"

    student_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id"), nullable=True, index=True
    )
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    folder: Mapped[str] = mapped_column(String(200), default="/")
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)

    student: Mapped[Student | None] = relationship("Student", back_populates="files")


# ── Feature Flags ───────────────────────────────────────────────────

class FeatureFlag(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "feature_flags"

    key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    school: Mapped[School] = relationship("School", back_populates="feature_flags")


# ── Dashboard Layout ────────────────────────────────────────────────

class DashboardLayout(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "dashboard_layouts"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True
    )
    layout: Mapped[dict] = mapped_column(JSON, nullable=False)  # widget positions, sizes, order
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    student: Mapped[Student] = relationship("Student", back_populates="dashboard_layouts")


# ── Consent ─────────────────────────────────────────────────────────

class ConsentType(str, enum.Enum):
    DATA_PROCESSING = "data_processing"
    PHOTO_VIDEO = "photo_video"
    NOTIFICATIONS = "notifications"
    AI_FEATURES = "ai_features"
    CUSTOM = "custom"


class Consent(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "consents"

    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("parents.id"), nullable=False, index=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id"), nullable=False
    )
    consent_type: Mapped[ConsentType] = mapped_column(Enum(ConsentType), nullable=False)
    granted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    granted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)

    parent: Mapped[Parent] = relationship("Parent", back_populates="consents")

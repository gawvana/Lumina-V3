"""Gamification models: Achievement, UserAchievement, Title, XPTransaction, Skill, StudentSkill."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin


class AchievementCategory(str, enum.Enum):
    ACADEMIC = "academic"
    ATTENDANCE = "attendance"
    SOCIAL = "social"
    STREAK = "streak"
    SPECIAL = "special"


class Achievement(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "achievements"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category: Mapped[AchievementCategory] = mapped_column(
        Enum(AchievementCategory), nullable=False
    )
    xp_reward: Mapped[int] = mapped_column(Integer, default=0)
    # Trigger condition as JSON: {"type": "grade_count", "threshold": 10, "min_value": 4}
    trigger_condition: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    rarity: Mapped[str] = mapped_column(String(20), default="common")  # common/rare/epic/legendary
    order: Mapped[int] = mapped_column(Integer, default=0)

    school: Mapped[School] = relationship("School")


class UserAchievement(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "user_achievements"
    __table_args__ = (
        UniqueConstraint("student_id", "achievement_id", name="uq_user_achievement"),
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True
    )
    achievement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("achievements.id"), nullable=False
    )
    earned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notified: Mapped[bool] = mapped_column(Boolean, default=False)

    student: Mapped[Student] = relationship("Student", back_populates="achievements")
    achievement: Mapped[Achievement] = relationship("Achievement")


class Title(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "titles"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    min_level: Mapped[int] = mapped_column(Integer, default=1)
    required_achievement_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("achievements.id"), nullable=True
    )
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    rarity: Mapped[str] = mapped_column(String(20), default="common")

    school: Mapped[School] = relationship("School")


class XPSource(str, enum.Enum):
    GRADE = "grade"
    ATTENDANCE = "attendance"
    HOMEWORK = "homework"
    STREAK = "streak"
    ACHIEVEMENT = "achievement"
    BONUS = "bonus"
    CORRECTION = "correction"  # negative for corrections


class XPTransaction(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    """Immutable XP ledger — never edit, only append."""

    __tablename__ = "xp_transactions"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # can be negative
    source: Mapped[XPSource] = mapped_column(Enum(XPSource), nullable=False)
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )  # FK to grade/homework/etc.
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)

    student: Mapped[Student] = relationship("Student", back_populates="xp_transactions")


class SkillCategory(str, enum.Enum):
    MATH = "math"
    SCIENCE = "science"
    LANGUAGE = "language"
    SOCIAL = "social"
    CREATIVE = "creative"
    PHYSICAL = "physical"
    TECHNOLOGY = "technology"


class Skill(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "skills"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[SkillCategory] = mapped_column(Enum(SkillCategory), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    max_level: Mapped[int] = mapped_column(Integer, default=5)
    # Prerequisites as JSON array of skill IDs
    prerequisites: Mapped[list | None] = mapped_column(JSON, nullable=True)
    subject_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=True
    )
    order: Mapped[int] = mapped_column(Integer, default=0)
    # Position in skill tree for UI
    tree_x: Mapped[int] = mapped_column(Integer, default=0)
    tree_y: Mapped[int] = mapped_column(Integer, default=0)

    school: Mapped[School] = relationship("School")


class StudentSkill(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "student_skills"
    __table_args__ = (
        UniqueConstraint("student_id", "skill_id", name="uq_student_skill"),
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False
    )
    current_level: Mapped[int] = mapped_column(Integer, default=0)
    progress: Mapped[float] = mapped_column(Float, default=0.0)  # 0.0 to 1.0 within current level
    mastered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    student: Mapped[Student] = relationship("Student", back_populates="skills")
    skill: Mapped[Skill] = relationship("Skill")

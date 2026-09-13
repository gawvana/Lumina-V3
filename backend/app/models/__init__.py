"""Lumina V3 — All models re-exported from this package."""

from app.models.academic import (  # noqa: F401
    AcademicYear,
    Class,
    DayOfWeek,
    Lesson,
    Schedule,
    Subject,
    TeacherAssignment,
    Term,
)
from app.models.base import Base  # noqa: F401
from app.models.communication import (  # noqa: F401
    Notification,
    NotificationPreference,
    NotificationType,
    SchoolAnnouncement,
    StudentVibe,
    TeacherNote,
    VibeType,
)
from app.models.core import (  # noqa: F401
    Admin,
    Parent,
    School,
    Student,
    StudentParent,
    Teacher,
    User,
    UserRole,
)
from app.models.gamification import (  # noqa: F401
    Achievement,
    AchievementCategory,
    Skill,
    SkillCategory,
    StudentSkill,
    Title,
    UserAchievement,
    XPSource,
    XPTransaction,
)
from app.models.grades import (  # noqa: F401
    Attendance,
    AttendanceStatus,
    Grade,
    GradeType,
    GradingScaleType,
    GradingSystem,
)
from app.models.homework import (  # noqa: F401
    Homework,
    HomeworkStatus,
    HomeworkSubmission,
    SubmissionStatus,
)
from app.models.system import (  # noqa: F401
    AuditAction,
    AuditLog,
    Consent,
    ConsentType,
    DashboardLayout,
    FeatureFlag,
    FileAsset,
    Flashcard,
    FlashcardSet,
    FlashcardStatus,
    Invite,
)

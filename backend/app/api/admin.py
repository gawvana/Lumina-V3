"""Admin API — full CRUD for schools, classes, subjects, users, invites, settings."""

from __future__ import annotations

import secrets
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.errors import ConflictError, NotFoundError
from app.core.security import CurrentUser, require_role
from app.models import (
    AcademicYear,
    Admin,
    AuditAction,
    AuditLog,
    Class,
    FeatureFlag,
    GradingScaleType,
    GradingSystem,
    Invite,
    Parent,
    School,
    SchoolAnnouncement,
    Student,
    Subject,
    Teacher,
    User,
    UserRole,
)
from app.schemas import (
    ClassCreate,
    ClassResponse,
    ClassUpdate,
    IDResponse,
    InviteCreate,
    InviteResponse,
    PaginatedResponse,
    SchoolResponse,
    SchoolUpdate,
    SubjectCreate,
    SubjectResponse,
    SuccessResponse,
    UserCreate,
    UserResponse,
)

router = APIRouter()

admin_dep = require_role(UserRole.ADMIN)


# ── Tenant filter helper ───────────────────────────────────────────

def _tenant_filter(model, current_user: CurrentUser):
    """Return SQLAlchemy filter for multi-tenant isolation."""
    if hasattr(model, "school_id"):
        return model.school_id == current_user.school_id
    return True


# ── School ──────────────────────────────────────────────────────────

@router.get("/school", response_model=SchoolResponse)
async def get_school(
    current_user: CurrentUser = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(School).where(School.id == current_user.school_id))
    school = result.scalar_one_or_none()
    if not school:
        raise NotFoundError("School")
    return SchoolResponse(
        id=str(school.id), name=school.name, code=school.code,
        address=school.address, phone=school.phone, email=school.email,
        timezone=school.timezone, language=school.language,
        is_active=school.is_active, logo_url=school.logo_url,
        created_at=school.created_at,
    )


@router.put("/school", response_model=SchoolResponse)
async def update_school(
    body: SchoolUpdate,
    current_user: CurrentUser = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(School).where(School.id == current_user.school_id))
    school = result.scalar_one_or_none()
    if not school:
        raise NotFoundError("School")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(school, field, value)

    # Audit
    db.add(AuditLog(
        school_id=current_user.school_id, user_id=current_user.user_id,
        action=AuditAction.SCHOOL_UPDATE, entity_type="school",
        entity_id=school.id, new_value=body.model_dump(exclude_unset=True),
    ))

    return SchoolResponse(
        id=str(school.id), name=school.name, code=school.code,
        address=school.address, phone=school.phone, email=school.email,
        timezone=school.timezone, language=school.language,
        is_active=school.is_active, logo_url=school.logo_url,
        created_at=school.created_at,
    )


# ── Classes ─────────────────────────────────────────────────────────

@router.get("/classes", response_model=PaginatedResponse[ClassResponse])
async def list_classes(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    base_q = select(Class).where(
        Class.school_id == current_user.school_id, Class.is_active == True
    )
    total_q = select(func.count()).select_from(base_q.subquery())
    total = (await db.execute(total_q)).scalar() or 0

    items_q = base_q.order_by(Class.grade_level, Class.name).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(items_q)
    classes = result.scalars().all()

    return PaginatedResponse(
        items=[ClassResponse(
            id=str(c.id), name=c.name, grade_level=c.grade_level,
            section=c.section, max_students=c.max_students,
            is_active=c.is_active, created_at=c.created_at,
        ) for c in classes],
        total=total, page=page, per_page=per_page,
        pages=(total + per_page - 1) // per_page if per_page else 0,
    )


@router.post("/classes", response_model=IDResponse, status_code=201)
async def create_class(
    body: ClassCreate,
    current_user: CurrentUser = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    new_class = Class(
        school_id=current_user.school_id,
        name=body.name,
        grade_level=body.grade_level,
        section=body.section,
        max_students=body.max_students,
    )
    if body.academic_year_id:
        new_class.academic_year_id = uuid.UUID(body.academic_year_id)
    if body.homeroom_teacher_id:
        new_class.homeroom_teacher_id = uuid.UUID(body.homeroom_teacher_id)

    db.add(new_class)
    await db.flush()

    db.add(AuditLog(
        school_id=current_user.school_id, user_id=current_user.user_id,
        action=AuditAction.CLASS_CREATE, entity_type="class", entity_id=new_class.id,
        new_value=body.model_dump(),
    ))

    return IDResponse(id=str(new_class.id))


@router.put("/classes/{class_id}", response_model=SuccessResponse)
async def update_class(
    class_id: str,
    body: ClassUpdate,
    current_user: CurrentUser = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Class).where(
        Class.id == uuid.UUID(class_id),
        Class.school_id == current_user.school_id,
    ))
    cls = result.scalar_one_or_none()
    if not cls:
        raise NotFoundError("Class", class_id)

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(cls, field, value)

    return SuccessResponse()


@router.delete("/classes/{class_id}", response_model=SuccessResponse)
async def delete_class(
    class_id: str,
    current_user: CurrentUser = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Class).where(
        Class.id == uuid.UUID(class_id),
        Class.school_id == current_user.school_id,
    ))
    cls = result.scalar_one_or_none()
    if not cls:
        raise NotFoundError("Class", class_id)

    cls.is_active = False

    db.add(AuditLog(
        school_id=current_user.school_id, user_id=current_user.user_id,
        action=AuditAction.CLASS_DELETE, entity_type="class", entity_id=cls.id,
    ))

    return SuccessResponse(message="Class deactivated")


# ── Subjects ────────────────────────────────────────────────────────

@router.get("/subjects", response_model=PaginatedResponse[SubjectResponse])
async def list_subjects(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    base_q = select(Subject).where(
        Subject.school_id == current_user.school_id, Subject.is_active == True
    )
    total = (await db.execute(select(func.count()).select_from(base_q.subquery()))).scalar() or 0
    items = (await db.execute(
        base_q.order_by(Subject.name).offset((page - 1) * per_page).limit(per_page)
    )).scalars().all()

    return PaginatedResponse(
        items=[SubjectResponse(
            id=str(s.id), name=s.name, code=s.code, description=s.description,
            color=s.color, icon=s.icon, is_active=s.is_active, created_at=s.created_at,
        ) for s in items],
        total=total, page=page, per_page=per_page,
        pages=(total + per_page - 1) // per_page if per_page else 0,
    )


@router.post("/subjects", response_model=IDResponse, status_code=201)
async def create_subject(
    body: SubjectCreate,
    current_user: CurrentUser = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    subj = Subject(school_id=current_user.school_id, **body.model_dump())
    db.add(subj)
    await db.flush()
    return IDResponse(id=str(subj.id))


# ── Users (Teachers, Students, Parents) ────────────────────────────

@router.get("/users", response_model=PaginatedResponse[UserResponse])
async def list_users(
    role: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = None,
    current_user: CurrentUser = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    base_q = select(User).where(
        User.school_id == current_user.school_id,
        User.is_deleted == False,
    )
    if role:
        base_q = base_q.where(User.role == UserRole(role))
    if search:
        search_filter = f"%{search}%"
        base_q = base_q.where(
            (User.first_name.ilike(search_filter)) |
            (User.last_name.ilike(search_filter))
        )

    total = (await db.execute(select(func.count()).select_from(base_q.subquery()))).scalar() or 0
    items = (await db.execute(
        base_q.order_by(User.last_name, User.first_name)
        .offset((page - 1) * per_page).limit(per_page)
    )).scalars().all()

    return PaginatedResponse(
        items=[UserResponse(
            id=str(u.id), telegram_id=u.telegram_id, role=u.role.value,
            first_name=u.first_name, last_name=u.last_name, middle_name=u.middle_name,
            username=u.username, phone=u.phone, email=u.email,
            avatar_url=u.avatar_url, language=u.language, is_active=u.is_active,
            last_login=u.last_login, created_at=u.created_at,
        ) for u in items],
        total=total, page=page, per_page=per_page,
        pages=(total + per_page - 1) // per_page if per_page else 0,
    )


@router.post("/users", response_model=IDResponse, status_code=201)
async def create_user(
    body: UserCreate,
    current_user: CurrentUser = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    # Check for duplicate telegram_id
    existing = await db.execute(select(User).where(User.telegram_id == body.telegram_id))
    if existing.scalar_one_or_none():
        raise ConflictError(f"User with telegram_id {body.telegram_id} already exists")

    user = User(
        school_id=current_user.school_id,
        telegram_id=body.telegram_id,
        role=UserRole(body.role),
        first_name=body.first_name,
        last_name=body.last_name,
        middle_name=body.middle_name,
        phone=body.phone,
        email=body.email,
    )
    db.add(user)
    await db.flush()

    # Create role-specific profile
    if user.role == UserRole.ADMIN:
        db.add(Admin(user_id=user.id))
    elif user.role == UserRole.TEACHER:
        db.add(Teacher(user_id=user.id))
    elif user.role == UserRole.STUDENT:
        student = Student(user_id=user.id)
        if body.class_id:
            student.class_id = uuid.UUID(body.class_id)
        db.add(student)
    elif user.role == UserRole.PARENT:
        db.add(Parent(user_id=user.id))

    db.add(AuditLog(
        school_id=current_user.school_id, user_id=current_user.user_id,
        action=AuditAction.USER_CREATE, entity_type="user", entity_id=user.id,
        new_value={"role": body.role, "telegram_id": body.telegram_id},
    ))

    return IDResponse(id=str(user.id))


# ── Invites ─────────────────────────────────────────────────────────

@router.get("/invites", response_model=list[InviteResponse])
async def list_invites(
    current_user: CurrentUser = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Invite).where(
        Invite.school_id == current_user.school_id,
    ).order_by(Invite.created_at.desc()))
    invites = result.scalars().all()

    return [InviteResponse(
        id=str(i.id), token=i.token, role=i.role, class_id=str(i.class_id) if i.class_id else None,
        max_uses=i.max_uses, use_count=i.use_count, is_revoked=i.is_revoked,
        expires_at=i.expires_at, created_at=i.created_at,
    ) for i in invites]


@router.post("/invites", response_model=InviteResponse, status_code=201)
async def create_invite(
    body: InviteCreate,
    current_user: CurrentUser = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    token = secrets.token_urlsafe(48)
    invite = Invite(
        school_id=current_user.school_id,
        token=token,
        role=body.role,
        class_id=uuid.UUID(body.class_id) if body.class_id else None,
        created_by=current_user.user_id,
        expires_at=datetime.now(UTC) + timedelta(hours=body.expires_in_hours),
        max_uses=body.max_uses,
    )
    db.add(invite)
    await db.flush()

    db.add(AuditLog(
        school_id=current_user.school_id, user_id=current_user.user_id,
        action=AuditAction.INVITE_CREATE, entity_type="invite", entity_id=invite.id,
        new_value={"role": body.role, "max_uses": body.max_uses},
    ))

    return InviteResponse(
        id=str(invite.id), token=invite.token, role=invite.role,
        class_id=str(invite.class_id) if invite.class_id else None,
        max_uses=invite.max_uses, use_count=invite.use_count,
        is_revoked=invite.is_revoked, expires_at=invite.expires_at,
        created_at=invite.created_at,
    )


@router.post("/invites/{invite_id}/revoke", response_model=SuccessResponse)
async def revoke_invite(
    invite_id: str,
    current_user: CurrentUser = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Invite).where(
        Invite.id == uuid.UUID(invite_id),
        Invite.school_id == current_user.school_id,
    ))
    invite = result.scalar_one_or_none()
    if not invite:
        raise NotFoundError("Invite", invite_id)

    invite.is_revoked = True
    invite.revoked_at = datetime.now(UTC)
    invite.revoked_by = current_user.user_id

    db.add(AuditLog(
        school_id=current_user.school_id, user_id=current_user.user_id,
        action=AuditAction.INVITE_REVOKE, entity_type="invite", entity_id=invite.id,
    ))

    return SuccessResponse(message="Invite revoked")


# ── Feature Flags ───────────────────────────────────────────────────

@router.get("/feature-flags")
async def list_feature_flags(
    current_user: CurrentUser = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(FeatureFlag).where(
        FeatureFlag.school_id == current_user.school_id,
    ))
    flags = result.scalars().all()
    return [{"id": str(f.id), "key": f.key, "enabled": f.enabled, "description": f.description} for f in flags]


@router.put("/feature-flags/{flag_id}")
async def toggle_feature_flag(
    flag_id: str,
    enabled: bool = Query(...),
    current_user: CurrentUser = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(FeatureFlag).where(
        FeatureFlag.id == uuid.UUID(flag_id),
        FeatureFlag.school_id == current_user.school_id,
    ))
    flag = result.scalar_one_or_none()
    if not flag:
        raise NotFoundError("FeatureFlag", flag_id)

    flag.enabled = enabled
    return {"success": True}


# ── Audit Logs ──────────────────────────────────────────────────────

@router.get("/audit-logs")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    action: str | None = None,
    current_user: CurrentUser = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    base_q = select(AuditLog).where(AuditLog.school_id == current_user.school_id)
    if action:
        base_q = base_q.where(AuditLog.action == AuditAction(action))

    total = (await db.execute(select(func.count()).select_from(base_q.subquery()))).scalar() or 0
    items = (await db.execute(
        base_q.order_by(AuditLog.created_at.desc())
        .offset((page - 1) * per_page).limit(per_page)
    )).scalars().all()

    return {
        "items": [{
            "id": str(a.id), "user_id": str(a.user_id), "action": a.action.value,
            "entity_type": a.entity_type, "entity_id": str(a.entity_id) if a.entity_id else None,
            "old_value": a.old_value, "new_value": a.new_value,
            "created_at": a.created_at.isoformat(),
        } for a in items],
        "total": total, "page": page, "per_page": per_page,
    }


# ── Academic Years & Terms ──────────────────────────────────────────

@router.get("/academic-years")
async def list_academic_years(
    current_user: CurrentUser = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AcademicYear).where(
        AcademicYear.school_id == current_user.school_id,
    ).order_by(AcademicYear.start_date.desc()))
    years = result.scalars().all()
    return [{
        "id": str(y.id), "name": y.name, "start_date": y.start_date.isoformat(),
        "end_date": y.end_date.isoformat(), "is_current": y.is_current,
    } for y in years]


@router.post("/academic-years", response_model=IDResponse, status_code=201)
async def create_academic_year(
    name: str,
    start_date: str,
    end_date: str,
    current_user: CurrentUser = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    from datetime import date as dt_date

    year = AcademicYear(
        school_id=current_user.school_id,
        name=name,
        start_date=dt_date.fromisoformat(start_date),
        end_date=dt_date.fromisoformat(end_date),
    )
    db.add(year)
    await db.flush()
    return IDResponse(id=str(year.id))


# ── Grading Systems ────────────────────────────────────────────────

@router.get("/grading-systems")
async def list_grading_systems(
    current_user: CurrentUser = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(GradingSystem).where(
        GradingSystem.school_id == current_user.school_id,
    ))
    systems = result.scalars().all()
    return [{
        "id": str(gs.id), "name": gs.name, "scale_type": gs.scale_type.value,
        "min_value": gs.min_value, "max_value": gs.max_value,
        "passing_value": gs.passing_value, "is_default": gs.is_default,
        "custom_scale": gs.custom_scale,
    } for gs in systems]


@router.post("/grading-systems", response_model=IDResponse, status_code=201)
async def create_grading_system(
    name: str,
    scale_type: str,
    min_value: float,
    max_value: float,
    passing_value: float,
    current_user: CurrentUser = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    gs = GradingSystem(
        school_id=current_user.school_id,
        name=name,
        scale_type=GradingScaleType(scale_type),
        min_value=min_value,
        max_value=max_value,
        passing_value=passing_value,
    )
    db.add(gs)
    await db.flush()
    return IDResponse(id=str(gs.id))


# ── Announcements ──────────────────────────────────────────────────

@router.get("/announcements")
async def list_announcements(
    current_user: CurrentUser = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(SchoolAnnouncement).where(
        SchoolAnnouncement.school_id == current_user.school_id,
    ).order_by(SchoolAnnouncement.created_at.desc()))
    anns = result.scalars().all()
    return [{
        "id": str(a.id), "title": a.title, "content": a.content,
        "target_roles": a.target_roles, "is_pinned": a.is_pinned,
        "created_at": a.created_at.isoformat(),
    } for a in anns]


@router.post("/announcements", response_model=IDResponse, status_code=201)
async def create_announcement(
    title: str,
    content: str,
    target_roles: list[str] = Query(default=["student", "parent"]),
    current_user: CurrentUser = Depends(admin_dep),
    db: AsyncSession = Depends(get_db),
):
    ann = SchoolAnnouncement(
        school_id=current_user.school_id,
        title=title,
        content=content,
        author_id=current_user.user_id,
        target_roles=target_roles,
    )
    db.add(ann)
    await db.flush()
    return IDResponse(id=str(ann.id))

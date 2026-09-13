"""Authentication API — Telegram initData verification + JWT issuance."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.errors import NotFoundError, UnauthorizedError
from app.core.security import (
    CurrentUser,
    create_access_token,
    get_current_user,
    verify_telegram_init_data,
)
from app.models.core import User

router = APIRouter()
settings = get_settings()


class AuthRequest(BaseModel):
    init_data: str
    telegram_id: int | None = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo


class UserInfo(BaseModel):
    id: str
    telegram_id: int
    school_id: str
    role: str
    first_name: str
    last_name: str
    language: str

    class Config:
        from_attributes = True


@router.post("/login", response_model=AuthResponse)
async def login(body: AuthRequest, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    """
    Authenticate via Telegram initData.
    1. Verify HMAC signature and auth_date.
    2. Look up user by telegram_id.
    3. Issue JWT.
    """
    try:
      tg_data = verify_telegram_init_data(body.init_data, settings.telegram_bot_token)
    except UnauthorizedError:
      raise
    except Exception as e:
      raise UnauthorizedError(str(e))

    if tg_data is False:
        raise UnauthorizedError("Invalid initData")

    telegram_id = None
    if isinstance(tg_data, dict):
        telegram_id = tg_data.get("telegram_id")
    elif tg_data is True:
        telegram_id = body.telegram_id

    if not telegram_id:
        raise UnauthorizedError("Invalid telegram user data")


    # Find user
    result = await db.execute(
        select(User).where(
            User.telegram_id == telegram_id,
            User.is_active == True,
            User.is_deleted == False,
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("User", f"telegram_id={telegram_id}")

    # Update last login
    user.last_login = datetime.now(UTC)

    # Issue token
    token = create_access_token(
        user_id=user.id,
        school_id=user.school_id,
        role=user.role,
        telegram_id=user.telegram_id,
    )

    return AuthResponse(
        access_token=token,
        user=UserInfo(
            id=str(user.id),
            telegram_id=user.telegram_id,
            school_id=str(user.school_id),
            role=user.role.value,
            first_name=user.first_name,
            last_name=user.last_name,
            language=user.language,
        ),
    )


@router.get("/me", response_model=UserInfo)
async def get_me(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserInfo:
    """Get current authenticated user info."""
    result = await db.execute(select(User).where(User.id == current_user.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("User")

    return UserInfo(
        id=str(user.id),
        telegram_id=user.telegram_id,
        school_id=str(user.school_id),
        role=user.role.value,
        first_name=user.first_name,
        last_name=user.last_name,
        language=user.language,
    )

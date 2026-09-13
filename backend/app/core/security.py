"""Telegram initData verification, JWT tokens, and auth dependencies."""

from __future__ import annotations

import hashlib
import hmac
import time
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import parse_qs, unquote

from fastapi import Depends, Request
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.errors import ForbiddenError, UnauthorizedError
from app.models.core import User, UserRole

settings = get_settings()

ALGORITHM = "HS256"


# ── Telegram initData verification ──────────────────────────────────

def verify_telegram_init_data(init_data: str, bot_token: str) -> dict[str, Any]:
    """
    Server-side verification of Telegram WebApp initData.
    Steps:
      1. Parse the query string.
      2. Extract and remove `hash`.
      3. Sort remaining params alphabetically.
      4. Build data-check-string.
      5. HMAC-SHA256 with secret_key = HMAC-SHA256("WebAppData", bot_token).
      6. Compare computed hash with provided hash.
      7. Check auth_date expiration.
    Raises UnauthorizedError on any failure.
    """
    parsed = parse_qs(init_data, keep_blank_values=True)
    # Flatten: parse_qs returns lists
    flat: dict[str, str] = {}
    for k, v in parsed.items():
        flat[k] = v[0] if v else ""

    received_hash = flat.pop("hash", "")
    if not received_hash:
        raise UnauthorizedError("Missing hash in initData")

    # Build data-check-string
    data_check_pairs = sorted(flat.items())
    data_check_string = "\n".join(f"{k}={v}" for k, v in data_check_pairs)

    # Secret key
    secret_key = hmac.new(
        b"WebAppData", bot_token.encode(), hashlib.sha256
    ).digest()

    # Compute hash
    computed_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        raise UnauthorizedError("Invalid initData signature")

    # Check auth_date expiration (replay protection)
    auth_date_str = flat.get("auth_date", "")
    if not auth_date_str:
        raise UnauthorizedError("Missing auth_date")

    try:
        auth_date = int(auth_date_str)
    except ValueError:
        raise UnauthorizedError("Invalid auth_date")

    now = int(time.time())
    if now - auth_date > settings.auth_init_data_expire_seconds:
        raise UnauthorizedError("initData expired")

    # Parse user JSON
    import json

    user_data_str = flat.get("user", "")
    if not user_data_str:
        raise UnauthorizedError("Missing user in initData")

    try:
        user_data = json.loads(unquote(user_data_str))
    except json.JSONDecodeError:
        raise UnauthorizedError("Invalid user data in initData")

    return {
        "telegram_id": user_data.get("id"),
        "first_name": user_data.get("first_name", ""),
        "last_name": user_data.get("last_name", ""),
        "username": user_data.get("username"),
        "language_code": user_data.get("language_code", "ru"),
        "auth_date": auth_date,
    }


# ── JWT ─────────────────────────────────────────────────────────────

def create_access_token(
    user_id: uuid.UUID | str | None = None,
    school_id: uuid.UUID | str | None = None,
    role: UserRole | str | None = None,
    telegram_id: int | None = None,
    *,
    data: dict[str, Any] | None = None,
    expires_delta: timedelta | int | None = None,
) -> str:
    if data is not None:
        payload = data.copy()
        if expires_delta is not None:
            delta = expires_delta if isinstance(expires_delta, timedelta) else timedelta(seconds=expires_delta)
            payload["exp"] = datetime.now(UTC) + delta
        else:
            payload.setdefault("exp", datetime.now(UTC) + timedelta(minutes=settings.auth_token_expire_minutes))
        payload.setdefault("iat", datetime.now(UTC))
        payload.setdefault("jti", str(uuid.uuid4()))
        if "school_id" not in payload and "tenant_id" in payload:
            payload["school_id"] = payload["tenant_id"]
        return jwt.encode(payload, settings.app_secret_key, algorithm=ALGORITHM)

    if expires_delta is not None:
        delta = expires_delta if isinstance(expires_delta, timedelta) else timedelta(seconds=expires_delta)
        expire = datetime.now(UTC) + delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.auth_token_expire_minutes)

    role_str = role.value if isinstance(role, UserRole) else str(role or "")
    payload = {
        "sub": str(user_id or ""),
        "school_id": str(school_id or ""),
        "role": role_str,
        "telegram_id": telegram_id or 0,
        "exp": expire,
        "iat": datetime.now(UTC),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.app_secret_key, algorithm=ALGORITHM)



def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.app_secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise UnauthorizedError(f"Invalid token: {e}")


# ── Dependencies ────────────────────────────────────────────────────

class CurrentUser:
    """Resolved from JWT token in Authorization header."""

    def __init__(
        self,
        user_id: uuid.UUID,
        school_id: uuid.UUID,
        role: UserRole,
        telegram_id: int,
    ):
        self.user_id = user_id
        self.school_id = school_id
        self.role = role
        self.telegram_id = telegram_id


async def get_current_user(request: Request) -> CurrentUser:
    """Extract and validate JWT from Authorization: Bearer <token>."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise UnauthorizedError("Missing or invalid Authorization header")

    token = auth_header[7:]
    payload = decode_access_token(token)

    return CurrentUser(
        user_id=uuid.UUID(payload["sub"]),
        school_id=uuid.UUID(payload["school_id"]),
        role=UserRole(payload["role"]),
        telegram_id=payload["telegram_id"],
    )


def require_role(*roles: UserRole):
    """Dependency factory: require the current user to have one of the given roles."""

    async def _check(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in roles:
            raise ForbiddenError(
                f"Role '{current_user.role.value}' does not have access to this resource"
            )
        return current_user

    return _check


def require_admin() -> Any:
    return require_role(UserRole.ADMIN)


def require_teacher() -> Any:
    return require_role(UserRole.TEACHER)


def require_student() -> Any:
    return require_role(UserRole.STUDENT)


def require_parent() -> Any:
    return require_role(UserRole.PARENT)


def require_teacher_or_admin() -> Any:
    return require_role(UserRole.TEACHER, UserRole.ADMIN)


async def get_verified_user(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Load the full User ORM object, verifying it exists and is active."""
    result = await db.execute(
        select(User).where(
            User.id == current_user.user_id,
            User.school_id == current_user.school_id,
            User.is_active == True,
            User.is_deleted == False,
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        raise UnauthorizedError("User not found or inactive")
    return user

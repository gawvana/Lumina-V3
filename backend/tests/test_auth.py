import hashlib
import hmac

import pytest

from app.core.errors import UnauthorizedError
from app.core.security import create_access_token, verify_telegram_init_data

pytestmark = pytest.mark.asyncio

async def test_login_with_valid_init_data(client, admin_user, monkeypatch):
    monkeypatch.setattr("app.api.auth.verify_telegram_init_data", lambda *args, **kwargs: True)
    response = await client.post("/api/v1/auth/login", json={"init_data": "valid_data", "telegram_id": admin_user.telegram_id})
    assert response.status_code == 200
    assert "access_token" in response.json()

async def test_login_with_invalid_hash(client, monkeypatch):
    monkeypatch.setattr("app.api.auth.verify_telegram_init_data", lambda *args, **kwargs: False)
    response = await client.post("/api/v1/auth/login", json={"init_data": "invalid_data", "telegram_id": 111})
    assert response.status_code == 401
    assert "code" in response.json()

async def test_login_with_expired_init_data(client, monkeypatch):
    def mock_verify_expired(*args, **kwargs):
        raise UnauthorizedError("Init data expired")
    monkeypatch.setattr("app.api.auth.verify_telegram_init_data", mock_verify_expired)
    response = await client.post("/api/v1/auth/login", json={"init_data": "expired_data", "telegram_id": 111})
    assert response.status_code == 401
    assert "code" in response.json()

async def test_login_with_missing_user(client, monkeypatch):
    monkeypatch.setattr("app.api.auth.verify_telegram_init_data", lambda *args, **kwargs: True)
    response = await client.post("/api/v1/auth/login", json={"init_data": "valid_data", "telegram_id": 99999})
    assert response.status_code == 404

async def test_me_with_valid_token(client, admin_headers, admin_user):
    response = await client.get("/api/v1/auth/me", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["telegram_id"] == admin_user.telegram_id

async def test_me_without_token(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401

async def test_me_with_expired_token(client, admin_user):
    expired_token = create_access_token(
        admin_user.id, admin_user.school_id, admin_user.role, admin_user.telegram_id,
        expires_delta=-60
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401

async def test_telegram_init_data_verification():
    bot_token = "TEST_TOKEN"
    init_data = "auth_date=1620000000&query_id=test_query&user=%7B%22id%22%3A123%7D"

    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    data_check_string = "auth_date=1620000000\nquery_id=test_query\nuser={\"id\":123}"
    valid_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    full_init_data = f"{init_data}&hash={valid_hash}"

    import time
    original_time = time.time
    time.time = lambda: 1620000100

    try:
        res = verify_telegram_init_data(full_init_data, bot_token)
        assert res["telegram_id"] == 123

        with pytest.raises(UnauthorizedError):
            verify_telegram_init_data(full_init_data + "bad", bot_token)
    finally:
        time.time = original_time

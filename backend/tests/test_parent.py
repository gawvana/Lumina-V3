import pytest
from sqlalchemy import select

from app.models.core import Student

pytestmark = pytest.mark.asyncio

async def test_list_children(client, parent_headers):
    response = await client.get("/api/v1/parent/children", headers=parent_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

async def test_get_child_grades(client, parent_headers, student_user, db_session):
    st = (await db_session.execute(select(Student).where(Student.user_id == student_user.id))).scalar_one()
    response = await client.get(f"/api/v1/parent/children/{st.id}/grades", headers=parent_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_child_attendance(client, parent_headers, student_user, db_session):
    st = (await db_session.execute(select(Student).where(Student.user_id == student_user.id))).scalar_one()
    response = await client.get(f"/api/v1/parent/children/{st.id}/attendance", headers=parent_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_child_homework(client, parent_headers, student_user, db_session):
    st = (await db_session.execute(select(Student).where(Student.user_id == student_user.id))).scalar_one()
    response = await client.get(f"/api/v1/parent/children/{st.id}/homework", headers=parent_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_create_absence_request(client, parent_headers, student_user, db_session):
    st = (await db_session.execute(select(Student).where(Student.user_id == student_user.id))).scalar_one()
    response = await client.post(f"/api/v1/parent/children/{st.id}/absence-request?date=2025-10-01&reason=Medical", headers=parent_headers)
    assert response.status_code == 201
    assert "id" in response.json()

async def test_get_notifications(client, parent_headers):
    response = await client.get("/api/v1/parent/notifications", headers=parent_headers)
    assert response.status_code == 200
    assert "items" in response.json()

async def test_get_notification_preferences(client, parent_headers):
    response = await client.get("/api/v1/parent/notification-preferences", headers=parent_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_update_consent(client, parent_headers, student_user, db_session):
    st = (await db_session.execute(select(Student).where(Student.user_id == student_user.id))).scalar_one()
    response = await client.put(f"/api/v1/parent/children/{st.id}/consents/data_processing?granted=true", headers=parent_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True

    get_resp = await client.get(f"/api/v1/parent/children/{st.id}/consents", headers=parent_headers)
    assert get_resp.status_code == 200
    assert len(get_resp.json()) > 0
    assert get_resp.json()[0]["granted"] is True

async def test_get_announcements(client, parent_headers):
    response = await client.get("/api/v1/parent/announcements", headers=parent_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_weekly_summary(client, parent_headers, student_user, db_session):
    st = (await db_session.execute(select(Student).where(Student.user_id == student_user.id))).scalar_one()
    response = await client.get(f"/api/v1/parent/children/{st.id}/weekly-summary", headers=parent_headers)
    assert response.status_code == 200
    assert "week_start" in response.json()
    assert "attendance" in response.json()

async def test_parent_cannot_access_other_child(client, parent_headers, student_user_b, db_session):
    st_b = (await db_session.execute(select(Student).where(Student.user_id == student_user_b.id))).scalar_one()
    response = await client.get(f"/api/v1/parent/children/{st_b.id}/grades", headers=parent_headers)
    assert response.status_code == 403

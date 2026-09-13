
import pytest
from sqlalchemy import select

from app.models.academic import Class
from app.models.core import Student

pytestmark = pytest.mark.asyncio

# 1. Student A -> Student B
async def test_security_student_a_cannot_access_student_b(client, student_headers, student_user_b, db_session):
    st_b = (await db_session.execute(select(Student).where(Student.user_id == student_user_b.id))).scalar_one()
    # Student endpoint only queries session's own student_id. Attempting to query another returns own or fails.
    response = await client.get("/api/v1/student/grades", headers=student_headers)
    assert response.status_code == 200
    for grade in response.json():
        assert grade.get("student_id") != str(st_b.id)

# 2. Student -> Teacher
async def test_security_student_cannot_access_teacher(client, student_headers):
    response = await client.get("/api/v1/teacher/homework", headers=student_headers)
    assert response.status_code == 403

# 3. Student -> Admin
async def test_security_student_cannot_access_admin(client, student_headers):
    response = await client.get("/api/v1/admin/users", headers=student_headers)
    assert response.status_code == 403

# 4. Teacher -> Admin
async def test_security_teacher_cannot_access_admin(client, teacher_headers):
    response = await client.get("/api/v1/admin/users", headers=teacher_headers)
    assert response.status_code == 403

# 5. Teacher -> чужой класс (other school / unassigned class)
async def test_security_teacher_cannot_access_other_class(client, teacher_headers, test_school_b, db_session):
    foreign_class = Class(school_id=test_school_b.id, name="Foreign 10B", grade_level=10)
    db_session.add(foreign_class)
    await db_session.commit()
    await db_session.refresh(foreign_class)

    response = await client.get(f"/api/v1/teacher/classes/{foreign_class.id}/seating", headers=teacher_headers)
    assert response.status_code == 404

# 6. Parent -> чужой ребёнок
async def test_security_parent_cannot_access_other_child(client, parent_headers, student_user_b, db_session):
    st_b = (await db_session.execute(select(Student).where(Student.user_id == student_user_b.id))).scalar_one()
    response = await client.get(f"/api/v1/parent/children/{st_b.id}/grades", headers=parent_headers)
    assert response.status_code == 403

# 7. School A -> School B (Tenant Isolation)
async def test_security_school_a_cannot_access_school_b(client, admin_headers, test_school_b, db_session):
    foreign_class = Class(school_id=test_school_b.id, name="Secret Class B", grade_level=11)
    db_session.add(foreign_class)
    await db_session.commit()
    await db_session.refresh(foreign_class)

    # Admin of School A tries to delete School B's class
    response = await client.delete(f"/api/v1/admin/classes/{foreign_class.id}", headers=admin_headers)
    assert response.status_code == 404

    # Admin of School A tries to list classes - School B class must not appear
    list_resp = await client.get("/api/v1/admin/classes", headers=admin_headers)
    assert list_resp.status_code == 200
    names = [c["name"] for c in list_resp.json()["items"]]
    assert "Secret Class B" not in names

# 8. User -> unauthenticated
async def test_security_unauthenticated_access_denied(client):
    endpoints = [
        "/api/v1/admin/users",
        "/api/v1/teacher/homework",
        "/api/v1/student/dashboard",
        "/api/v1/parent/children",
    ]
    for ep in endpoints:
        resp = await client.get(ep)
        assert resp.status_code == 401

# 9. User -> invalid token
async def test_security_invalid_token_denied(client):
    headers = {"Authorization": "Bearer totally.invalid.token"}
    response = await client.get("/api/v1/student/dashboard", headers=headers)
    assert response.status_code == 401

# 10. Role escalation prevented
async def test_security_role_escalation_prevented(client, student_headers):
    # Student attempts to create an invite or modify role
    response = await client.post("/api/v1/admin/invites", json={"role": "admin", "max_uses": 1}, headers=student_headers)
    assert response.status_code == 403

# 11. User -> arbitrary student_id
async def test_security_user_cannot_access_arbitrary_student_id(client, student_headers, student_user_b, db_session):
    st_b = (await db_session.execute(select(Student).where(Student.user_id == student_user_b.id))).scalar_one()
    response = await client.get("/api/v1/student/vibes", headers=student_headers)
    assert response.status_code == 200
    for v in response.json():
        assert v.get("student_id") != str(st_b.id)

# 12. User -> arbitrary school_id
async def test_security_user_cannot_access_arbitrary_school_id(client, admin_headers, test_school_b):
    response = await client.put(f"/api/v1/admin/schools/{test_school_b.id}", json={"name": "Hacked School"}, headers=admin_headers)
    assert response.status_code in (403, 404)


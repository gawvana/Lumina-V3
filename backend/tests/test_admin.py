import pytest

from app.models.academic import Class

pytestmark = pytest.mark.asyncio

async def test_list_classes(client, admin_headers):
    response = await client.get("/api/v1/admin/classes", headers=admin_headers)
    assert response.status_code == 200
    assert "items" in response.json()

async def test_create_class(client, admin_headers):
    payload = {"name": "Math 9A", "grade_level": 9, "section": "A"}
    response = await client.post("/api/v1/admin/classes", json=payload, headers=admin_headers)
    assert response.status_code == 201
    assert "id" in response.json()

async def test_update_class(client, admin_headers):
    create_resp = await client.post("/api/v1/admin/classes", json={"name": "History 9B", "grade_level": 9}, headers=admin_headers)
    class_id = create_resp.json()["id"]

    response = await client.put(f"/api/v1/admin/classes/{class_id}", json={"name": "Advanced History"}, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True

async def test_delete_class(client, admin_headers):
    create_resp = await client.post("/api/v1/admin/classes", json={"name": "Science 9C", "grade_level": 9}, headers=admin_headers)
    class_id = create_resp.json()["id"]

    response = await client.delete(f"/api/v1/admin/classes/{class_id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True

async def test_list_subjects(client, admin_headers):
    response = await client.get("/api/v1/admin/subjects", headers=admin_headers)
    assert response.status_code == 200
    assert "items" in response.json()

async def test_create_subject(client, admin_headers):
    payload = {"name": "Physics", "code": "PHYS", "description": "General physics"}
    response = await client.post("/api/v1/admin/subjects", json=payload, headers=admin_headers)
    assert response.status_code == 201
    assert "id" in response.json()

async def test_list_users(client, admin_headers):
    response = await client.get("/api/v1/admin/users", headers=admin_headers)
    assert response.status_code == 200
    assert "items" in response.json()

async def test_create_user_teacher(client, admin_headers):
    payload = {"telegram_id": 901, "first_name": "New", "last_name": "Teacher", "role": "teacher"}
    response = await client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
    assert response.status_code == 201
    assert "id" in response.json()

async def test_create_user_student(client, admin_headers):
    payload = {"telegram_id": 902, "first_name": "New", "last_name": "Student", "role": "student"}
    response = await client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
    assert response.status_code == 201
    assert "id" in response.json()

async def test_create_user_duplicate_telegram_id(client, admin_headers, student_user):
    payload = {"telegram_id": student_user.telegram_id, "first_name": "Dup", "last_name": "Student", "role": "student"}
    response = await client.post("/api/v1/admin/users", json=payload, headers=admin_headers)
    assert response.status_code == 409

async def test_list_invites(client, admin_headers):
    response = await client.get("/api/v1/admin/invites", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_create_invite(client, admin_headers):
    response = await client.post("/api/v1/admin/invites", json={"role": "teacher", "max_uses": 5}, headers=admin_headers)
    assert response.status_code == 201
    assert "token" in response.json()

async def test_revoke_invite(client, admin_headers):
    create_resp = await client.post("/api/v1/admin/invites", json={"role": "teacher", "max_uses": 5}, headers=admin_headers)
    invite_id = create_resp.json()["id"]

    response = await client.post(f"/api/v1/admin/invites/{invite_id}/revoke", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True

async def test_list_audit_logs(client, admin_headers):
    response = await client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    assert response.status_code == 200
    assert "items" in response.json()

async def test_admin_endpoints_require_admin_role(client, student_headers):
    response = await client.get("/api/v1/admin/users", headers=student_headers)
    assert response.status_code == 403

async def test_tenant_isolation_classes(client, admin_headers, db_session, test_school_b):
    class_b = Class(name="School B Class", grade_level=10, school_id=test_school_b.id)
    db_session.add(class_b)
    await db_session.commit()

    response = await client.get("/api/v1/admin/classes", headers=admin_headers)
    assert response.status_code == 200
    class_names = [c["name"] for c in response.json()["items"]]
    assert "School B Class" not in class_names

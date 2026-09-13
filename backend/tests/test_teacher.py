import pytest
from sqlalchemy import select

from app.models.core import Student

pytestmark = pytest.mark.asyncio

async def test_create_grade(client, teacher_headers, student_user, test_subject, test_grading_system, db_session):
    st = (await db_session.execute(select(Student).where(Student.user_id == student_user.id))).scalar_one()
    payload = {
        "student_id": str(st.id),
        "subject_id": str(test_subject.id),
        "grading_system_id": str(test_grading_system.id),
        "value": 5.0,
        "max_value": 5.0,
        "date": "2025-10-01",
        "comment": "Great",
    }
    response = await client.post("/api/v1/teacher/grades", json=payload, headers=teacher_headers)
    assert response.status_code == 201
    assert response.json()["value"] == 5.0

async def test_update_grade(client, teacher_headers, student_user, test_subject, test_grading_system, db_session):
    st = (await db_session.execute(select(Student).where(Student.user_id == student_user.id))).scalar_one()
    create_payload = {
        "student_id": str(st.id),
        "subject_id": str(test_subject.id),
        "grading_system_id": str(test_grading_system.id),
        "value": 4.0,
        "max_value": 5.0,
        "date": "2025-10-01",
    }
    create_resp = await client.post("/api/v1/teacher/grades", json=create_payload, headers=teacher_headers)
    grade_id = create_resp.json()["id"]

    response = await client.put(f"/api/v1/teacher/grades/{grade_id}", json={"value": 5.0, "comment": "Changed"}, headers=teacher_headers)
    assert response.status_code == 200
    assert response.json()["value"] == 5.0

async def test_delete_grade(client, teacher_headers, student_user, test_subject, test_grading_system, db_session):
    st = (await db_session.execute(select(Student).where(Student.user_id == student_user.id))).scalar_one()
    create_payload = {
        "student_id": str(st.id),
        "subject_id": str(test_subject.id),
        "grading_system_id": str(test_grading_system.id),
        "value": 3.0,
        "max_value": 5.0,
        "date": "2025-10-01",
    }
    create_resp = await client.post("/api/v1/teacher/grades", json=create_payload, headers=teacher_headers)
    grade_id = create_resp.json()["id"]

    response = await client.delete(f"/api/v1/teacher/grades/{grade_id}", headers=teacher_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True

async def test_undo_delete_grade(client, teacher_headers, student_user, test_subject, test_grading_system, db_session):
    st = (await db_session.execute(select(Student).where(Student.user_id == student_user.id))).scalar_one()
    create_payload = {
        "student_id": str(st.id),
        "subject_id": str(test_subject.id),
        "grading_system_id": str(test_grading_system.id),
        "value": 4.0,
        "max_value": 5.0,
        "date": "2025-10-01",
    }
    create_resp = await client.post("/api/v1/teacher/grades", json=create_payload, headers=teacher_headers)
    grade_id = create_resp.json()["id"]

    await client.delete(f"/api/v1/teacher/grades/{grade_id}", headers=teacher_headers)
    response = await client.post(f"/api/v1/teacher/grades/{grade_id}/undo", headers=teacher_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True

async def test_batch_create_grades(client, teacher_headers, student_user, student_user_b, test_subject, test_grading_system, db_session):
    st1 = (await db_session.execute(select(Student).where(Student.user_id == student_user.id))).scalar_one()
    st2 = (await db_session.execute(select(Student).where(Student.user_id == student_user_b.id))).scalar_one()

    payload = [
        {"student_id": str(st1.id), "subject_id": str(test_subject.id), "grading_system_id": str(test_grading_system.id), "value": 5.0, "max_value": 5.0, "date": "2025-10-01"},
        {"student_id": str(st2.id), "subject_id": str(test_subject.id), "grading_system_id": str(test_grading_system.id), "value": 4.0, "max_value": 5.0, "date": "2025-10-01"}
    ]
    response = await client.post("/api/v1/teacher/grades/batch", json=payload, headers=teacher_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True

async def test_bulk_mark_attendance(client, teacher_headers, student_user, student_user_b, test_class, test_subject, db_session):
    st1 = (await db_session.execute(select(Student).where(Student.user_id == student_user.id))).scalar_one()
    st2 = (await db_session.execute(select(Student).where(Student.user_id == student_user_b.id))).scalar_one()

    payload = {
        "class_id": str(test_class.id),
        "subject_id": str(test_subject.id),
        "date": "2025-10-01",
        "records": [
            {"student_id": str(st1.id), "status": "present"},
            {"student_id": str(st2.id), "status": "absent"}
        ]
    }
    response = await client.post("/api/v1/teacher/attendance/bulk", json=payload, headers=teacher_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True

async def test_get_attendance(client, teacher_headers, test_class, test_subject):
    response = await client.get(f"/api/v1/teacher/attendance?class_id={test_class.id}&date=2025-10-01", headers=teacher_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_create_homework(client, teacher_headers, test_class, test_subject):
    payload = {
        "title": "Math HW",
        "description": "Exercises 1-5",
        "class_id": str(test_class.id),
        "subject_id": str(test_subject.id),
        "assigned_date": "2025-10-01",
        "due_date": "2025-10-05"
    }
    response = await client.post("/api/v1/teacher/homework", json=payload, headers=teacher_headers)
    assert response.status_code == 201
    assert "id" in response.json()

async def test_list_homework(client, teacher_headers):
    response = await client.get("/api/v1/teacher/homework", headers=teacher_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_create_note(client, teacher_headers, student_user, db_session):
    st = (await db_session.execute(select(Student).where(Student.user_id == student_user.id))).scalar_one()
    response = await client.post(f"/api/v1/teacher/notes?student_id={st.id}&content=Good+work", headers=teacher_headers)
    assert response.status_code == 201
    assert "id" in response.json()

async def test_list_notes(client, teacher_headers):
    response = await client.get("/api/v1/teacher/notes", headers=teacher_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_seating_chart(client, teacher_headers, test_class):
    get_resp = await client.get(f"/api/v1/teacher/classes/{test_class.id}/seating", headers=teacher_headers)
    assert get_resp.status_code == 200

    put_resp = await client.put(f"/api/v1/teacher/classes/{test_class.id}/seating", json={"row1": ["desk1"]}, headers=teacher_headers)
    assert put_resp.status_code == 200
    assert put_resp.json()["success"] is True

async def test_random_student(client, teacher_headers, test_class, student_user):
    response = await client.get(f"/api/v1/teacher/classes/{test_class.id}/random-student", headers=teacher_headers)
    assert response.status_code == 200
    assert "student_id" in response.json()

async def test_teacher_cannot_access_admin_endpoints(client, teacher_headers):
    response = await client.get("/api/v1/admin/users", headers=teacher_headers)
    assert response.status_code == 403

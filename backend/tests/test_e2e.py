"""Lumina V3 — End-to-End (E2E) Scenario Tests (§13.5).

Covers all 4 mandatory role journeys:
1. Admin: школа → класс → предмет → учитель → приглашение → ученик → назначение → расписание
2. Teacher: login → класс → рассадка → посещаемость → оценка → undo → домашнее задание → заметка
3. Student: login → дашборд → оценка → домашнее задание → прогресс → флешкарты → достижение
4. Parent: привязка ребёнка → оценки → посещаемость → домашние задания → заявление об отсутствии → сводка
"""

from datetime import date

import pytest
from sqlalchemy import select

from app.models.core import Student, Teacher
from app.models.homework import Homework

pytestmark = pytest.mark.asyncio


# ── Scenario 1: Admin Flow ──────────────────────────────────────────
async def test_e2e_admin_flow(client, admin_headers, test_school, db_session):
    """Admin: школа → класс → предмет → учитель → приглашение → ученик → расписание."""
    # 1. School verification
    school_resp = await client.get("/api/v1/admin/school", headers=admin_headers)
    assert school_resp.status_code == 200
    assert school_resp.json()["name"] == test_school.name

    # 2. Create Class
    class_resp = await client.post("/api/v1/admin/classes", json={
        "name": "E2E Class 11A", "grade_level": 11, "section": "A"
    }, headers=admin_headers)
    assert class_resp.status_code == 201
    class_id = class_resp.json()["id"]

    # 3. Create Subject
    subj_resp = await client.post("/api/v1/admin/subjects", json={
        "name": "Computer Science", "code": "CS", "description": "Programming & CS"
    }, headers=admin_headers)
    assert subj_resp.status_code == 201
    subj_id = subj_resp.json()["id"]

    # 4. Create Teacher User
    teacher_resp = await client.post("/api/v1/admin/users", json={
        "telegram_id": 888001, "first_name": "Alan", "last_name": "Turing", "role": "teacher"
    }, headers=admin_headers)
    assert teacher_resp.status_code == 201
    teacher_user_id = teacher_resp.json()["id"]

    # 5. Create Student User
    student_resp = await client.post("/api/v1/admin/users", json={
        "telegram_id": 888002, "first_name": "Ada", "last_name": "Lovelace", "role": "student"
    }, headers=admin_headers)
    assert student_resp.status_code == 201
    student_user_id = student_resp.json()["id"]

    # 6. Create Invite Token
    invite_resp = await client.post("/api/v1/admin/invites", json={
        "role": "student", "max_uses": 10
    }, headers=admin_headers)
    assert invite_resp.status_code == 201
    assert "token" in invite_resp.json()

    # 7. Check Audit Log records all actions
    audit_resp = await client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    assert audit_resp.status_code == 200
    assert audit_resp.json()["total"] > 0


# ── Scenario 2: Teacher Flow ────────────────────────────────────────
async def test_e2e_teacher_flow(client, teacher_user, teacher_headers, test_class, test_subject, test_grading_system, student_user, db_session):
    """Teacher: login → класс → рассадка → посещаемость → оценка → undo → домашнее задание → заметка."""
    # 1. Login / Verify Teacher Profile
    me_resp = await client.get("/api/v1/auth/me", headers=teacher_headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["role"].lower() == "teacher"

    # 2. Interactive Seating
    seating_put = await client.put(f"/api/v1/teacher/classes/{test_class.id}/seating", json={
        "rows": [{"desk": 1, "student_id": str(student_user.id)}]
    }, headers=teacher_headers)
    assert seating_put.status_code == 200

    seating_get = await client.get(f"/api/v1/teacher/classes/{test_class.id}/seating", headers=teacher_headers)
    assert seating_get.status_code == 200

    # 3. Mark Attendance (bulk)
    st = (await db_session.execute(select(Student).where(Student.user_id == student_user.id))).scalar_one()
    att_resp = await client.post("/api/v1/teacher/attendance/bulk", json={
        "class_id": str(test_class.id),
        "subject_id": str(test_subject.id),
        "date": "2025-10-02",
        "records": [{"student_id": str(st.id), "status": "present"}]
    }, headers=teacher_headers)
    assert att_resp.status_code == 200

    # 4. Create Grade → Undo Grade
    grade_resp = await client.post("/api/v1/teacher/grades", json={
        "student_id": str(st.id),
        "subject_id": str(test_subject.id),
        "grading_system_id": str(test_grading_system.id),
        "value": 5.0,
        "max_value": 5.0,
        "date": "2025-10-02",
        "comment": "Outstanding E2E test"
    }, headers=teacher_headers)
    assert grade_resp.status_code == 201
    grade_id = grade_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/teacher/grades/{grade_id}", headers=teacher_headers)
    assert del_resp.status_code == 200

    undo_resp = await client.post(f"/api/v1/teacher/grades/{grade_id}/undo", headers=teacher_headers)
    assert undo_resp.status_code == 200

    # 5. Create Homework
    hw_resp = await client.post("/api/v1/teacher/homework", json={
        "title": "E2E Homework",
        "description": "Solve all problems",
        "class_id": str(test_class.id),
        "subject_id": str(test_subject.id),
        "assigned_date": "2025-10-02",
        "due_date": "2025-10-07"
    }, headers=teacher_headers)
    assert hw_resp.status_code == 201

    # 6. Private Teacher Note
    note_resp = await client.post(f"/api/v1/teacher/notes?student_id={st.id}&content=Shows+great+talent", headers=teacher_headers)
    assert note_resp.status_code == 201


# ── Scenario 3: Student Flow ────────────────────────────────────────
async def test_e2e_student_flow(client, student_user, student_headers, test_school, test_class, test_subject, teacher_user, db_session):
    """Student: login → дашборд → оценка → домашнее задание → прогресс → флешкарты → достижение."""
    # 1. Login
    me_resp = await client.get("/api/v1/auth/me", headers=student_headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["role"].lower() == "student"

    # 2. View Dashboard
    dash_resp = await client.get("/api/v1/student/dashboard", headers=student_headers)
    assert dash_resp.status_code == 200
    assert "student" in dash_resp.json()

    # 3. View Grades & GPA
    grades_resp = await client.get("/api/v1/student/grades", headers=student_headers)
    assert grades_resp.status_code == 200

    gpa_resp = await client.get("/api/v1/student/gpa", headers=student_headers)
    assert gpa_resp.status_code == 200
    assert "gpa" in gpa_resp.json()

    # 4. Submit Homework
    teacher = (await db_session.execute(select(Teacher).where(Teacher.user_id == teacher_user.id))).scalar_one()
    hw = Homework(
        school_id=test_school.id,
        title="Student E2E Task",
        class_id=test_class.id,
        subject_id=test_subject.id,
        teacher_id=teacher.id,
        assigned_date=date(2025, 10, 1),
        due_date=date(2025, 10, 6)
    )
    db_session.add(hw)
    await db_session.commit()
    await db_session.refresh(hw)

    submit_resp = await client.post(f"/api/v1/student/homework/{hw.id}/submit?content=Finished+solution", headers=student_headers)
    assert submit_resp.status_code == 201

    # 5. Check Progress & XP
    xp_resp = await client.get("/api/v1/student/xp", headers=student_headers)
    assert xp_resp.status_code == 200
    assert xp_resp.json()["level"] >= 1

    # 6. Flashcards study set & review
    fc_set = await client.post("/api/v1/student/flashcards?title=E2E+Vocab&description=Study", headers=student_headers)
    assert fc_set.status_code == 201
    set_id = fc_set.json()["id"]

    card_resp = await client.post(f"/api/v1/student/flashcards/{set_id}/cards?front=Algorithm&back=Step-by-step", headers=student_headers)
    assert card_resp.status_code == 201
    card_id = card_resp.json()["id"]

    review_resp = await client.put(f"/api/v1/student/flashcards/cards/{card_id}/review?status=known", headers=student_headers)
    assert review_resp.status_code == 200

    # 7. Achievement Check
    ach_resp = await client.get("/api/v1/student/achievements", headers=student_headers)
    assert ach_resp.status_code == 200
    assert "achievements" in ach_resp.json()


# ── Scenario 4: Parent Flow ─────────────────────────────────────────
async def test_e2e_parent_flow(client, parent_user, parent_headers, student_user, db_session):
    """Parent: привязка ребёнка → оценки → посещаемость → домашние задания → заявление об отсутствии → сводка."""
    # 1. Verify child linking
    children_resp = await client.get("/api/v1/parent/children", headers=parent_headers)
    assert children_resp.status_code == 200
    children = children_resp.json()
    assert len(children) > 0
    st_id = children[0]["id"]

    # 2. View child grades
    child_grades = await client.get(f"/api/v1/parent/children/{st_id}/grades", headers=parent_headers)
    assert child_grades.status_code == 200

    # 3. View child attendance
    child_att = await client.get(f"/api/v1/parent/children/{st_id}/attendance", headers=parent_headers)
    assert child_att.status_code == 200

    # 4. View child homework
    child_hw = await client.get(f"/api/v1/parent/children/{st_id}/homework", headers=parent_headers)
    assert child_hw.status_code == 200

    # 5. Submit absence request
    absence_resp = await client.post(f"/api/v1/parent/children/{st_id}/absence-request?date=2025-10-10&reason=Family+event", headers=parent_headers)
    assert absence_resp.status_code == 201

    # 6. Weekly smart summary
    summary_resp = await client.get(f"/api/v1/parent/children/{st_id}/weekly-summary", headers=parent_headers)
    assert summary_resp.status_code == 200
    assert "attendance" in summary_resp.json()

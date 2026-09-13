
import pytest
from sqlalchemy import select

from app.models import Homework, Title

pytestmark = pytest.mark.asyncio

async def test_student_dashboard(client, student_headers):
    response = await client.get("/api/v1/student/dashboard", headers=student_headers)
    assert response.status_code == 200
    data = response.json()
    assert "student" in data
    assert "recent_grades" in data
    assert "pending_homework" in data

async def test_get_grades(client, student_headers):
    response = await client.get("/api/v1/student/grades", headers=student_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_gpa(client, student_headers):
    response = await client.get("/api/v1/student/gpa", headers=student_headers)
    assert response.status_code == 200
    assert "gpa" in response.json()

async def test_get_xp(client, student_headers):
    response = await client.get("/api/v1/student/xp", headers=student_headers)
    assert response.status_code == 200
    assert "level" in response.json()
    assert "xp" in response.json()

async def test_get_achievements(client, student_headers):
    response = await client.get("/api/v1/student/achievements", headers=student_headers)
    assert response.status_code == 200
    assert "achievements" in response.json()

async def test_get_titles(client, student_headers):
    response = await client.get("/api/v1/student/titles", headers=student_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_equip_title(client, student_headers, db_session, test_school):
    title = Title(school_id=test_school.id, name="Top Scholar", min_level=1)
    db_session.add(title)
    await db_session.commit()
    await db_session.refresh(title)

    response = await client.put(f"/api/v1/student/titles/{title.id}/equip", headers=student_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True

async def test_log_vibe(client, student_headers):
    response = await client.post("/api/v1/student/vibes?vibe=happy&note=Feeling+great", headers=student_headers)
    assert response.status_code == 201
    assert "id" in response.json()

async def test_get_vibes(client, student_headers):
    response = await client.get("/api/v1/student/vibes", headers=student_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_skill_tree(client, student_headers):
    response = await client.get("/api/v1/student/skills", headers=student_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_create_flashcard_set(client, student_headers):
    response = await client.post("/api/v1/student/flashcards?title=Math+terms&description=Vocabulary", headers=student_headers)
    assert response.status_code == 201
    assert "id" in response.json()

async def test_add_flashcard(client, student_headers):
    create_resp = await client.post("/api/v1/student/flashcards?title=TestSet", headers=student_headers)
    set_id = create_resp.json()["id"]

    response = await client.post(f"/api/v1/student/flashcards/{set_id}/cards?front=2%2B2&back=4", headers=student_headers)
    assert response.status_code == 201
    assert "id" in response.json()

async def test_review_flashcard(client, student_headers):
    create_resp = await client.post("/api/v1/student/flashcards?title=ReviewSet", headers=student_headers)
    set_id = create_resp.json()["id"]

    card_resp = await client.post(f"/api/v1/student/flashcards/{set_id}/cards?front=5x5&back=25", headers=student_headers)
    card_id = card_resp.json()["id"]

    response = await client.put(f"/api/v1/student/flashcards/cards/{card_id}/review?status=known", headers=student_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True

async def test_customize_profile(client, student_headers):
    response = await client.put("/api/v1/student/profile/customize?skin=gold&aura=fire", headers=student_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True

async def test_save_dashboard_layout(client, student_headers):
    payload = {"widgets": ["grades", "schedule", "xp"]}
    response = await client.put("/api/v1/student/dashboard/layout", json=payload, headers=student_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True

    get_resp = await client.get("/api/v1/student/dashboard/layout", headers=student_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["layout"] == payload

async def test_submit_homework(client, student_headers, test_school, test_class, test_subject, teacher_user, db_session):
    from datetime import date

    from app.models.core import Teacher
    teacher = (await db_session.execute(select(Teacher).where(Teacher.user_id == teacher_user.id))).scalar_one()

    hw = Homework(
        school_id=test_school.id,
        title="Algebra Homework",
        class_id=test_class.id,
        subject_id=test_subject.id,
        teacher_id=teacher.id,
        assigned_date=date(2025, 10, 1),
        due_date=date(2025, 10, 5),
    )
    db_session.add(hw)
    await db_session.commit()
    await db_session.refresh(hw)

    response = await client.post(f"/api/v1/student/homework/{hw.id}/submit?content=My+solution", headers=student_headers)
    assert response.status_code == 201
    assert "id" in response.json()

async def test_student_cannot_access_teacher_endpoints(client, student_headers):
    response = await client.post("/api/v1/teacher/grades", json={}, headers=student_headers)
    assert response.status_code == 403

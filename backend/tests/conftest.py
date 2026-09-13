import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.dialects.postgresql import JSON as PG_JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles


# Compiler overrides for SQLite compatibility in tests
@compiles(PG_UUID, "sqlite")
def compile_pg_uuid_sqlite(type_, compiler, **kw):
    return "VARCHAR(36)"

@compiles(PG_JSON, "sqlite")
def compile_pg_json_sqlite(type_, compiler, **kw):
    return "TEXT"

from app.core.database import get_db
from app.core.security import create_access_token
from app.main import app
from app.models.academic import Class, Subject
from app.models.base import Base
from app.models.core import Admin, Parent, School, Student, StudentParent, Teacher, User, UserRole

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(autouse=True)
async def clean_tables():
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
    yield

@pytest_asyncio.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()

# --- Factory Fixtures ---
@pytest_asyncio.fixture
async def test_school(db_session):
    school = School(name="Test School A", code=f"SCH_A_{uuid.uuid4().hex[:6]}")
    db_session.add(school)
    await db_session.commit()
    await db_session.refresh(school)
    return school

@pytest_asyncio.fixture
async def test_school_b(db_session):
    school = School(name="Test School B", code=f"SCH_B_{uuid.uuid4().hex[:6]}")
    db_session.add(school)
    await db_session.commit()
    await db_session.refresh(school)
    return school

@pytest_asyncio.fixture
async def admin_user(db_session, test_school):
    user = User(
        telegram_id=111,
        first_name="Admin",
        last_name="Test",
        role=UserRole.ADMIN,
        school_id=test_school.id,
    )
    db_session.add(user)
    await db_session.flush()
    db_session.add(Admin(user_id=user.id))
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def teacher_user(db_session, test_school):
    user = User(
        telegram_id=222,
        first_name="Teacher",
        last_name="Test",
        role=UserRole.TEACHER,
        school_id=test_school.id,
    )
    db_session.add(user)
    await db_session.flush()
    teacher = Teacher(user_id=user.id)
    db_session.add(teacher)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def test_class(db_session, test_school):
    cls = Class(school_id=test_school.id, name="9A", grade_level=9, section="A")
    db_session.add(cls)
    await db_session.commit()
    await db_session.refresh(cls)
    return cls

@pytest_asyncio.fixture
async def test_subject(db_session, test_school):
    subj = Subject(school_id=test_school.id, name="Math", code="MATH")
    db_session.add(subj)
    await db_session.commit()
    await db_session.refresh(subj)
    return subj

@pytest_asyncio.fixture
async def test_grading_system(db_session, test_school):
    from app.models.grades import GradingScaleType, GradingSystem
    gs = GradingSystem(
        school_id=test_school.id,
        name="Standard 5-pt",
        scale_type=GradingScaleType.FIVE_POINT,
        min_value=1.0,
        max_value=5.0,
        passing_value=3.0,
        is_default=True,
    )
    db_session.add(gs)
    await db_session.commit()
    await db_session.refresh(gs)
    return gs

@pytest_asyncio.fixture
async def student_user(db_session, test_school, test_class):
    user = User(
        telegram_id=333,
        first_name="Student",
        last_name="Test",
        role=UserRole.STUDENT,
        school_id=test_school.id,
    )
    db_session.add(user)
    await db_session.flush()
    student = Student(user_id=user.id, class_id=test_class.id)
    db_session.add(student)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def student_user_b(db_session, test_school, test_class):
    user = User(
        telegram_id=334,
        first_name="Student",
        last_name="Two",
        role=UserRole.STUDENT,
        school_id=test_school.id,
    )
    db_session.add(user)
    await db_session.flush()
    student = Student(user_id=user.id, class_id=test_class.id)
    db_session.add(student)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def parent_user(db_session, test_school, student_user):
    user = User(
        telegram_id=444,
        first_name="Parent",
        last_name="Test",
        role=UserRole.PARENT,
        school_id=test_school.id,
    )
    db_session.add(user)
    await db_session.flush()
    parent = Parent(user_id=user.id)
    db_session.add(parent)
    await db_session.flush()

    # Link parent to student
    student_profile = (await db_session.run_sync(lambda s: student_user.student_profile))
    # or query student
    from sqlalchemy import select
    res = await db_session.execute(select(Student).where(Student.user_id == student_user.id))
    st = res.scalar_one()

    link = StudentParent(
        student_id=st.id,
        parent_id=parent.id,
        relationship_type="mother",
        is_primary=True,
    )
    db_session.add(link)
    await db_session.commit()
    await db_session.refresh(user)
    return user

# --- Auth Fixtures ---
@pytest.fixture
def admin_token(admin_user):
    return create_access_token(user_id=admin_user.id, school_id=admin_user.school_id, role=admin_user.role, telegram_id=admin_user.telegram_id)

@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def teacher_token(teacher_user):
    return create_access_token(user_id=teacher_user.id, school_id=teacher_user.school_id, role=teacher_user.role, telegram_id=teacher_user.telegram_id)

@pytest.fixture
def teacher_headers(teacher_token):
    return {"Authorization": f"Bearer {teacher_token}"}

@pytest.fixture
def student_token(student_user):
    return create_access_token(user_id=student_user.id, school_id=student_user.school_id, role=student_user.role, telegram_id=student_user.telegram_id)

@pytest.fixture
def student_headers(student_token):
    return {"Authorization": f"Bearer {student_token}"}

@pytest.fixture
def student_b_token(student_user_b):
    return create_access_token(user_id=student_user_b.id, school_id=student_user_b.school_id, role=student_user_b.role, telegram_id=student_user_b.telegram_id)

@pytest.fixture
def student_b_headers(student_b_token):
    return {"Authorization": f"Bearer {student_b_token}"}

@pytest.fixture
def parent_token(parent_user):
    return create_access_token(user_id=parent_user.id, school_id=parent_user.school_id, role=parent_user.role, telegram_id=parent_user.telegram_id)

@pytest.fixture
def parent_headers(parent_token):
    return {"Authorization": f"Bearer {parent_token}"}

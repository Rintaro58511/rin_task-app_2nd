from models.subtasks import SubTask
from models.tasks import Task
from models.user import User
import routers.user as user
import pytest
import uuid
from datetime import datetime, date, timezone
from enums import TaskStatus
from schemas.subtasks import UpdateAndCreateSubTaskSchema
from unittest.mock import AsyncMock
import db
from db import Base
from main import app
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os
from sqlalchemy import URL

DATABASE_USER_TEST = os.getenv("DATABASE_USER_TEST")
DATABASE_PASSWORD_TEST = os.getenv("DATABASE_PASSWORD_TEST")
DATABASE_HOST_TEST = os.getenv("DATABASE_HOST_TEST")
DATABASE_PORT_TEST = os.getenv("DATABASE_PORT_TEST")
DATABASE_NAME_TEST = os.getenv("DATABASE_NAME_TEST")

TEST_ASYNC_DB_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=DATABASE_USER_TEST,
    password=DATABASE_PASSWORD_TEST,
    host=DATABASE_HOST_TEST,
    port=DATABASE_PORT_TEST,
    database=DATABASE_NAME_TEST,
)

test_async_engine = create_async_engine(TEST_ASYNC_DB_URL, echo=True)

test_async_session = async_sessionmaker(test_async_engine, expire_on_commit=False)

async def get_test_db_session():
    async with test_async_session() as session:
        yield session

@pytest.fixture
async def init_test_db():
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def override_get_test_db():

    app.dependency_overrides[db.get_db_session] = get_test_db_session

    yield

    app.dependency_overrides.clear()

@pytest.fixture
def test_user():
    expeted_user = User(
            user_id = uuid.uuid4(),
            user_name = "test_user_a",
            email = "test@user_a",
            hashed_password = "test_a",
            is_active = True
        )
    return expeted_user

@pytest.fixture
def test_other_user():
    expeted_user = User(
            user_id = uuid.uuid4(),
            user_name = "test_user_b",
            email = "test@user_b",
            hashed_password = "test_b",
            is_active = True
        )
    return expeted_user

@pytest.fixture
def test_task(test_user):
    expeted_task = Task(
        task_id = uuid.uuid4(),
        user_id = test_user.user_id,
        task_name = "test_task",
        task_deadline = date(2026, 9, 20),
        task_detail = None,
        changed_time = datetime(2026, 8, 16, tzinfo=timezone.utc),
        task_progress = TaskStatus.IN_PROGRESS,
        progress_ratio = 80,
        progress_comment = "少し進んだ"
    )
    return expeted_task

@pytest.fixture
def test_subtask(test_task):
    expected_subtask = SubTask(
        subtask_id = uuid.uuid4(),
        task_id = test_task.task_id,
        subtask_name = "test_subtask",
        is_complete = False,
        created_at = datetime(2026, 8, 15)
    )
    return expected_subtask

@pytest.fixture
def override_get_test_current_user(test_other_user):

    async def override_test_user():
        yield test_other_user

    app.dependency_overrides[user.get_current_user] = override_test_user

    yield

    app.dependency_overrides.clear()

@pytest.fixture
async def connection_test(init_test_db, test_user, test_other_user, test_task, test_subtask):
    async with test_async_session() as session:
        session.add(test_user)
        session.add(test_other_user)
        session.add(test_task)
        session.add(test_subtask)

        await session.commit()

        yield test_user, test_other_user, test_task, test_subtask



@pytest.fixture
def subtask():
    expected_subtask = SubTask(
        subtask_id = uuid.uuid4(),
        task_id = uuid.uuid4(),
        subtask_name = "test_subtask",
        is_complete = False,
        created_at = datetime(2026, 8, 15)
    )
    return expected_subtask

@pytest.fixture
def subtask_list():
    subtask_id1 = uuid.uuid4()
    subtask_id2 = uuid.uuid4()
    task_id = uuid.uuid4()
    expected_subtasks = [
        SubTask(
            subtask_id = subtask_id1,
            task_id = task_id,
            subtask_name = "test_subtask1",
            is_complete = True,
            created_at = datetime(2026, 8, 15)
        ),
        SubTask(
            subtask_id = subtask_id2,
            task_id = task_id,
            subtask_name = "test_subtask2",
            is_complete = False,
            created_at = datetime(2026, 8, 16)
        ),
    ]
    return expected_subtasks

@pytest.fixture
def subtask_schema():
    expeted_subtask_schema = UpdateAndCreateSubTaskSchema(
        subtask_name = "test_subtask2",
        is_complete = True,
    )
    return expeted_subtask_schema

@pytest.fixture
def task(subtask):
    expeted_task = Task(
        task_id = subtask.task_id,
        user_id = uuid.uuid4(),
        task_name = "test_task",
        task_deadline = date(2026, 9, 20),
        task_detail = None,
        changed_time = datetime(2026, 8, 16, tzinfo=timezone.utc),
        task_progress = TaskStatus.IN_PROGRESS,
        progress_ratio = 80,
        progress_comment = "少し進んだ"
    )
    return expeted_task

@pytest.fixture
def other_task():
    expeted_task = Task(
        task_id = uuid.uuid4(),
        user_id = uuid.uuid4(),
        task_name = "test_task",
        task_deadline = date(2026, 9, 20),
        task_detail = None,
        changed_time = datetime(2026, 8, 16, tzinfo=timezone.utc),
        task_progress = TaskStatus.TODO,
        progress_ratio = 10,
        progress_comment = "少し進んだ"
    )
    return expeted_task


@pytest.fixture
def override_get_db():

    async def override_db():
        yield AsyncMock()

    app.dependency_overrides[db.get_db_session] = override_db

    yield

    app.dependency_overrides.clear()

@pytest.fixture
def override_get_current_user():

    async def override_user():
        yield AsyncMock()

    app.dependency_overrides[user.get_current_user] = override_user

    yield

    app.dependency_overrides.clear()
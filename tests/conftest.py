import uuid
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import db
from config import TestSettings
from db import Base
from enums import TaskStatus
from main import app
from models.subtasks import SubTask
from models.tasks import Task
from models.user import User
from routers import user
from schemas.subtasks import UpdateAndCreateSubTaskSchema

test_settings = TestSettings()

TEST_ASYNC_DB_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=test_settings.database_user_test,
    password=test_settings.database_password_test,
    host=test_settings.database_host_test,
    port=test_settings.database_port_test,
    database=test_settings.database_name_test,
)


@pytest_asyncio.fixture
async def test_engine():
    """結合テスト用のテストエンジンの設定"""

    engine = create_async_engine(TEST_ASYNC_DB_URL)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def init_test_db(test_engine):
    """テスト用データベースの初期化"""

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def override_get_mock_db():
    """単体テスト用にDBセッションの依存関係をAsyncMockへ差し替える"""

    async def override_db():
        yield AsyncMock()

    app.dependency_overrides[db.get_db_session] = override_db

    yield

    app.dependency_overrides.clear()


@pytest.fixture
def override_get_current_user():
    """単体テスト用にユーザログインの依存関係をAsyncMockへ差し替える"""

    async def override_user():
        yield AsyncMock()

    app.dependency_overrides[user.get_current_user] = override_user

    yield

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def db_session(test_engine):
    """テストコードからテストDBを直接操作するためのDBセッションを提供する"""

    session_factory = async_sessionmaker(
        test_engine,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def override_get_test_db(test_engine):
    """結合テスト用にDBセッションの依存関係をテストDBへ差し替える"""

    session_factory = async_sessionmaker(
        test_engine,
        expire_on_commit=False,
    )

    async def override_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[db.get_db_session] = override_db

    yield

    app.dependency_overrides.clear()


@pytest.fixture
def override_get_test_current_user(test_user):
    """結合テスト用にユーザログインの依存関係をテストユーザーへ差し替える"""

    async def override_test_user():
        yield test_user

    app.dependency_overrides[user.get_current_user] = override_test_user

    yield

    app.dependency_overrides.clear()


@pytest.fixture
def override_get_test_other_user(test_other_user):
    """結合テスト用に別ユーザログインの依存関係を別のテストユーザーへ差し替える"""

    async def override_test_user():
        yield test_other_user

    app.dependency_overrides[user.get_current_user] = override_test_user

    yield

    app.dependency_overrides.clear()


@pytest.fixture
def test_user():
    """テスト用のユーザー情報"""

    expeted_user = User(
        user_id=uuid.uuid4(),
        user_name="test_user_a",
        email="test@user_a",
        hashed_password="test_a",
        is_active=True,
    )
    return expeted_user


@pytest.fixture
def test_other_user():
    """テスト用のユーザー情報。他のユーザータスクの取得などに使う"""

    expeted_user = User(
        user_id=uuid.uuid4(),
        user_name="test_user_b",
        email="test@user_b",
        hashed_password="test_b",
        is_active=True,
    )
    return expeted_user


@pytest.fixture
def test_task(test_user):
    """テスト用のタスク情報。正規のユーザーが所有する"""

    expeted_task = Task(
        task_id=uuid.uuid4(),
        user_id=test_user.user_id,
        task_name="test_task",
        task_deadline=date(2026, 9, 20),
        task_detail=None,
        changed_time=datetime(2026, 8, 16, tzinfo=timezone.utc),
        task_progress=TaskStatus.IN_PROGRESS,
        progress_ratio=80,
        progress_comment="少し進んだ",
    )
    return expeted_task


@pytest.fixture
def test_subtask(test_task):
    """テスト用のサブタスク情報。正規のユーザー、タスクが所有する"""

    expected_subtask = SubTask(
        subtask_id=uuid.uuid4(),
        task_id=test_task.task_id,
        subtask_name="test_subtask",
        is_complete=False,
        created_at=datetime(2026, 8, 15, tzinfo=timezone.utc),
    )
    return expected_subtask


@pytest_asyncio.fixture
async def connection_test(
    init_test_db, db_session, test_user, test_other_user, test_task, test_subtask, other_task
):
    """結合テスト用にデータを用意"""

    db_session.add(test_user)
    db_session.add(test_other_user)
    db_session.add(test_task)
    db_session.add(test_subtask)
    db_session.add(other_task)

    await db_session.commit()

    yield test_user, test_other_user, test_task, test_subtask, other_task


@pytest.fixture
def subtask():
    """単体テスト用のサブタスクデータ"""

    expected_subtask = SubTask(
        subtask_id=uuid.uuid4(),
        task_id=uuid.uuid4(),
        subtask_name="test_subtask",
        is_complete=False,
        created_at=datetime(2026, 8, 15),
    )
    return expected_subtask


@pytest.fixture
def subtask_list():
    """単体テスト用のサブタスクリストデータ"""

    subtask_id1 = uuid.uuid4()
    subtask_id2 = uuid.uuid4()
    task_id = uuid.uuid4()
    expected_subtasks = [
        SubTask(
            subtask_id=subtask_id1,
            task_id=task_id,
            subtask_name="test_subtask1",
            is_complete=True,
            created_at=datetime(2026, 8, 15),
        ),
        SubTask(
            subtask_id=subtask_id2,
            task_id=task_id,
            subtask_name="test_subtask2",
            is_complete=False,
            created_at=datetime(2026, 8, 16),
        ),
    ]
    return expected_subtasks


@pytest.fixture
def subtask_schema():
    """単体テストでのサブタスク追加更新用"""

    expeted_subtask_schema = UpdateAndCreateSubTaskSchema(
        subtask_name="test_subtask2",
        is_complete=True,
    )
    return expeted_subtask_schema


@pytest.fixture
def task(subtask):
    """サブタスクに紐づくタスク情報"""

    expeted_task = Task(
        task_id=subtask.task_id,
        user_id=uuid.uuid4(),
        task_name="test_task",
        task_deadline=date(2026, 9, 20),
        task_detail=None,
        changed_time=datetime(2026, 8, 16, tzinfo=timezone.utc),
        task_progress=TaskStatus.IN_PROGRESS,
        progress_ratio=80,
        progress_comment="少し進んだ",
    )
    return expeted_task


@pytest.fixture
def other_task(test_user):
    """正規ユーザーが所有するサブタスクと紐づいていない他のタスク"""

    expeted_task = Task(
        task_id=uuid.uuid4(),
        user_id=test_user.user_id,
        task_name="test_task",
        task_deadline=date(2026, 9, 19),
        task_detail=None,
        changed_time=datetime(2026, 8, 16, tzinfo=timezone.utc),
        task_progress=TaskStatus.TODO,
        progress_ratio=10,
        progress_comment="少し進んだ",
    )
    return expeted_task

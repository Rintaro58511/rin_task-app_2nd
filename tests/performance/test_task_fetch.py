import random
import uuid
from datetime import date, datetime, timezone

import pytest
from sqlalchemy import text

from enums import TaskStatus
from models.tasks import Task
from models.user import User


@pytest.mark.asyncio
async def test_task_search_performance(init_test_db, db_session):

    tasks = []
    users = []
    target_user_id = 0

    TASK_COUNT = 100
    USER_COUNT = 1000
    TARGET_USER_COUNT = random.randrange(1000)

    for i in range(USER_COUNT):
        user_id = uuid.uuid4()

        user = User(
            user_id = user_id,
            user_name = f"test_user-{i}",
            email = f"example{i}@gmail.com",
            hashed_password = f"test_pass{i}",
            is_active = True
        )
        users.append(user)
        if i == TARGET_USER_COUNT:
            target_user_id = user_id
        for j in range(TASK_COUNT):
            tasks.append(
                Task(
                    task_id = uuid.uuid4(),
                    user_id = user_id,
                    task_name = f"test_task-{i}{j}",
                    task_deadline = date(2026, 9, 20),
                    task_detail = None,
                    changed_time = datetime(2026, 8, 16, tzinfo=timezone.utc),
                    task_progress = TaskStatus.IN_PROGRESS,
                    progress_ratio = 80,
                    progress_comment = "少し進んだ"
                )
            )
    db_session.add_all(users)
    await db_session.commit()

    db_session.add_all(tasks)
    await db_session.commit()

    result = await db_session.execute(
        text("""
            EXPLAIN ANALYZE
            SELECT *
            FROM tasks
            WHERE user_id = :user_id;
        """),
        {
            "user_id": target_user_id
        }
    )

    rows = result.fetchall()

    for row in rows:
        print(row[0])
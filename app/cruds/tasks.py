from schemas.tasks import UpdateAndCreateTaskSchema
from models.tasks import Task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, case
from uuid import UUID


async def fetch_task(task_id: UUID, db_session: AsyncSession) -> Task:
    """
    タスク情報をタスクのIDを元にデータベースから探す

    Args
        task_id(UUID): 探したいタスクのID
        db_session(AsyncSession): データベースの接続動作の依存性注入

    Return
        Task: 探したいタスクの情報

    """
    result = await db_session.execute(select(Task).filter(Task.task_id == task_id))
    target_task = result.scalars().first()

    return target_task


async def fetch_tasks(user_id: UUID, db_session: AsyncSession) -> list[Task]:
    """
    ユーザーが持っている全てのタスク情報をデータベースから探す

    Args
        user_id(UUID): ログイン中のユーザーのID
        db_session(AsyncSession): データベースの接続動作の依存性注入

    Return
        list[Task]: ユーザーが所有するタスクリスト

    """
    results = await db_session.execute(select(Task).where(Task.user_id == user_id))
    target_tasks = results.scalars().all()

    return target_tasks


async def add_task(
    task: UpdateAndCreateTaskSchema, user_id: UUID, db_session: AsyncSession
) -> None:
    """
    データベースにタスクを追加する

    Args
        task(UpdateAndCreateTaskSchema): タスク追加フォームに入力された内容
        user_id(UUID): ログイン中のユーザーのID
        db_session(AsyncSession): データベースの接続動作の依存性注入

    """
    new_task = Task(
        task_name=task.task_name,
        task_deadline=task.task_deadline,
        task_detail=task.task_detail,
        changed_time=task.changed_time,
        user_id=user_id,
        task_progress=task.task_status.task_progress,
        progress_ratio=task.task_status.progress_ratio,
        progress_comment=task.task_status.progress_comment,
    )

    db_session.add(new_task)
    await db_session.commit()
    await db_session.refresh(new_task)


async def remove_task(task_id: UUID, db_session: AsyncSession) -> None:
    """
    引数のタスクIDと一致したタスクを削除する

    Args
        task_id(UUID): 削除したいタスクのID
        db_session(AsyncSession): データベースの接続動作の依存性注入

    """
    target_task = await fetch_task(task_id, db_session)

    if target_task:
        await db_session.delete(target_task)
        await db_session.commit()


async def modify_task(
    task: UpdateAndCreateTaskSchema, target_task: Task, db_session: AsyncSession
) -> Task:
    """
    データベースのタスク情報を更新する

    Args
        task(UpdateAndCreateTaskSchema): タスク変更フォームに入力された内容
        target_task(Task): 変更したいタスクの情報
        db_session(AsyncSession): データベースの接続動作の依存性注入

    Return
        Task: 変更後のタスクの内容

    """

    target_task.task_name = task.task_name
    target_task.task_deadline = task.task_deadline
    target_task.task_detail = task.task_detail
    target_task.changed_time = task.changed_time
    target_task.task_progress = task.task_status.task_progress
    target_task.progress_ratio = task.task_status.progress_ratio
    target_task.progress_comment = task.task_status.progress_comment

    await db_session.commit()
    await db_session.refresh(target_task)

    return target_task


async def arrange_tasks(
    sort_order: str, user_id: UUID, db_session: AsyncSession
) -> list[Task]:
    """
    sort_orderに応じてタスクを並び替える

    Args
        sort_order(str): ソートの方式
        user_id(UUID): ログイン中のユーザーのID
        db_session(AsyncSession): データベースの接続動作の依存性注入

    Return
        list[Task]: 並び替えたタスクのリスト

    """
    stmt = select(Task).where(Task.user_id == user_id)

    if sort_order == "deadline":
        stmt = stmt.order_by(Task.task_deadline.asc(), Task.task_progress.asc())
    if sort_order == "status":
        status_order = case(
            (Task.task_progress == "TODO", 1),
            (Task.task_progress == "IN_PROGRESS", 2),
            (Task.task_progress == "DONE", 3),
            else_=4,
        )
        stmt = stmt.order_by(status_order, Task.task_deadline.asc())

    result = await db_session.execute(stmt)
    return list(result.scalars().all())


async def filter_tasks(
    search_name: str, user_id: UUID, db_session: AsyncSession
) -> list[Task]:
    """
    タスクの検索結果に応じてタスクを絞り込む

    Args
        search_name(str): 検索ワード
        user_id(UUID): ログイン中のユーザーのID
        db_session(AsyncSession): データベースの接続動作の依存性注入

    Return
        list[Task]: 検索ワードで絞ったタスクのリスト

    """
    stmt = select(Task).where(
        Task.user_id == user_id, Task.task_name.like(f"%{search_name}%")
    )

    result = await db_session.execute(stmt)

    return list(result.scalars().all())

from schemas.subtasks import UpdateAndCreateSubTaskSchema
from models.subtasks import SubTask
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID


async def fetch_subtask(subtask_id: UUID, db_session: AsyncSession) -> SubTask | None:
    """
    サブタスク情報をサブタスクのIDを元にデータベースから探す

    Args
        subtask_id(UUID): 探したいサブタスクのID
        db_session(AsyncSession): データベースの接続動作の依存性注入

    Return
        SubTask: 探したいタスクの情報

    """
    result = await db_session.execute(select(SubTask).filter(SubTask.subtask_id == subtask_id))
    target_subtask = result.scalars().first()

    return target_subtask


async def fetch_subtasks(task_id: UUID, db_session: AsyncSession) -> list[SubTask]:
    """
    タスクが持っている全てのサブタスク情報をデータベースから探す

    Args
        task_id(UUID): 親タスクのID
        db_session(AsyncSession): データベースの接続動作の依存性注入

    Return
        list[SubTask]: ユーザーが所有するサブタスクリスト

    """

    results = await db_session.execute(select(SubTask).where(SubTask.task_id == task_id))
    target_subtasks = results.scalars().all()

    return target_subtasks


async def add_subtask(
    subtask: UpdateAndCreateSubTaskSchema, task_id: UUID, db_session: AsyncSession
) -> None:
    """
    データベースにサブタスクを追加する

    Args
        subtask(UpdateAndCreateSubTaskSchema): サブタスク追加フォームに入力された内容
        task_id(UUID): 親タスクのID
        db_session(AsyncSession): データベースの接続動作の依存性注入

    """
    new_subtask = SubTask(
        task_id=task_id,
        subtask_name=subtask.subtask_name,
        is_complete=subtask.is_complete,
    )

    db_session.add(new_subtask)


async def remove_subtask(subtask_id: UUID, db_session: AsyncSession) -> SubTask | None:
    """
    引数のタスクIDと一致したタスクを削除する

    Args
        subtask_id(UUID): 削除したいタスクのID
        db_session(AsyncSession): データベースの接続動作の依存性注入

    """
    target_subtask = await fetch_subtask(subtask_id, db_session)

    if target_subtask is None:
        return None

    await db_session.delete(target_subtask)
    return target_subtask


async def modify_subtask(
    subtask: UpdateAndCreateSubTaskSchema, target_subtask: SubTask
) -> SubTask:
    """
    データベースのサブタスク情報を更新する

    Args
        subtask(UpdateAndCreateSubTaskSchema): サブタスク変更フォームに入力された内容
        target_subtask(SubTask): 変更したいサブタスクの情報
        db_session(AsyncSession): データベースの接続動作の依存性注入

    Return
        SubTask: 変更後のタスクの内容

    """

    target_subtask.subtask_name = subtask.subtask_name
    target_subtask.is_complete = subtask.is_complete

    return target_subtask

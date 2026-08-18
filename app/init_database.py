import asyncio
from db import Base, async_engine
from models.user import User
from models.tasks import Task
from models.subtasks import SubTask

engine = async_engine

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_db())

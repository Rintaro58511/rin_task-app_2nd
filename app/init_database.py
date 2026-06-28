from sqlalchemy.ext.asyncio import create_async_engine
from models.user import Base
import asyncio

ASYNC_DB_URL = "postgresql+asyncpg://postgres:password123@db:5432/task_db"

engine = create_async_engine(ASYNC_DB_URL, echo=True)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_db())

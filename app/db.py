from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

ASYNC_DB_URL = "postgresql+asyncpg://postgres:password123@db:5432/task_db"

async_engine = create_async_engine(ASYNC_DB_URL, echo=True)

async_session = async_sessionmaker(async_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db_session():
    async with async_session() as session:
        yield session

import asyncio

from db import async_session
from service.emails import send_deadline_notifications


async def main():

    async with async_session() as session:
        await send_deadline_notifications(session)


if __name__ == "__main__":
    asyncio.run(main())

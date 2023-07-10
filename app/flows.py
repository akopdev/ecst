import asyncio

from prefect import flow, get_run_logger

from .tasks import fetch, save
from .database import storage


@flow(
    name="Fetch upcomming events",
    description="Fetch future event",
    retries=3,
    retry_delay_seconds=5 * 60,
)
async def upcoming():
    events = await fetch()
    if events:
        for event in events:
            await save(storage, event)


if __name__ == "__main__":
    asyncio.run(upcoming())

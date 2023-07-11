import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .database import storage
from . import api

scheduler = AsyncIOScheduler()


@scheduler.scheduled_job("interval", seconds=5)
async def upcoming():
    """Fetch upcoming events from remote server"""
    events = await api.fetch()
    if events:
        for event in events:
            await api.save(storage, event)


scheduler.start()

if __name__ == "__main__":
    asyncio.get_event_loop().run_forever()

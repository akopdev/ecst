import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from . import api
from .database import storage

scheduler = AsyncIOScheduler()


# @scheduler.scheduled_job("cron", day_of_week="mon-fri", hour=9)
@scheduler.scheduled_job("interval", seconds=10)
async def upcoming():
    """Fetch upcoming events from remote server"""
    events = await api.fetch()
    if events:
        for event in events:
            if not await api.save(storage, event):
                print("failed to save event")
                print(event)


@scheduler.scheduled_job("interval", seconds=10)
async def update():
    """Update actual value for passed indicators"""
    pending = await api.get_date_ranges(storage)


scheduler.start()

if __name__ == "__main__":
    asyncio.get_event_loop().run_forever()

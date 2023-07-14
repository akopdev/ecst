from . import api
from .database import connect
from .logger import log


async def upcoming():
    """Fetch upcoming events from remote server"""
    events = await api.fetch()
    if events:
        db = connect()
        for event in events:
            is_updated = await api.save(db, event)
            if not is_updated:
                log.error("Failed to store data in database.")


async def update():
    """Update actual value for passed indicators"""
    db = connect()
    date_range = await api.get_date_ranges(db)
    log.info(date_range)
    if date_range:
        events = await api.fetch(**date_range)
        log.info(events)


if __name__ == "__main__":
    import asyncio

    # asyncio.run(upcoming())
    asyncio.run(update())

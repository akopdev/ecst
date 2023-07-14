from . import api
from .database import connect
from .logger import log


async def upcoming():
    """Fetch upcoming events from remote server"""
    await api.fetch(connect())

async def update():
    """Update actual value for passed indicators"""
    db = connect()
    date_range = await api.get_date_ranges(db)
    if date_range:
        await api.fetch(db=db, **date_range)
    else:
        log.info("Nothing to update")


if __name__ == "__main__":
    import asyncio

    # asyncio.run(upcoming())
    asyncio.run(update())

import sys

from .schemas import Settings
from .storages import Storage


def format(data, dump_as: str = "text"):
    dump = {
        "csv": data.model_dump_csv,
        "json": data.model_dump_json,
        "text": data.model_dump_text,
    }[dump_as]
    print(dump())


async def query_indicators(settings: Settings):
    """Query data from storage for given range of dates."""
    try:
        storage = Storage(settings.storage)
        await storage.connect()
        result = await storage.query(
            date_start=settings.date_start,
            date_end=settings.date_end,
        )
        format(result, settings.format)
    except Exception as e:
        sys.exit(e)


async def list_indicators(settings: Settings):
    """List available indicators."""
    try:
        storage = Storage(settings.storage)
        await storage.connect()
        result = await storage.list()
        format(result, settings.format)
    except Exception as e:
        sys.exit(e)

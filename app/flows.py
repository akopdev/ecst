from datetime import datetime
from functools import wraps

from motor.frameworks.asyncio import asyncio
from typer import Option, Typer
from typing_extensions import Annotated

from .logger import log
from .provider import DataProvider

app = Typer(no_args_is_help=True)


def flow(f):
    @app.command()
    @wraps(f)
    def wrapper(*args, **kwargs):
        log.info(f"Start `{f.__name__}` job")
        res = asyncio.run(f(*args, **kwargs))
        log.info(f"Job `{f.__name__}` completed successfully")
        return res

    return wrapper


@flow
async def upcoming(
    dsn: Annotated[str, Option()],
):
    """Fetch upcoming events from remote server"""
    provider = DataProvider(dsn)
    await provider.etl()


@flow
async def indicators(
    dsn: Annotated[str, Option()],
):
    """Update actual value for passed events"""
    provider = DataProvider(dsn)
    date_range = await provider.get_date_ranges()
    if date_range:
        await provider.etl(**date_range)
    else:
        log.info("Nothing to update")

from functools import wraps

from motor.frameworks.asyncio import asyncio
from typer import Option, Typer
from typing_extensions import Annotated

from . import api
from .database import connect
from .logger import log

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
    await api.fetch(connect(dsn))


@flow
async def indicators(
    dsn: Annotated[str, Option()],
):
    """Update actual value for passed events"""
    db = connect(dsn)
    date_range = await api.get_date_ranges(db)
    if date_range:
        await api.fetch(db=db, **date_range)
    else:
        log.info("Nothing to update")

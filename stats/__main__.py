import argparse
import asyncio
import os
import sys

from pydantic import ValidationError

from .providers import DataProvider
from .schemas import Settings
from . import __version__
import tempfile


async def main(settings: Settings):
    try:
        provider = DataProvider(settings.storage)
        await provider.etl(
            date_start=settings.date_start,
            date_end=settings.date_end,
        )
    except Exception as e:
        sys.exit(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Economic indicators")
    parser.add_argument(
        "--storage",
        help="Specify DSN string to connect external data storage. "
        "Support environment variable `STORAGE`",
        default=os.environ.get("STORAGE") or f"montydb://{tempfile.gettempdir()}/stats",
    )
    parser.add_argument(
        "--date-start",
        help="Fetch events starting from this date (2023-01-19, 2023-01-19T10:30:00)",
    )
    parser.add_argument(
        "--date-end",
        help="Fetch data till provided date (ex 2023-01-19, 2023-01-19T10:30:00)",
    )
    parser.add_argument("--days", help="Calculate date range based on number of days", type=int)
    parser.add_argument(
        "--version", help="Print current version and exit", action="version", version=__version__
    )

    try:
        args = parser.parse_args()
        settings = Settings(**vars(args))
    except ValidationError as e:
        sys.exit(e.errors(include_url=False, include_context=False)[0].get("msg"))

    asyncio.run(main(settings))

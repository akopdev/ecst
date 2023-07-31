import argparse
import asyncio
import os
import sys
import tempfile

from pydantic import ValidationError

from . import __version__
from .schemas import Settings
from .storages import Storage


async def main(settings: Settings):
    try:
        storage = Storage(settings.storage)
        await storage.connect()
        events = await storage.query(
            date_start=settings.date_start,
            date_end=settings.date_end,
        )

        format = {"csv": events.csv, "json": events.json, "text": events.text}[settings.format]
        print(format())
    except Exception as e:
        sys.exit(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Economic indicators",
        argument_default=argparse.SUPPRESS
    )
    parser.add_argument(
        "--storage",
        help="Specify DSN string to connect to external data storage. "
        "Support environment variable `STATS_STORAGE`",
        # default=os.environ.get("STATS_STORAGE"),
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
    parser.add_argument("--format", help="Output format (csv, json, text)")
    parser.add_argument(
        "--version", help="Print current version and exit", action="version", version=__version__
    )

    try:
        args = parser.parse_args()
        settings = Settings(**vars(args))
    except ValidationError as e:
        error = e.errors(include_url=False, include_context=False)[0]
        sys.exit(
            "Wrong argument value passed ({}): {}".format(
                error.get("loc", ("system",))[0], error.get("msg")
            )
        )

    asyncio.run(main(settings))

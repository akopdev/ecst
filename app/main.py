import argparse
import asyncio
import os
import sys

from pydantic import ValidationError

from .providers import DataProvider
from .schemas import Settings


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
    parser = argparse.ArgumentParser(
        description="Load actual values for all indicators from data provider"
    )
    parser.add_argument(
        "storage",
        help="Specify DSN string to connect data storage",
        default=os.environ.get("STORAGE"),
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

    try:
        args = parser.parse_args()
        settings = Settings(**vars(args))
    except ValidationError as e:
        sys.exit(e.errors(include_url=False, include_context=False)[0].get("msg"))

    asyncio.run(main(settings))

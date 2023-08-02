import argparse
import asyncio
import os
import sys

from pydantic import ValidationError

from . import __version__
from .commands import list_indicators, query_indicators
from .schemas import Settings


def main():
    parser = argparse.ArgumentParser(
        description="Economic indicators", argument_default=argparse.SUPPRESS
    )
    # Global arguments
    parser.add_argument(
        "--storage",
        help="Database connection string. "
        "Support environment variable `STATS_STORAGE`",
        # default=os.environ.get("STATS_STORAGE"),
    )
    parser.add_argument(
        "--version",
        help="Print version information and quite",
        action="version",
        version=__version__,
    )
    parser.add_argument("--format", help="Output format (csv, json, text)")

    # Commands
    commands = parser.add_subparsers(title="Commands", dest="command")

    # Query command
    query_parser = commands.add_parser("query", help="Get indicator data for specified date range", argument_default=argparse.SUPPRESS)
    query_parser.add_argument(
        "--date-start",
        help="Fetch data starting from this date (2023-01-19, 2023-01-19T10:30:00)",
    )
    query_parser.add_argument(
        "--date-end",
        help="Fetch data till provided date (ex 2023-01-19, 2023-01-19T10:30:00)",
    )
    query_parser.add_argument(
        "--days", help="Calculate date range based on number of days", type=int
    )
    query_parser.add_argument(
        "--countries", help="Fetch data related to particular countries", type=str
    )

    query_parser.set_defaults(func=query_indicators)

    # List command
    list_parser = commands.add_parser("list", help="List pre-fetched indicators", argument_default=argparse.SUPPRESS)
    list_parser.set_defaults(func=list_indicators)

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

    if args.command:
        asyncio.run(args.func(settings))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

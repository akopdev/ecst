import argparse
import asyncio

from .api.providers import DataProvider

parser = argparse.ArgumentParser(description="Fetch upcoming events from remote server")
parser.add_argument("DB_DSN", help="DSN string to connect data storage")
args = parser.parse_args()

provider = DataProvider(args.DB_DSN)

asyncio.run(provider.etl())

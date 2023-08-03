from datetime import datetime
from typing import List

import pytest
import pytest_asyncio

from stats.models import Indicator, IndicatorData
from stats.storages import Storage


@pytest.fixture(scope="session")
def dsn() -> str:
    return "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture()
async def storage(dsn: str):
    storage = Storage(dsn)
    await storage.connect()
    return storage


@pytest_asyncio.fixture()
async def populate_db(storage) -> List[Indicator]:
    # create a set of indicators in the database
    indicators = [
        Indicator(
            country="AU",
            indicator="Core Inflation Rate",
            title="Core Inflation Rate",
            ticker="AUCIR",
            currency="AUD",
            unit="%",
            data=[
                IndicatorData(
                    ticker="AUCIR", date=datetime(2023, 7, 26, 1, 30), actual=5.9, forecast=6
                ),
                IndicatorData(
                    ticker="AUCIR", date=datetime(2023, 7, 26, 18, 30), actual=6.6, forecast=6
                ),
            ],
        ),
        Indicator(
            country="US",
            indicator="Mortgage Applications",
            title="Core Inflation Rate",
            ticker="USMAPL",
            currency="USD",
            unit="%",
            data=[
                IndicatorData(
                    ticker="USMAPL", date=datetime(2023, 7, 26, 1, 30), actual=1.1, forecast=None
                )
            ],
        ),
    ]
    async with storage.session() as session:
        async with session.begin():
            session.add_all(indicators)
    return indicators

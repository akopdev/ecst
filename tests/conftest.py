from typing import List

import pytest
import pytest_asyncio

from stats.models import Indicator, IndicatorData
from stats.storages import Storage


@pytest.fixture(scope="session")
def dsn():
    return "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture()
async def populate_db(dsn) -> List[Indicator]:
    # create a set of indicators in the database
    indicators = [
        Indicator(
            country="AU",
            indicator="Core Inflation Rate",
            ticker="AUCIR",
            currency="AUD",
            unit="%",
            data=[
                IndicatorData(date="2023-07-26T01:30:00.000Z", actual=5.9, forecast=6),
                IndicatorData(date="2023-07-26T01:30:00.000Z", actual=6.6, forecast=6),
            ],
        ),
        Indicator(
            country="US",
            indicator="Mortgage Applications",
            ticker="USMAPL",
            currency="USD",
            unit="%",
            data=[IndicatorData(date="2023-07-26T11:00:00.000Z", actual=1.1, forecast=None)],
        ),
    ]
    storage = Storage(dsn)
    await storage.connect()
    async with storage.session() as session:
        async with session.begin():
            session.add_all(indicators)
    return indicators

import re
from datetime import datetime
from typing import Dict, List, Tuple

import pytest
from aioresponses import aioresponses

from stats.schemas import Event
from stats.storages import Storage

sample_event = {
    "id": "324884",
    "title": "RBA Trimmed Mean CPI YoY",
    "country": "AU",
    "indicator": "Core Inflation Rate",
    "ticker": "AUCIR",
    "comment": "In Australia, the Trimmed mean is calculated as the weighted mean ...",
    "period": "Q2",
    "source": "Bureau of Statistics",
    "actual": 5.9,
    "previous": 6.6,
    "forecast": 6,
    "currency": "AUD",
    "unit": "%",
    "importance": -1,
    "date": "2023-07-26T01:30:00.000Z",
}

sample_dates_to_sync = [
    (
        (datetime(2023, 7, 24, 1, 30), datetime(2023, 7, 24, 18, 30)),
        [(datetime(2023, 7, 24, 1, 30), datetime(2023, 7, 24, 18, 30))],
    ),
    (
        (datetime(2023, 7, 24, 2), datetime(2023, 7, 28, 1, 30)),
        [
            (datetime(2023, 7, 24, 2, 0), datetime(2023, 7, 26, 1, 30)),
            (datetime(2023, 7, 26, 18, 30), datetime(2023, 7, 28, 1, 30)),
        ],
    ),
]


@pytest.mark.asyncio()
async def test_transform_event_to_indicator(storage: Storage):
    """
    Test if `transform` method is returning an Indicator object
    """
    event = Event(**sample_event)
    indicators = await storage.transform([event])
    assert indicators.meta["AUCIR"].country == "AU"
    assert (
        indicators.data[
            (
                "AUCIR",
                datetime(2023, 7, 26, 1, 30),
            )
        ].actual
        == 5.9
    )


@pytest.mark.parametrize("dates, expected", sample_dates_to_sync)
@pytest.mark.asyncio()
async def test_dates_to_sync(
    dates: Tuple[datetime, datetime],
    expected: List[Tuple[datetime, datetime]],
    storage: Storage,
    populate_db: Dict,
):
    """date_to_sync should return a list of tuples that contains range of dates to sync"""
    result = await storage.dates_to_sync(dates[0], dates[1])
    assert result == expected


@pytest.mark.asyncio()
async def test_sync_and_list(storage: Storage):
    """sync should add new data to the database, and list extract it"""
    with aioresponses() as m:
        pattern = re.compile(r"^https://economic-calendar\.tradingview\.com/events\?.*")
        m.get(
            pattern,
            payload={"status": "ok", "result": [sample_event]},
            status=200,
        )
        await storage.sync(datetime(2023, 7, 24, 2), datetime(2023, 7, 26, 1, 30))

        results = await storage.list()
        assert len(results.data) == 1
        assert results.data[0].ticker == "AUCIR"

        results = await storage.list(countries=["US"])
        assert len(results.data) == 0

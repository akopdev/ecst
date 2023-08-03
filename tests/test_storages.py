from datetime import datetime
from typing import Dict, List, Tuple

import pytest

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
        [(datetime(2023, 7, 24, 2, 0), datetime(2023, 7, 26, 1, 30)), (datetime(2023, 7, 26, 18, 30), datetime(2023, 7, 28, 1, 30))],
    )
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

    print("dates", dates)
    print("result", result)
    assert result == expected

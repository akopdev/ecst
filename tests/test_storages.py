from datetime import datetime

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


@pytest.mark.asyncio()
async def test_transform_event_to_indicator(dsn: str):
    """
    Test if `transform` method is returning an Indicator object
    """
    event = Event(**sample_event)
    storage = Storage(dsn)
    await storage.connect()
    indicators = await storage.transform([event])
    assert indicators.meta["AUCIR"].country == "AU"
    assert indicators.data[("AUCIR", datetime(2023, 7, 26, 1, 30),)].actual == 5.9

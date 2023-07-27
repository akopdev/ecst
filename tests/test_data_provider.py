import re
from datetime import datetime

import pytest
from aioresponses import aioresponses

from stats.providers import DataProvider
from stats.schemas import Event


@pytest.fixture()
def tradingview_sample_response():
    return {
        "status": "ok",
        "result": [
            {
                "id": "313746",
                "title": "MBA Mortgage Applications",
                "country": "US",
                "indicator": "Mortgage Applications",
                "ticker": "USMAPL",
                "comment": "In the US, the MBA Weekly Mortgage Application Survey is a  ...",
                "period": "Jul/21",
                "source": "Mortgage Bankers Association of America",
                "actual": None,
                "previous": 1.1,
                "forecast": None,
                "currency": "USD",
                "unit": "%",
                "importance": -1,
                "date": "2023-07-26T11:00:00.000Z",
            },
            {
                "id": "313747",
                "title": "MBA Mortgage Refinance Index",
                "country": "US",
                "indicator": "MBA Mortgage Refinance Index",
                "ticker": "USMRI",
                "comment": "The MBA Weekly Mortgage Application Survey is a comprehensive...",
                "period": "Jul/21",
                "source": "Mortgage Bankers Association of America",
                "actual": None,
                "previous": 446.4,
                "forecast": None,
                "currency": "USD",
                "importance": -1,
                "date": "2023-07-26T11:00:00.000Z",
            },
            {
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
            },
        ],
    }


@pytest.mark.asyncio()
async def test_data_provider_is_matching_event_schema(tradingview_sample_response: dict):
    """
    Test if `extract` method is returning a list of Event objects
    """
    provider = DataProvider("mongodb://localhost:27017/fake")
    date = datetime.today()

    with aioresponses() as m:
        pattern = re.compile(r"^https://economic-calendar\.tradingview\.com/events\?.*")
        m.get(
            pattern,
            payload=tradingview_sample_response,
            status=200,
        )
        events = await provider.extract(date, date)
        assert len(events) == 3
        assert all([isinstance(event, Event) for event in events])


@pytest.mark.asyncio()
async def test_data_provider_validation_fail(tradingview_sample_response: dict):
    """
    Test if `extract` method is returning False if validation fails
    """
    tradingview_sample_response["result"][0]["actual"] = "invalid"

    provider = DataProvider("mongodb://localhost:27017/fake")
    date = datetime.utcnow()
    with aioresponses() as m:
        pattern = re.compile(r"^https://economic-calendar\.tradingview\.com/events\?.*")
        m.get(
            pattern,
            payload=tradingview_sample_response,
            status=200,
        )
        events = await provider.extract(date, date)
        assert not events


@pytest.mark.asyncio()
def test_data_provider_transform_event_to_indicator(tradingview_sample_response: dict):
    """
    Test if `transform` method is returning an Indicator object
    """
    event = Event(**tradingview_sample_response["result"][2])
    provider = DataProvider("mongodb://localhost:27017/fake")
    indicator = provider.transform(event)
    assert indicator.country.value == "AU"
    assert indicator.data.actual.value == 5.9

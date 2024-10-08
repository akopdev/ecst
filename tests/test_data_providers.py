import re
from datetime import datetime

import pytest
from aioresponses import aioresponses
from ecst.providers import DataProvider

from ecst.schemas import Event



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
    provider = DataProvider()
    date = datetime.today()

    with aioresponses() as m:
        pattern = re.compile(r"^https://economic-calendar\.tradingview\.com/events\?.*")
        m.get(
            pattern,
            payload=tradingview_sample_response,
            status=200,
        )
        events = await provider.fetch(date, date)
        assert len(events) == 3
        assert all([isinstance(event, Event) for event in events])


@pytest.mark.asyncio()
async def test_data_provider_validation_fail(tradingview_sample_response: dict):
    """
    Test if `extract` method is returning False if validation fails
    """
    tradingview_sample_response["result"][0]["actual"] = "invalid"

    provider = DataProvider()

    date = datetime.today()
    with aioresponses() as m:
        pattern = re.compile(r"^https://economic-calendar\.tradingview\.com/events\?.*")
        m.get(
            pattern,
            payload=tradingview_sample_response,
            status=200,
        )
        events = await provider.fetch(date, date)
        assert not events



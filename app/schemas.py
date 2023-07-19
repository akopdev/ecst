from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, validator

from .enums import Country, Currency


class IndicatorDataTS(BaseModel):
    """Store data as a pair of timeseries"""

    date: datetime
    value: Optional[float] = None


class IndicatorData(BaseModel):
    """Store data as a pair of timeseries"""

    # actual data should always be present otherwise store it as a future event
    actual: IndicatorDataTS
    # there might not be consensus forcast for this indicator
    forcast: Optional[IndicatorDataTS] = None


class Indicator(BaseModel):
    """
    Schema for indicators to store and extract from database
    """

    data: Optional[IndicatorData] = []
    comment: Optional[str] = None
    country: Country
    currency: Currency
    indicator: str
    period: Optional[str] = None
    scale: Optional[str] = None
    source: str
    ticker: Optional[str] = None
    title: str
    unit: Optional[str] = None


class Event(BaseModel):
    """
    Schema that represents structure of event from TradingView API
    """

    actual: Optional[float] = None
    comment: Optional[str] = None
    country: Country
    currency: Currency
    date: datetime
    forecast: Optional[float] = None
    indicator: str
    period: Optional[str] = None
    scale: Optional[str] = None
    source: str
    ticker: Optional[str] = None
    title: str
    unit: Optional[str] = None

    @validator("date", pre=True, always=True)
    def fix_date(cls, v):
        return datetime.fromisoformat(v.replace("Z", "+00:00"))


class DataProviderResult(BaseModel):
    status: str
    result: Optional[List[Event]] = None

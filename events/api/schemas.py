from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, validator

from .enums import Country, Currency, Period


class IndicatorDataTS(BaseModel):
    """Store data as a pair of timeseries"""

    date: datetime
    value: Optional[float] = None


class IndicatorData(BaseModel):
    # actual data should always be present otherwise store it as a upcoming event
    actual: IndicatorDataTS
    # there might not be consensus forcast for the indicator
    forcast: Optional[IndicatorDataTS] = None


class Indicator(BaseModel):
    """
    Indicator to store in database
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
    TradingView API Event

    May contain events without actual and forecast values.
    """

    actual: Optional[float] = None
    comment: Optional[str] = None
    country: Country
    currency: Currency
    date: datetime
    forecast: Optional[float] = None
    indicator: str
    period: Optional[Period] = None
    scale: Optional[str] = None
    source: str
    ticker: str
    title: str
    unit: Optional[str] = None

    @validator("date", pre=True, always=True)
    def fix_date(cls, v):
        return datetime.fromisoformat(v.replace("Z", "+00:00"))

    @validator("period", pre=True, always=True)
    def fix_period(cls, v):
        return v if v in ["Q1", "Q2", "Q3", "Q4"] else "".join(filter(str.isalpha, v or "")) or None


class DataProviderResult(BaseModel):
    """TradingView API response"""
    status: str
    result: Optional[List[Event]] = None

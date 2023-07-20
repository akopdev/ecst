from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, MongoDsn, validator

from .enums import Country, Currency, Period


class Settings(BaseModel):
    """Validates CLI arguments"""

    storage: MongoDsn
    date_start: Optional[datetime] = None
    date_end: Optional[datetime] = None
    days: Optional[int] = None

    @validator("date_start", "date_end", pre=True)
    def parse_date(cls, value: datetime) -> datetime:
        """Parse date from string"""
        try:
            if isinstance(value, str):
                v = datetime.strptime(value, "%Y-%m-%d")
                # convert date to datetime
                return datetime.combine(v, datetime.min.time())
        except ValueError:
            return value
        return value

    @validator("days", always=True)
    def parse_days(cls, value: int, values: dict) -> int:
        """If days is specified, calculate date_start and date_end.

        If days is a positive number, then set date range to future, otherwise to past.
        """
        if value is not None:
            if value > 0:
                values["date_start"] = values.get("date_start", datetime.utcnow())
                values["date_end"] = values["date_start"] + timedelta(days=value)
            else:
                values["date_end"] = values.get("date_end", datetime.utcnow())
                values["date_start"] = values["date_end"] - timedelta(days=value * -1)
        return values

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

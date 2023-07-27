from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel, FieldValidationInfo, MongoDsn, field_validator

from .enums import Country, Currency, Period


class Settings(BaseModel):
    """Validates CLI arguments."""

    storage: MongoDsn
    date_start: Optional[datetime] = None
    date_end: Optional[datetime] = None
    days: Optional[int] = None

    @field_validator("days")
    def parse_days(cls, v: int, values: FieldValidationInfo) -> dict:
        """If days is specified, calculate date_start and date_end.

        If days is a positive number, then set date range to future, otherwise to past.
        If date_start is defined, then calculate date_end based on days.
        If date_end is defined, then calculate date_start based on days.
        If both date_start and date_end are defined, then calculate days.
        """
        if values.data.get("date_start") and values.data.get("date_end"):
            values.data["days"] = (values.data["date_end"] - values.data["date_start"]).days
        elif v is not None:
            if v > 0:
                if values.data.get("date_start"):
                    values.data["date_end"] = values.data["date_start"] + timedelta(days=v)
                elif values.data.get("date_end"):
                    values.data["date_start"] = values.data["date_end"] - timedelta(days=v)
            else:
                if values.data.get("date_start"):
                    values.data["date_end"] = values.data["date_start"] - timedelta(days=v * -1)
                elif values.data.get("date_end"):
                    values.data["date_start"] = values.data["date_end"] - timedelta(days=v * -1)
        return values

    @field_validator("date_start", "date_end", mode="before")
    def parse_date(cls, v: datetime) -> datetime:
        """Parse date from string."""
        try:
            if isinstance(v, str):
                v = datetime.strptime(v, "%Y-%m-%d")
                # convert date to datetime
                return datetime.combine(v, datetime.min.time())
        except ValueError:
            return v
        return v


class IndicatorDataTS(BaseModel):
    """Store data as a pair of timeseries."""

    date: datetime
    value: Optional[float] = None


class IndicatorData(BaseModel):
    # actual data should always be present otherwise store it as a upcoming event
    actual: IndicatorDataTS
    # there might not be consensus forcast for the indicator
    forcast: Optional[IndicatorDataTS] = None


class Indicator(BaseModel):
    """Indicator to store in database."""

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
    TradingView API Event.

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

    @field_validator("date", mode="before")
    def fix_date(cls, v):
        return datetime.fromisoformat(v.replace("Z", "+00:00"))

    @field_validator("period", mode="before")
    def fix_period(cls, v):
        return v if v in ["Q1", "Q2", "Q3", "Q4"] else "".join(filter(str.isalpha, v or "")) or None


class DataProviderResult(BaseModel):
    """TradingView API response."""

    status: str
    result: Optional[List[Event]] = None

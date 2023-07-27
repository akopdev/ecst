from datetime import datetime, timedelta
from typing import Annotated, List, Optional

from pydantic import (BaseModel, MongoDsn, UrlConstraints, field_validator,
                      model_validator)
from pydantic_core import MultiHostUrl

from .enums import Country, Currency, Period

MontyDsn = Annotated[MultiHostUrl, UrlConstraints(allowed_schemes=["montydb"])]


class Settings(BaseModel):
    """Validates CLI arguments."""

    storage: MongoDsn | MontyDsn
    date_start: Optional[datetime] = None
    date_end: Optional[datetime] = None
    days: Optional[int] = None

    @model_validator(mode="after")
    def parse_days(self):
        """If days is specified, calculate date_start and date_end.

        If days is a positive number, then set date range to future, otherwise to past.
        If date_start is defined, then calculate date_end based on days.
        If date_end is defined, then calculate date_start based on days.
        If both date_start and date_end are defined, then calculate days.
        """
        if self.date_start and self.date_end:
            self.days = (self.date_end - self.date_start).days
        elif self.days is not None:
            if self.days > 0:
                if self.date_start:
                    self.date_end = self.date_start + timedelta(days=self.days)
                elif self.date_end:
                    self.date_start = self.date_end - timedelta(days=self.days)
                else:
                    self.date_start = datetime.utcnow()
                    self.date_end = self.date_start + timedelta(days=self.days)
            else:
                if self.date_start:
                    self.date_end = self.date_start - timedelta(days=self.days * -1)
                elif self.date_end:
                    self.date_start = self.date_end - timedelta(days=self.days * -1)
                else:
                    self.date_end = datetime.utcnow()
                    self.date_start = self.date_end - timedelta(days=self.days * -1)

        return self

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
    ticker: Optional[str] = None
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

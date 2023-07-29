from datetime import datetime, timedelta
from typing import Annotated, List, Optional

from pydantic import (BaseModel, Field, FieldValidationInfo, PostgresDsn,
                      UrlConstraints, field_validator, model_validator)
from pydantic_core import MultiHostUrl, Url

from .enums import Country, Currency, Period

SQLiteDsn = Annotated[
    Url,
    UrlConstraints(
        host_required=False,
        allowed_schemes=[
            "sqlite",
            "sqlite3",
        ],
    ),
]


class Settings(BaseModel):
    """Validates CLI arguments."""

    storage: PostgresDsn | str  # TODO: replace str with SQLiteDsn
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
                # todo: don't confuse user with positive/negative days,
                #       just use date_start and date_end to understand direction.
                #       days + date_end will fetch past events, days + date_start - upcoming
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
                return datetime.combine(datetime.strptime(v, "%Y-%m-%d"), datetime.min.time())
        except ValueError:
            return v
        return v


class Event(BaseModel):
    """
    TradingView API Event.

    May contain events without actual and forecast values.
    """

    actual: Optional[float] = None
    country: Country
    currency: Currency
    date: datetime
    forecast: Optional[float] = None
    indicator: str
    period: Optional[Period] = None
    scale: Optional[str] = None
    source: str
    title: str
    ticker: str
    unit: Optional[str] = None

    @model_validator(mode="before")
    def fix_ticker(values: dict):
        # if ticker is not specified, then generate it by combining the first letter of each word in title
        if not values.get("ticker"):
            values["ticker"] = (
                values.get("country")
                + "".join([word[0] for word in values.get("title", "").split()]).upper()
            )
        return values

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

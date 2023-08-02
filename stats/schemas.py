from datetime import datetime, timedelta
from typing import Annotated, Dict, List, Optional, Tuple

from pydantic import (BaseModel, ConfigDict, Field, PostgresDsn,
                      UrlConstraints, field_validator, model_validator)
from pydantic_core import Url

from stats.models import Indicator, IndicatorData

from .enums import Country, Currency, OutputFormat, Period

SQLiteDsn = Annotated[
    Url,
    UrlConstraints(
        host_required=False,
        allowed_schemes=["sqlite", "sqlite3", "sqlite+aiosqlite"],
    ),
]


class Settings(BaseModel):
    """Validates CLI arguments."""

    storage: Optional[PostgresDsn | SQLiteDsn] = Field(default="sqlite+aiosqlite:///stats.db")
    date_start: Optional[datetime] = None
    date_end: Optional[datetime] = None
    days: int = Field(default=1, ge=0)
    format: OutputFormat = Field(default=OutputFormat.TEXT)
    countries: Optional[List[Country]] = []

    @model_validator(mode="before")
    def parse_countries(values: dict):
        """Parse countries from comma separated string."""
        if isinstance(values.get("countries"), str):
            values["countries"] = values.get("countries").split(",")
        return values

    @model_validator(mode="after")
    def parse_days(self):
        """Calculate date ranges based on days and starting point.

        if date_start is set, date_end will be calculated based on date_start + days.
        if date_end is set, date_start will be calculated based on date_end - days.
        If both date_start and date_end are set, days will be calculated based on date_end - date_start.
        If none of them are set, date_end will be set to current date and date_start will be calculated based on date_end - days.
        """
        if self.date_start and self.date_end:
            self.days = (self.date_end - self.date_start).days
            return self

        if self.date_start and self.days:
            self.date_end = self.date_start + timedelta(days=self.days)
        elif self.date_end and self.days:
            self.date_start = self.date_end - timedelta(days=self.days)
        elif not self.date_start and not self.date_end:
            self.date_end = datetime.utcnow()
            self.date_start = self.date_end - timedelta(days=self.days)

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
    source: Optional[str] = None
    title: str
    ticker: str
    unit: Optional[str] = None

    @model_validator(mode="before")
    def fix_ticker(values: dict):
        # if ticker is not specified, then generate it.
        # Take the first letter of each word in a title
        if not values.get("ticker"):
            values["ticker"] = (
                values.get("country")
                + "".join([word[0] for word in values.get("title", "").split()]).upper()
            )
        return values

    @field_validator("period", mode="before")
    def fix_period(cls, v):
        return v if v in ["Q1", "Q2", "Q3", "Q4"] else "".join(filter(str.isalpha, v or "")) or None


class DataProviderResult(BaseModel):
    """TradingView API response."""

    status: str
    result: Optional[List[Event]] = None


class Indicators(BaseModel):
    """
    Container to store indicators and metrics to easy sync with existing records.
    """

    meta: Dict[str, Indicator]
    data: Dict[Tuple[str, datetime], IndicatorData]

    model_config = ConfigDict(arbitrary_types_allowed=True)


class QueryResultData(BaseModel):
    ticker: str = Field(title="Ticker")
    date: datetime = Field(title="Date")
    actual: float = Field(title="Actual")
    forecast: Optional[float] = Field(title="Forecast")

    model_config = ConfigDict(from_attributes=True)


class QueryResult(BaseModel):
    """Result of query command."""

    data: Optional[List[QueryResultData]] = Field(default_factory=list)

    def model_dump_csv(self):
        result = [
            "{},{},{},{}".format(
                QueryResultData.__fields__.get("date").title,
                QueryResultData.__fields__.get("ticker").title,
                QueryResultData.__fields__.get("actual").title,
                QueryResultData.__fields__.get("forecast").title,
            )
        ]

        for row in self.data:
            result.append(f"{row.date},{row.ticker},{row.actual},{row.forecast}")
        return "\n".join(result)

    def model_dump_text(self):
        result = [
            "{:<8}\t{:<8}\t{:<8}\t{}".format(
                QueryResultData.__fields__.get("date").title,
                QueryResultData.__fields__.get("ticker").title,
                QueryResultData.__fields__.get("actual").title,
                QueryResultData.__fields__.get("forecast").title,
            )
        ]
        for row in self.data:
            result.append(
                "{}\t{:<8}\t{:<8}\t{}".format(
                    row.date.strftime("%d/%m %H:%M"), row.ticker, row.actual, row.forecast
                )
            )
        return "\n".join(result)


class ListResultData(BaseModel):
    country: Country = Field(title="Country")
    currency: Currency = Field(title="Currency")
    indicator: str = Field(title="Indicator")
    scale: Optional[str] = Field(title="Scale")
    ticker: str = Field(title="Ticker")
    title: str = Field(title="Title")
    unit: Optional[str] = Field(title="Unit")

    model_config = ConfigDict(from_attributes=True)


class ListResult(BaseModel):
    """Result of list command."""

    data: Optional[List[ListResultData]] = Field(default_factory=list)

    def model_dump_csv(self):
        result = [
            "{},{},{},{},{},{},{}".format(
                ListResultData.__fields__.get("country").title,
                ListResultData.__fields__.get("currency").title,
                ListResultData.__fields__.get("indicator").title,
                ListResultData.__fields__.get("scale").title,
                ListResultData.__fields__.get("ticker").title,
                ListResultData.__fields__.get("title").title,
                ListResultData.__fields__.get("unit").title,
            )
        ]

        for row in self.data:
            result.append(
                "{},{},{},{},{},{},{}".format(
                    row.country,
                    row.currency,
                    row.indicator,
                    row.scale,
                    row.ticker,
                    row.title,
                    row.unit,
                )
            )
        return "\n".join(result)

    def model_dump_text(self):
        result = [
            "{:<8}\t{}\t{:<8}\t{:<34}\t{}".format(
                ListResultData.__fields__.get("ticker").title,
                ListResultData.__fields__.get("country").title,
                ListResultData.__fields__.get("currency").title,
                ListResultData.__fields__.get("title").title,
                ListResultData.__fields__.get("indicator").title,
            )
        ]
        for row in self.data:
            result.append(
                "{:<8}\t{}\t{:<8}\t{:<34}\t{}".format(
                    row.ticker,
                    row.country.value,
                    row.currency.value,
                    row.title,
                    row.indicator,
                )
            )
        return "\n".join(result)

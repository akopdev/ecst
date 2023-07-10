from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator

from .enums import Country, Currency, Importance


class Event(BaseModel):
    actual: Optional[float] = None
    country: Country
    currency: Currency
    date: datetime
    forecast: Optional[float] = None
    id: int
    importance: Importance
    indicator: str
    period: str
    previous: Optional[float] = None
    scale: Optional[str] = None
    source: str
    ticker: Optional[str] = None
    title: str
    unit: Optional[str] = None

    @validator("date")
    def datetime_to_string(cls, v):
        return v.isoformat()

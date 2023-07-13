from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, validator

from .enums import Country, Currency, EventType, Importance


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
    type: EventType = None
    unit: Optional[str] = None

    @validator("date")
    def format_date(cls, v):
        return v.isoformat()

    @validator("type", pre=True, always=True)
    def define_type(cls, v, *, values: Dict[str, Any]):
        return v or (
            EventType.INDICATOR
            if values["previous"] is not None or values["forecast"] is not None
            else EventType.EVENT
        )

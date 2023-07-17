from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, validator

from .enums import Country, Currency, EventType


class IndicatorData(BaseModel):
    actual: Optional[float] = None
    date: datetime
    forecast: Optional[float] = None
    period: Optional[str] = None


class Indicator(BaseModel):
    title: str
    country: Country
    ticker: Optional[str] = None
    data: Optional[List[IndicatorData]] = None
    indicator: str
    currency: Currency
    unit: Optional[str] = None


class Event(Indicator, IndicatorData):
    scale: Optional[str] = None
    comment: Optional[str] = None
    source: str
    type: EventType = None

    @validator("date", pre=True, always=True)
    def fix_date(cls, v):
        return datetime.fromisoformat(v.replace("Z", "+00:00"))

    @validator("type", pre=True, always=True)
    def define_type(cls, v, *, values: Dict[str, Any]):
        return v or (
            EventType.INDICATOR
            if values["actual"] is not None or values["forecast"] is not None
            else EventType.EVENT
        )


class DataProviderResult(BaseModel):
    status: str
    result: Optional[List[Event]] = None

import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from .enums import Country, Currency


class BaseModel(AsyncAttrs, DeclarativeBase):
    def __1init__(self, **entries):
        self.__dict__.update(entries)


class IndicatorData(BaseModel):
    __tablename__ = "indicator_data"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(ForeignKey("indicator.ticker"))
    date: Mapped[datetime.datetime]
    actual: Mapped[float]
    forcast: Mapped[Optional[float]]


class Indicator(BaseModel):
    __tablename__ = "indicator"

    ticker: Mapped[str] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    data: Mapped[List[IndicatorData]] = relationship()
    country: Mapped[Country]
    currency: Mapped[Currency]
    indicator: Mapped[str]
    period: Mapped[Optional[str]]
    scale: Mapped[Optional[str]]
    source: Mapped[str]
    title: Mapped[str]
    unit: Mapped[Optional[str]]

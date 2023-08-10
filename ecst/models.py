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

    ticker: Mapped[str] = mapped_column(ForeignKey("indicator.ticker"), primary_key=True)
    date: Mapped[datetime.datetime] = mapped_column(primary_key=True)
    actual: Mapped[float]
    forecast: Mapped[Optional[float]]
    meta: Mapped["Indicator"] = relationship(back_populates="data")


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
    title: Mapped[str]
    unit: Mapped[Optional[str]]

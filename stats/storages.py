from collections import defaultdict
from datetime import datetime
from typing import List

from pydantic import PostgresDsn
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .enums import Country
from .logger import log
from .models import BaseModel, Indicator, IndicatorData
from .providers import DataProvider
from .schemas import Event, Indicators, QueryResult, QueryResultData, SQLiteDsn


class Storage(DataProvider):
    def __init__(self, dsn: PostgresDsn | SQLiteDsn):
        self.engine = create_async_engine(dsn)
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def connect(self):
        log.info("Connecting to data storage ...")
        async with self.engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)

    async def query(
        self,
        date_start: datetime,
        date_end: datetime,
        countries: List[Country] = [],
    ) -> QueryResult:
        """
        Query data storage for events in period.

        Fetch indicators from providers, transform them to models
        and merge with existing data in storage.
        """
        log.info(
            f"Querying data storage for events in period {date_start:%d.%m.%Y %H:%I:%S} to {date_end:%d.%m.%Y %H:%I:%S}"
        )

        # fetch remote events
        events = await self.fetch(date_start, date_end, countries)
        indicators = await self.transform(events)

        tickers = []
        async with self.session() as session:
            async with session.begin():
                keys = indicators.meta.keys()
                if keys:
                    # First, sync meta data
                    q = select(Indicator.ticker).filter(Indicator.ticker.in_(keys))
                    for ind in await session.execute(q):
                        # copy original tickers to a separate list to use them in data query
                        tickers.append(ind[0])
                        if ind[0] in indicators.meta:
                            # update meta data for existing tickers
                            await session.merge(indicators.meta.pop(ind[0]))
                    session.add_all(indicators.meta.values())

                if tickers:
                    # Pull range of data for existing tickers and update with new values
                    q = select(IndicatorData.ticker, IndicatorData.date).filter(
                        IndicatorData.ticker.in_(tickers),
                        IndicatorData.date.between(date_start, date_end),
                    )
                    for index in await session.execute(q):
                        # update existing data rows
                        if index in indicators.data.keys():
                            await session.merge(indicators.data.pop(index))
                    # add new data
                    session.add_all([data for data in indicators.data.values()])

        # query data from Storage
        async with self.session() as session:
            async with session.begin():
                q = (
                    select(IndicatorData)
                    .filter(
                        IndicatorData.date.between(date_start, date_end),
                        IndicatorData.ticker.in_(tickers),
                    )
                    .order_by(IndicatorData.date)
                )
                result = await session.execute(q)
                return QueryResult(
                    data=[
                        QueryResultData(
                            ticker=data.ticker,
                            date=data.date,
                            actual=data.actual,
                            forecast=data.forecast,
                        )
                        for data in result.scalars().all()
                    ]
                )

    async def transform(self, events: List[Event]) -> Indicators:
        """Transform events into indicators.

        Remove events without actual data and then transform into two objects:
            - Indicator: meta data about particular indicator (always unique)
            - IndicatorData: forecast and actual data for particular date (not unique)

        Returns:
            Structure of indicators, that contains meta data and referenced metrics.
        """

        result = {"meta": {}, "data": defaultdict(IndicatorData)}
        for event in events:
            if event.actual:
                try:
                    result["meta"][event.ticker] = Indicator(
                        **event.dict(exclude_unset=True, exclude={"actual", "forecast", "date"})
                    )
                    # We use a combination of ticker and date as a primary key while comparing
                    # with already stored data. However, sqlalchemy returns datetime without tzinfo,
                    # so we need to remove it from pydantic model as well.
                    index = (
                        event.ticker,
                        event.date.replace(tzinfo=None),
                    )
                    result["data"][index] = IndicatorData(
                        ticker=event.ticker,
                        date=event.date,
                        actual=event.actual,
                        forecast=event.forecast,
                    )
                except Exception as error:
                    log.error("Failed to transform data into indicator {}".format(str(error)))
                    return False

        return Indicators(**result)

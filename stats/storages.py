import asyncio
from collections import defaultdict
from datetime import datetime
from typing import List, Tuple

from pydantic import PostgresDsn
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .enums import Country
from .logger import log
from .models import BaseModel, Indicator, IndicatorData
from .providers import DataProvider
from .schemas import (Event, Indicators, ListResult, QueryResult,
                      QueryResultData, SQLiteDsn)


class Storage(DataProvider):
    def __init__(self, dsn: PostgresDsn | SQLiteDsn):
        self.engine = create_async_engine(dsn)
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def connect(self):
        log.info("Connecting to data storage ...")
        async with self.engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)

    async def list(self, countries: List[Country] = []) -> ListResult:
        """List of all available indicators."""
        async with self.session() as session:
            async with session.begin():
                q = select(Indicator)
                if countries:
                    q = q.filter(Indicator.country.in_(countries))
                result = await session.execute(q)
                return ListResult(data=result.scalars().all() or [])

    async def query(
        self,
        date_start: datetime,
        date_end: datetime,
        countries: List[Country] = [],
        tickers: List[str] = [],
        no_sync: bool = False,
    ) -> QueryResult:
        """
        Query data storage for events in period.

        Fetch indicators from providers, transform them to models
        and merge with existing data in storage.

        Parameters
        ----------
        date_start : datetime
            Start date of the period.
        date_end : datetime
            End date of the period.
        countries : List[Country], optional
            List of countries to query, by default []
        tickers : List[str], optional
            List of tickers to query, by default []
        no_sync : bool, optional
            Do not sync data from providers, by default False

        """

        if not no_sync:
            log.info(f"Querying data for {date_start:%d.%m.%Y %H:%I:%S} - {date_end:%d.%m.%Y %H:%I:%S}")
            # get only dates that are not in storage
            dates = await self.dates_to_sync(date_start, date_end)
            tasks = [self.sync(*date, countries=countries) for date in dates]
            await asyncio.gather(*tasks)

        # query data from Storage
        async with self.session() as session:
            async with session.begin():
                q = (
                    select(IndicatorData)
                    .filter(
                        IndicatorData.date.between(date_start, date_end),
                    )
                    .order_by(IndicatorData.date)
                )
                if countries:
                    q = q.join(Indicator).filter(Indicator.country.in_(countries))

                if tickers:
                    q = q.filter(IndicatorData.ticker.in_(tickers))

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

    async def dates_to_sync(
        self, date_start: datetime, date_end: datetime
    ) -> List[Tuple[datetime, datetime]]:
        """
        Calculate the dates to sync with remote providers.

        Returns a list of non-overlapping ranges.
        """
        # get min and max dates from Storage
        async with self.session() as session:
            async with session.begin():
                q = select(func.min(IndicatorData.date), func.max(IndicatorData.date)).order_by(
                    IndicatorData.date
                )
                result = await session.execute(q)
                existing_rows_dates = result.fetchone()
                if all(existing_rows_dates):
                    dates = self.calculate_non_overlapping_ranges(
                        existing_rows_dates,
                        (
                            date_start,
                            date_end,
                        ),
                    )
                    return dates
                else:
                    return [(date_start, date_end)]

    def calculate_non_overlapping_ranges(
        self, existing_dates: Tuple[datetime, datetime], requested_dates: Tuple[datetime, datetime]
    ) -> List[Tuple[datetime, datetime]]:
        """
        Calculate the overlap between the two ranges of dates.

        Returns a list of non-overlapping ranges.
        """
        overlap_start = max(existing_dates[0], requested_dates[0])
        overlap_end = min(existing_dates[1], requested_dates[1])

        # Check if there is any overlap
        if overlap_start < overlap_end:
            # There is overlap, so return the non-overlapping ranges
            non_overlapping_ranges = []
            if existing_dates[0] < requested_dates[0]:
                non_overlapping_ranges.append((existing_dates[0], overlap_start))
            else:
                non_overlapping_ranges.append((requested_dates[0], overlap_start))
            if existing_dates[1] > requested_dates[1]:
                non_overlapping_ranges.append((overlap_end, existing_dates[1]))
            else:
                non_overlapping_ranges.append((overlap_end, requested_dates[1]))

            return non_overlapping_ranges
        else:
            # There is no overlap, so just return the original ranges
            return [requested_dates]

    async def sync(
        self, date_start: datetime, date_end: datetime, countries: List[Country] = []
    ) -> List[str]:
        """
        Sync data storage with remote providers.

        Returns a list of tickers that were updated.
        """
        # fetch remote events
        events = await self.fetch(date_start, date_end, countries)
        if events:
            indicators = await self.transform(events)
            return await self.update(indicators, date_start, date_end)
        return []

    async def update(
        self, indicators: Indicators, date_start: datetime, date_end: datetime
    ) -> List[str]:
        """Update data storage with new indicators.

        Returns a list of tickers that were created or modified.
        """
        tickers = list(indicators.meta.keys())
        async with self.session() as session:
            async with session.begin():
                if tickers:
                    # First, sync meta data
                    q = select(Indicator.ticker).filter(Indicator.ticker.in_(tickers))
                    for ind in await session.execute(q):
                        # copy original tickers to a separate list to use them in data query
                        if ind[0] in indicators.meta:
                            # update meta data for existing tickers
                            await session.merge(indicators.meta.pop(ind[0]))
                    session.add_all(indicators.meta.values())

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
        return tickers

    async def transform(self, events: List[Event]) -> Indicators:
        """Transform events into indicators.

        Remove events without actual data and then transform into two objects:
            - Indicator: meta data about particular indicator (always unique)
            - IndicatorData: forecast and actual data for particular date (not unique)

        Returns dictionary that contains meta data and referenced metrics.
        """
        result = {"meta": {}, "data": defaultdict(IndicatorData)}
        for event in events:
            if event.actual:
                try:
                    result["meta"][event.ticker] = Indicator(
                        **event.model_dump(
                            exclude_unset=True, exclude={"actual", "forecast", "date"}
                        )
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

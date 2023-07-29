from datetime import datetime
from typing import List

from pydantic import PostgresDsn
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .logger import log
from .models import BaseModel, Indicator, IndicatorData
from .schemas import Event, SQLiteDsn


class Storage:
    def __init__(self, dsn: PostgresDsn | SQLiteDsn):
        self.engine = create_async_engine(dsn, echo=True)
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def connect(self):
        log.info("Connecting to data storage ...")
        async with self.engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)

    async def load(self, events: List[Event]) -> bool:
        log.info("Transforming events into indicators ...")

        indicators = {}
        for event in events:
            if event.actual:
                try:
                    if event.ticker not in indicators:
                        indicators[event.ticker] = Indicator(
                            **event.dict(
                                exclude_unset=True,
                                exclude={"actual", "forecast", "date"}
                            ),
                            data=[
                                IndicatorData(
                                    ticker=event.ticker,
                                    date=event.date,
                                    actual=event.actual,
                                    forcast=event.forecast,
                                )
                            ],
                        )
                    else:
                        indicators[event.ticker].data.append(
                            IndicatorData(
                                ticker=event.ticker,
                                date=event.date,
                                actual=event.actual,
                                forcast=event.forecast,
                            )
                        )
                except Exception as error:
                    log.error("Failed to transform data into indicator {}".format(str(error)))
                    return False

        log.info("Loading event into data storage ...")
        async with self.session() as session:
            async with session.begin():
                try:
                    q = select(Indicator.ticker).filter(Indicator.ticker.in_(indicators.keys()))
                    for ind in await session.execute(q):
                        # todo: don't try to merge if data is already in Storage, instead create indicator
                        #       and then add all relevant data
                        await session.merge(indicators.pop(ind.ticker))
                    session.add_all(indicators.values())
                    await session.commit()
                except Exception as e:
                    log.error("Error while updating storage record: {}".format(str(e)))
                    return False
        return True

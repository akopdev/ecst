from datetime import datetime, timedelta
from typing import List, Optional

import aiohttp
from pydantic import ValidationError

from .enums import Country
from .logger import log
from .schemas import (DataProviderResult, Event, Indicator, IndicatorData,
                      IndicatorDataTS)
from .storage import Storage


class DataProvider(Storage):
    async def extract(
        self,
        date_start: Optional[datetime] = None,
        date_end: Optional[datetime] = None,
        countries: List[Country] = [],
    ) -> List[Event]:
        if not date_start:
            date_start = datetime.utcnow()
        if not date_end:
            date_end = date_start + timedelta(days=7)
        log.info(f"Extract events dated between `{date_start:%d.%m.%Y}-{date_end:%d.%m.%Y}`")
        async with aiohttp.ClientSession() as session:
            events = []
            async with session.get(
                "https://economic-calendar.tradingview.com/events",
                params={
                    "from": date_start.isoformat() + "Z",
                    "to": date_end.isoformat() + "Z",
                    "countries": ",".join(countries or [c.value for c in Country]),
                },
            ) as resp:
                res = await resp.json()
                try:
                    events = DataProviderResult(**res).result
                except ValidationError as error:
                    log.error("Error while parsing data: {}".format(str(error)))
                    return False
                return events

    def transform(self, event: Event) -> Optional[Indicator]:
        if event.actual or event.forecast:
            try:
                ind = Indicator(
                    **event.model_dump(exclude_unset=True),
                    data=IndicatorData(
                        actual=IndicatorDataTS(
                            date=event.date,
                            value=event.actual,
                        ),
                        forcast=IndicatorDataTS(
                            date=event.date,
                            value=event.forecast,
                        ),
                    ),
                )
            except Exception as e:
                log.error("Failed to transform data into indicator")
                log.error(e)
                return None
            return ind

    async def etl(
        self,
        date_start: Optional[datetime] = None,
        date_end: Optional[datetime] = None,
        countries: List[Country] = [],
    ):
        data = await self.extract(date_start, date_end, countries)
        if data:
            for event in data:
                indicator = self.transform(event)
                if indicator:
                    await self.load(indicator)

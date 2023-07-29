from datetime import datetime
from typing import List, Optional

import aiohttp
from pydantic import ValidationError

from .enums import Country
from .logger import log
from .models import Indicator, IndicatorData
from .schemas import DataProviderResult, Event
from .storages import Storage


class DataProvider(Storage):
    async def extract(
        self,
        date_start: datetime,
        date_end: datetime,
        countries: List[Country] = [],
    ) -> List[Event]:
        log.info(
            "Extract events from data provider for period:"
            f"`{date_start:%d.%m.%Y %H:%I:%S} to {date_end:%d.%m.%Y %H:%I:%S}`"
        )
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
        if event.actual:
            try:
                ind = Indicator(
                    **event.dict(exclude_unset=True, exclude={"actual", "forecast", "date"}),
                    data=[
                        IndicatorData(
                            ticker=event.ticker,
                            date=event.date,
                            actual=event.actual,
                            forcast=event.forecast,
                        )
                    ],
                )
            except Exception as error:
                log.error("Failed to transform data into indicator {}".format(str(error)))
                return None
            return ind

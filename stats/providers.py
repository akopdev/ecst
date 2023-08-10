import random
from datetime import datetime
from typing import List

import aiohttp
from pydantic import ValidationError

from .enums import Country
from .logger import log
from .schemas import DataProviderResult, Event


class DataProvider:
    _user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",  # noqa
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",  # noqa
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9",  # noqa
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1",  # noqa
        "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",  # noqa
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",  # noqa
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",  # noqa
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",  # noqa
    ]

    async def fetch(
        self,
        date_start: datetime,
        date_end: datetime,
        countries: List[Country] = [],
    ) -> List[Event]:
        log.info(
            "Fetch data from provider for period:"
            f"`{date_start:%d.%m.%Y %H:%I:%S} to {date_end:%d.%m.%Y %H:%I:%S}`"
        )
        async with aiohttp.ClientSession() as session:
            events = []
            async with session.get(
                "https://economic-calendar.tradingview.com/events",
                headers={"User-Agent": random.choice(self._user_agents)},
                params={
                    "from": date_start.isoformat() + "Z",
                    "to": date_end.isoformat() + "Z",
                    "countries": ",".join(countries or [c.value for c in Country]),
                },
            ) as resp:
                res = await resp.json()
                try:
                    events = DataProviderResult(**res).result
                    if not events:
                        return []
                except ValidationError as error:
                    log.error("Error while parsing data: {}".format(str(error)))
                    return False
                return events

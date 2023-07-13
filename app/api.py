from datetime import datetime, timedelta
from typing import Dict, List, Optional

import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient

from . import enums, schemas


async def fetch(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    countries: List[enums.Country] = [],
) -> List[schemas.Event]:
    events = []
    if not start:
        start = datetime.utcnow() - timedelta(days=1)
    if not end:
        end = datetime.utcnow() + timedelta(days=90)
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://economic-calendar.tradingview.com/events",
            params={
                "from": start.isoformat() + "Z",
                "to": end.isoformat() + "Z",
                "countries": ",".join(countries or [c.value for c in enums.Country]),
            },
        ) as resp:
            res = await resp.json()
            if res["status"] == "ok" and res["result"]:
                for result in res["result"]:
                    if result["date"]:
                        result["date"] = datetime.fromisoformat(
                            result["date"].replace("Z", "+00:00")
                        )
                    try:
                        events.append(schemas.Event(**result))
                    except Exception as e:
                        # TODO: more accurate exception validation
                        raise ValueError(e)
    return events


async def save(storage: AsyncIOMotorClient, event: schemas.Event) -> bool:
    payload = {
        "$set": {
            "currency": event.currency,
            "source": event.source,
            "importance": event.importance,
            "unit": event.unit,
            "scale": event.scale,
            "ticker": event.ticker,
            "type": event.type,
            "updated_at": datetime.now(),
        },
        "$addToSet": {
            "data": {
                "date": event.date,
                "period": event.period,
                "actual": event.actual,
                "forecast": event.forecast,
            }
        },
    }
    # If we don"t have an actual data then just update schedule info
    if not event.actual:
        del payload["$addToSet"]
        payload["$set"]["next"] = {
            "date": event.date,
            "period": event.period,
            "forecast": event.forecast,
        }

    res = await storage.events.update_one(
        {"title": event.title, "indicator": event.indicator, "country": event.country},
        payload,
        upsert=True,
    )

    return bool(res.modified_count)


async def get_date_ranges(storage: AsyncIOMotorClient) -> Dict[str, datetime]:
    pipeline = [
        {"$match": {"actual": "", "type": enums.EventType.INDICATOR.value}},
        {
            "$group": {
                "_id": {"title": "$title", "indicator": "$indicator", "country": "$country"},
                "start": {"$max": "$date"},
                "end": {"$min": "$date"},
            }
        },
    ]
    print(pipeline)
    async for doc in storage.events.aggregate(pipeline):
        print(doc)

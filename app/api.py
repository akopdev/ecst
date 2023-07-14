from datetime import datetime, timedelta
from typing import Dict, List, Optional

import aiohttp
from motor.motor_asyncio import AsyncIOMotorCollection

from . import enums, schemas
from .logger import log


async def fetch(
    db: Optional[AsyncIOMotorCollection] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    countries: List[enums.Country] = [],
) -> bool:
    if not start:
        start = datetime.utcnow() - timedelta(days=1)
    if not end:
        end = datetime.utcnow() + timedelta(days=90)

    log.info(f"Fetching data from server for date range '{start:%d.%m.%Y}' to '{end:%d.%m.%Y}'...")
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
                log.info(f"{len(res['result'])} new events found")
                for result in res["result"]:
                    if result["date"]:
                        result["date"] = datetime.fromisoformat(
                            result["date"].replace("Z", "+00:00")
                        )
                    try:
                        event = schemas.Event(**result)
                    except Exception as e:
                        log.error("Error while parsing data: {}".format(str(e)))
                        return False

                    if not await save(db, event):
                        log.error("Failed to store data in database.")
                        return False
            return True


async def save(db: AsyncIOMotorCollection, event: schemas.Event) -> bool:
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
    log.info("Saving event into data storage ...")
    try:
        res = await db.events.update_one(
            {"title": event.title, "indicator": event.indicator, "country": event.country},
            payload,
            upsert=True,
        )
    except Exception as e:
        log.error("Error while updating storage record: {}".format(str(e)))
        return False
    log.info(f"Matched {res.matched_count} documents and modified {res.modified_count} documents")
    return True


async def get_date_ranges(db: AsyncIOMotorCollection) -> Optional[Dict[str, datetime]]:
    pipeline = [
        {"$unwind": "$data"},
        {"$match": {"data.actual": None, "type": enums.EventType.INDICATOR.value}},
        {
            "$group": {
                "_id": None,
                "start": {"$min": "$data.date"},
                "end": {"$max": "$data.date"},
            }
        },
    ]
    try:
        res = await db.events.aggregate(pipeline).to_list(length=1)
    except Exception as e:
        log.error("Error while fetching indicators to update: {}".format(str(e)))
        return None

    return (
        None
        if not res[0]
        else {
            "start": res[0]["start"],
            "end": res[0]["end"],
        }
    )

from datetime import datetime
from typing import Dict, Optional

from motor.motor_asyncio import (AsyncIOMotorClient, AsyncIOMotorCollection,
                                 AsyncIOMotorDatabase)
from pydantic import MongoDsn, ValidationError

from .logger import log
from .schemas import Indicator


class Storage:
    def __init__(self, dsn: str):
        self.db: AsyncIOMotorDatabase = self.connect(dsn)
        if self.db is None:
            raise SystemError("Failed to enable storage")

    def connect(self, dsn: str) -> Optional[AsyncIOMotorDatabase]:
        try:
            valid_dsn = MongoDsn(dsn)
            db = str(valid_dsn).rsplit("/", 1)
            client = AsyncIOMotorClient(db[0])
        except ValidationError:
            log.error("Wrong storage connection string")
            return False
        except Exception as e:
            log.error("Storage is not available")
            log.error(e)
            return False

        if not client or not client.server_info():
            log.error("Failed to connect to storage.")
            return False
        return client[db[1]]

    async def load(self, ind: Indicator, collection: str = "indicators") -> bool:
        payload = {
            "$set": {
                "country": ind.country,
                "currency": ind.currency,
                "indicator": ind.indicator,
                "ticker": ind.ticker,
                "title": ind.title,
                "unit": ind.unit,
                "updated_at": datetime.utcnow(),
            },
            "$addToSet": {"data": ind.data.dict()},
        }
        log.info("Saving event into data storage ...")
        try:
            res = await self.db[collection].update_one(
                {"ticker": ind.ticker},
                payload,
                upsert=True,
            )
        except Exception as e:
            log.error("Error while updating storage record: {}".format(str(e)))
            return False
        log.info(
            f"Matched {res.matched_count} documents and modified {res.modified_count} documents"
        )
        return True

    async def get_date_ranges(
        self, collection: str = "indicators"
    ) -> Optional[Dict[str, datetime]]:
        pipeline = [
            {"$unwind": "$data"},
            {"$match": {"data.actual": None}},
            {
                "$group": {
                    "_id": None,
                    "start": {"$min": "$data.date"},
                    "end": {"$max": "$data.date"},
                }
            },
        ]
        try:
            res = await self.db[collection].aggregate(pipeline).to_list(length=1)
        except Exception as e:
            log.error("Error while fetching indicators to update: {}".format(str(e)))
            return None

        return (
            None
            if not res[0]
            else {
                "date_start": res[0]["start"],
                "date_end": res[0]["end"],
            }
        )

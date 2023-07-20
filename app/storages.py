from datetime import datetime, timedelta
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
            "$addToSet": {},
        }
        if ind.data.actual.value is not None:
            payload["$addToSet"]["data.actual"] = ind.data.actual.model_dump(exclude_unset=True)

        if ind.data.forcast.value is not None:
            payload["$addToSet"]["data.forcast"] = ind.data.forcast.model_dump(exclude_unset=True)

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

from datetime import datetime

from montydb import MontyClient, set_storage
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from pydantic import MongoDsn, ValidationError

from .logger import log
from .schemas import Indicator, MontyDsn


class Storage:
    def __init__(self, dsn: MongoDsn | MontyDsn, collection: str = "indicators"):
        if dsn.scheme == "montydb":
            self.collection = self.connect_montydb(dsn, collection)
        else:
            self.collection = self.connect_mongodb(dsn, collection)

    def connect_montydb(self, dsn: MontyDsn, collection: str) -> MontyClient:
        try:
            repo = "/".join([dsn.path, collection])
            set_storage(repository=repo, use_bson=True)
            client = MontyClient(repo)
        except Exception:
            ValidationError("Storage is not available or database was not provided.")
        return client[collection]

    def connect_mongodb(self, dsn: MongoDsn, collection: str) -> AsyncIOMotorCollection:
        try:
            db = str(dsn).rsplit("/", 1)
            client = AsyncIOMotorClient(db[0])
        except Exception:
            ValidationError("Storage is not available or database was not provided.")

        if not client or not client.server_info():
            raise SystemError("Failed to connect to storage.")
        return client[db[1]][collection]

    async def load(self, ind: Indicator) -> bool:
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
            res = await self.collection.update_one(
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

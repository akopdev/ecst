from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

# from .settings import settings


def connect(dsn: str) -> AsyncIOMotorCollection:
    try:
        db = dsn.rsplit("/", 1)
        client = AsyncIOMotorClient(db[0])
    except Exception:
        raise Exception("Wrong dsn address")

    if not client or not client.server_info():
        raise Exception("Failed to connect to storage.")
    return client[db[1]]

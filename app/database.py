from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from .settings import settings


def connect() -> AsyncIOMotorCollection:
    client = AsyncIOMotorClient(settings.DATABASE_DSL)

    if not client or not client.server_info():
        raise Exception("Failed to connect to storage.")
    return client[settings.DATABASE_NAME]


# store data in `events` collections
storage = connect()

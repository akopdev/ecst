from motor.motor_asyncio import AsyncIOMotorClient
from .settings import settings

client = AsyncIOMotorClient(settings.DATABASE_DSL)

# store data in `events` collections
storage = client[settings.DATABASE_NAME]

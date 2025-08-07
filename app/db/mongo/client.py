import asyncio
from contextlib import asynccontextmanager

from pymongo import AsyncMongoClient
from pymongo.errors import ConnectionFailure
from app.core.config import settings
from app.utils.logging import logger
from typing import Any, Dict

MONGODB_URI = settings.MONGODB_URI
MONGO_DATABASE = settings.MONGO_DATABASE
client: AsyncMongoClient[Dict[str, Any]] = AsyncMongoClient(MONGODB_URI)
mongo_db = client[MONGO_DATABASE]

async def depends_get_mongodb():
    global client, mongo_db

    try:
        await mongo_db.command("ping")
    except ConnectionFailure:
        logger.bind(event="mongodb_connection").error("Failed to connect to MongoDB")
        await asyncio.sleep(1)
        client = AsyncMongoClient(MONGODB_URI)
        mongo_db = client[MONGO_DATABASE]

    yield mongo_db

@asynccontextmanager
async def async_get_mongodb():
    global client, mongo_db

    try:
        await mongo_db.command("ping")
    except ConnectionFailure:
        logger.bind(event="mongodb_connection").error("Failed to connect to MongoDB")
        await asyncio.sleep(1)
        client = AsyncMongoClient(MONGODB_URI)
        mongo_db = client[MONGO_DATABASE]

    yield mongo_db
from fastapi import HTTPException

import app.services.session as session_service
from app.utils.redis import redis_client
from app.core.config import settings
from app.db.mongo.client import async_get_mongodb, mongo_db
import asyncio
from datetime import datetime
from app.utils.logging import logger

async def check_expired_sessions():
    now_ts = datetime.utcnow().timestamp()
    session_ids = await redis_client.zrangebyscore("session_queue", 0, now_ts)
    if session_ids:
        async with async_get_mongodb() as db:
            for sid in session_ids:
                try:
                    await session_service.update_session(
                        session_id=sid,
                        user_id=settings.ADMIN_USER_ID,
                        updated_at=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                        status="completed",
                        db=db
                    )
                except HTTPException as e:
                    if e.status_code == 404:
                        await redis_client.zrem("session_queue", sid)
    await redis_client.zremrangebyscore("session_queue", 0, now_ts)

async def session_watcher():
    while True:
        try:
            await check_expired_sessions()
        except Exception as e:
            print(f"[session_watcher] error: {e}")
        await asyncio.sleep(10)
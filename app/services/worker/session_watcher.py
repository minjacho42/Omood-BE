import app.repositories.session as session_repo
from app.utils.redis import redis_client
from app.db.mongo.client import async_get_mongodb, mongo_db
import asyncio
from datetime import datetime

async def check_expired_sessions():
    now_ts = datetime.utcnow().timestamp()
    session_ids = await redis_client.zrangebyscore("session_queue", 0, now_ts)
    async with async_get_mongodb() as db:
        for sid in session_ids:
            await session_repo.update_session(
                session_id=sid,
                updated_at=datetime.utcnow(),
                status="completed",
                reflection=None,
                db=db
            )
    await redis_client.zremrangebyscore("session_queue", 0, now_ts)

async def session_watcher():
    while True:
        try:
            await check_expired_sessions()
        except Exception as e:
            print(f"[session_watcher] error: {e}")
        await asyncio.sleep(10)
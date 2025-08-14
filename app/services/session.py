from app.core.config import settings
from app.models.session import Session
import app.repositories.session as session_repo
from app.utils.logging import logger
from app.utils.redis import redis_client
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi.exceptions import HTTPException
from typing import List, Dict

logger = logger.bind(layer="service", module="session")

async def create_session(user_id, subject:str, goal:str, duration: int, break_duration: int, tags: List[str], created_at: str, db) -> Session:
    try:
        new_session = Session(
            user_id=user_id,
            subject=subject,
            goal=goal,
            duration=duration,
            break_duration=break_duration,
            tags=tags,
            created_at=datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%S.%fZ'),
            status="pending",
        )
        created_session = await session_repo.add_session(new_session, db)
        await redis_client.set(f"current_session:{user_id}", created_session.id)
        logger_info = {
            "subject": subject,
            "goal": goal,
            "duration": duration,
            "break_duration": break_duration,
            "tags": tags,
            "status": created_session.status,
            "created_at": created_session.created_at.isoformat(),
        }
        logger.bind(
            event="create_session",
            session_id=created_session.id,
            user_id=user_id,
            **logger_info
        ).info(f"Session created successfully under user {user_id} with session ID {created_session.id}")
        return created_session
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def get_session(user_id: str, session_id: str, db) -> Session:
    try:
        target_session = await session_repo.get_session_by_id(session_id, db)
        if not target_session:
            raise HTTPException(status_code=404, detail="Session not found")
        if target_session.user_id != user_id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return target_session
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def get_current_session(user_id: str, db) -> Session:
    try:
        current_session_id = await redis_client.get(f"current_session:{user_id}")
        if not current_session_id:
            raise HTTPException(status_code=404, detail="Session not found")
        return await get_session(user_id=user_id, session_id=current_session_id, db=db)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def update_session(session_id: str, user_id: str, db, status: str=None, updated_at: str=None, reflection: str=None, session_info: Dict=None):
    try:
        updated_at = datetime.strptime(updated_at, '%Y-%m-%dT%H:%M:%S.%fZ')
        target_session = await session_repo.get_session_by_id(session_id, db)
        logger_info = {}
        if not target_session:
            raise HTTPException(status_code=404, detail="Session not found")
        if target_session.user_id != user_id and user_id != settings.ADMIN_USER_ID:
            raise HTTPException(status_code=403, detail="Forbidden")
        if status:
            logger_info["old_status"] = target_session.status
            logger_info["new_status"] = status
            if status == "started":
                await redis_client.zadd(
                    "session_queue",
                    {session_id: updated_at.timestamp() + target_session.duration * 60},
                )
            else:
                await redis_client.zrem("session_queue", session_id)
            if status in {"started", "pending", "paused"}:
                await redis_client.set(f"current_session:{user_id}", session_id)
            else:
                await redis_client.delete(f"current_session:{user_id}")
        if reflection:
            logger_info["old_status"] = target_session.status
            logger_info["new_status"] = "reviewed"
        if session_info:
            for key, value in session_info.items():
                logger_info[f"old_{key}"] = target_session.model_dump(by_alias=True).get(key)
                logger_info[f"new_{key}"] = value
        updated_session = await session_repo.update_session(session_id, updated_at, status, reflection, session_info, db)
        logger.bind(
            event="update_session",
            user_id=user_id,
            session_id=session_id,
            **logger_info
        ).info(f"Session updated successfully under user {user_id} with session ID {session_id}")
        return updated_session
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def delete_session(user_id: str, session_id: str, db):
    try:
        target_session = await session_repo.get_session_by_id(session_id, db)
        if not target_session:
            raise HTTPException(status_code=404, detail="Session not found")
        if target_session.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        delete_cnt = await session_repo.delete_session(session_id, db)
        if delete_cnt > 0:
            if target_session.status == "started":
                await redis_client.zrem("session_queue", session_id)
                await redis_client.delete(f"current_session:{user_id}")
            elif target_session.status in {"pending", "paused"}:
                await redis_client.delete(f"current_session:{user_id}")
            logger.bind(
                event="delete_session",
                user_id=user_id,session_id=session_id
            ).info(f"Session deleted successfully under user {user_id} with session ID {session_id}")
            return "Success"
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def get_user_session_by_date_range(user_id:str, tz: str, start_date: str, end_date: str, db):
    try:
        zone = ZoneInfo(tz)
        local_start_time = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=zone)
        local_end_time = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=zone)
        local_end_time = local_end_time.replace(hour=23, minute=59, second=59)
        start_time = local_start_time.astimezone(ZoneInfo("UTC"))
        end_time = local_end_time.astimezone(ZoneInfo("UTC"))
        sessions = await session_repo.get_user_sessions_by_range(user_id, start_time, end_time, db)
        return sessions
    except Exception as e:
        logger.bind(event="service memo").error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

from bson import ObjectId
from requests import session
from app.models.session import Session
from datetime import datetime
from app.utils.logging import logger
from typing import List, Dict

logger = logger.bind(layer="repository", module="session")

def fix_mongo_id(doc: dict) -> dict:
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

async def add_session(session: Session, db):
    session_collections = db["sessions"]
    session_dict = session.model_dump(by_alias=True)
    result = await session_collections.insert_one(session_dict)
    session.id = str(result.inserted_id)
    logger.info(f"Added session {session.id}")
    return session

async def delete_session(session_id: str, db):
    session_collections = db["sessions"]
    result = await session_collections.delete_one({"_id": ObjectId(session_id)})
    return result.deleted_count

async def update_session(session_id: str, updated_at: datetime, status: str, reflection: str | None, session_info: Dict, db) -> Session:
    session_collections = db["sessions"]
    update_doc = {
        "updated_at": updated_at,
    }
    if session_info:
        for key, value in session_info.items():
            update_doc[key] = value
    if status:
        update_doc["status"] = status
    if status == "started":
        update_doc["started_at"] = updated_at
    if reflection:
        update_doc["reflection"] = reflection
    await session_collections.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": update_doc}
    )
    # Fetch and return the updated document as Session
    updated_doc = await session_collections.find_one(
        {"_id": ObjectId(session_id)}
    )
    if not updated_doc:
        return None
    return Session(**fix_mongo_id(updated_doc))

async def get_session_by_id(session_id: str, db) -> Session | None:
    session_collections = db["sessions"]
    result = await session_collections.find_one({"_id": ObjectId(session_id)})
    if result:
        return Session(**fix_mongo_id(result))
    else:
        return None

async def get_user_session_by_date(user_id: str, date: datetime, db):
    session_collections = db["sessions"]
    start = datetime(date.year, date.month, date.day)
    end = datetime(date.year, date.month, date.day, 23, 59, 59)
    cursor = session_collections.find({
        "user_id": user_id,
        "created_at": {
            "$gte": start,
            "$lte": end
        }
    })
    results = await cursor.to_list(length=None)
    logger.info([fix_mongo_id(r) for r in results])
    return [Session(**fix_mongo_id(r)) for r in results]

async def get_user_sessions_by_range(user_id: str, start_time: datetime, end_time: datetime, db):
    session_collections = db["sessions"]
    cursor = session_collections.find({
        "user_id": user_id,
        "created_at": {
            "$gte": start_time,
            "$lte": end_time
        }
    })
    results = await cursor.to_list(length=None)
    return [Session(**fix_mongo_id(r)) for r in results]

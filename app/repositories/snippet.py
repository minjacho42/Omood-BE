from bson import ObjectId
from app.models.snippet import Snippet
from datetime import datetime
from app.utils.logging import logger

def fix_mongo_id(doc: dict) -> dict:
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

async def add_snippet(snippet: Snippet, db):
    snippet_collections = db["snippets"]
    snippet_dict = snippet.model_dump(by_alias=True)
    result = await snippet_collections.insert_one(snippet_dict)
    snippet.id = str(result.inserted_id)
    return snippet

async def delete_snippet(snippet_id: str, db):
    snippet_collections = db["snippets"]
    result = await snippet_collections.delete_one({"_id": ObjectId(snippet_id)})
    return result.deleted_count

async def update_snippet(snippet_id: str, updated_fields: dict, db):
    snippet_collections = db["snippets"]
    updated_fields["updated_at"] = datetime.utcnow()
    result = await snippet_collections.update_one(
        {"_id": ObjectId(snippet_id)},
        {"$set": updated_fields}
    )
    return result.modified_count

async def get_snippet_by_id(snippet_id: str, db):
    snippet_collections = db["snippets"]
    result = await snippet_collections.find_one({"_id": ObjectId(snippet_id)})
    return Snippet(**fix_mongo_id(result))

async def get_user_snippet_by_date(user_id: str, date: datetime, db):
    snippet_collections = db["snippets"]
    start = datetime(date.year, date.month, date.day)
    end = datetime(date.year, date.month, date.day, 23, 59, 59)
    cursor = snippet_collections.find({
        "user_id": user_id,
        "created_at": {
            "$gte": start,
            "$lte": end
        }
    })
    results = await cursor.to_list(length=None)
    logger.info([fix_mongo_id(r) for r in results])
    return [Snippet(**fix_mongo_id(r)) for r in results]

async def get_user_snippets_by_range(user_id: str, start_time: datetime, end_time: datetime, db):
    snippet_collections = db["snippets"]
    cursor = snippet_collections.find({
        "user_id": user_id,
        "created_at": {
            "$gte": start_time,
            "$lte": end_time
        }
    })
    results = await cursor.to_list(length=None)
    return [Snippet(**fix_mongo_id(r)) for r in results]
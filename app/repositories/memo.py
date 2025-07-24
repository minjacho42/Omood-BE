from bson import ObjectId
from app.models.memo import Memo
from datetime import datetime
from app.utils.logging import logger

def fix_mongo_id(doc: dict) -> dict:
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

async def add_memo(memo: Memo, db):
    memo_collections = db["memos"]
    memo_dict = memo.model_dump(by_alias=True)
    result = await memo_collections.insert_one(memo_dict)
    memo.id = str(result.inserted_id)
    return memo

async def delete_memo(memo_id: str, db):
    memo_collections = db["memos"]
    result = await memo_collections.delete_one({"_id": ObjectId(memo_id)})
    return result.deleted_count

async def update_memo(memo_id: str, updated_fields: dict, db):
    memo_collections = db["memos"]
    updated_fields["updated_at"] = datetime.utcnow()
    result = await memo_collections.update_one(
        {"_id": ObjectId(memo_id)},
        {"$set": updated_fields}
    )
    return result.modified_count

async def get_memo_by_id(memo_id: str, db):
    memo_collections = db["memos"]
    result = await memo_collections.find_one({"_id": ObjectId(memo_id)})
    return Memo(**fix_mongo_id(result))

async def get_user_memo_by_date(user_id: str, date: datetime, db):
    memo_collections = db["memos"]
    start = datetime(date.year, date.month, date.day)
    end = datetime(date.year, date.month, date.day, 23, 59, 59)
    cursor = memo_collections.find({
        "user_id": user_id,
        "created_at": {
            "$gte": start,
            "$lte": end
        }
    })
    results = await cursor.to_list(length=None)
    logger.info([fix_mongo_id(r) for r in results])
    return [Memo(**fix_mongo_id(r)) for r in results]

async def get_user_memos_by_range(user_id: str, start_time: datetime, end_time: datetime, db):
    memo_collections = db["memos"]
    cursor = memo_collections.find({
        "user_id": user_id,
        "created_at": {
            "$gte": start_time,
            "$lte": end_time
        }
    })
    results = await cursor.to_list(length=None)
    return [Memo(**fix_mongo_id(r)) for r in results]
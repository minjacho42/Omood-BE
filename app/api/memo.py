from fastapi import APIRouter, Depends, UploadFile, Form, Query, Request
from typing import Optional, List, Any
from app.utils.logging import logger
from app.db.mongo.client import get_mongodb
from app.services.auth import get_authenticated_user_id
from app.services.memo import (
    create_memo,
    get_user_memos_by_date_range,
    delete_memo,
)
from app.models.memo import (
    MemoResponse
)

router = APIRouter()

@router.post("/", summary="Create a memo")
async def post_memo(
    request: Request,
    content: str = Form(...),
    tags: str = Form(None),
    user_id: str = Depends(get_authenticated_user_id),
    db: Any = Depends(get_mongodb)
):
    form = await request.form()
    logger.info(form)
    files = [(k, v) for k, v in form.items() if k.split("_")[0] == "image" or k.split("_")[0] == "audio"]
    logger.info(files)
    tag_list = tags.split(',') if tags else []
    content = content.strip()
    return await create_memo(
        user_id=user_id,
        tags=tag_list,
        content=content,
        attachments=files,
        db=db
    )

@router.delete("/{memo_id}", summary="Delete a memo")
async def delete_memo_api(
    memo_id: str,
    user_id: str = Depends(get_authenticated_user_id),
    db: Any = Depends(get_mongodb)
):
    await delete_memo(user_id, memo_id, db)
    return {"message": "memo deleted successfully"}



# @router.get("/date", response_model=List[MemoResponse], summary="Get each date's memos with details")
# async def get_today_memos_api(
#     tz: str = Query(...),
#     date: str = Query(...),
#     user_id: str = Depends(get_authenticated_user_id),
#     db: Any = Depends(get_mongodb)
# ):
#     return await get_user_memos_by_date(user_id, tz, date, db)

@router.get("/list", response_model=List[MemoResponse], summary="Get memos by date range")
async def get_list_of_memos_api(
        tz: str = Query(...),
        start_date: str = Query(...),
        end_date: str = Query(...),
        user_id: str = Depends(get_authenticated_user_id),
        db: Any = Depends(get_mongodb)
):
    return await get_user_memos_by_date_range(user_id, tz, start_date, end_date, db)

# @router.get("/organize", response_model=List[MemoResponse], summary="Get organized memos")
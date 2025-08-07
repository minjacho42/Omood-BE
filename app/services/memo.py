import uuid
import asyncio
from app.models.memo import Memo, MemoResponse, MemoAttachment, MemoAttachmentResponse
from typing import List, Tuple
import app.repositories.memo as memo_repo
import app.repositories.s3 as s3_repo
from app.utils.logging import logger
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import UploadFile
from fastapi.exceptions import HTTPException

async def create_memo(user_id: str, tags: List[str], content: str, attachments: List[Tuple[str, UploadFile]]
, db):
    try:
        attachment_list = []
        for key, file in attachments:
            attachment_type = key.split('_')[0]
            if attachment_type == 'image' or attachment_type == 'audio':
                attachment_id = str(uuid.uuid4())
                attachment_filename = f"{attachment_id}.{file.filename.rsplit('.')[1]}"
                attachment_key = f"{user_id}/{attachment_filename}"
                await s3_repo.put_object(object_key=attachment_key, object_content=file)
                attachment_list.append(
                    MemoAttachment(
                        id = attachment_id,
                        type = key.split('_')[0],
                        key = attachment_key,
                        filename = attachment_filename,
                    )
                )
            else:
                HTTPException(status_code=404, detail="Not Found")
        new_memo = Memo(
            user_id = user_id,
            content = content,
            tags= tags,
            attachments = attachment_list
        )
        await memo_repo.add_memo(new_memo, db)
    except Exception as e:
        logger.bind(event="service memo").error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def delete_memo(user_id: str, memo_id: str, db):
    try:
        target_memo = await memo_repo.get_memo_by_id(memo_id, db)
        if not target_memo:
            raise HTTPException(status_code=404, detail="Memo not found")
        if target_memo.user_id != user_id:
            raise HTTPException(status_code=403, detail="Forbidden")
        delete_cnt = await memo_repo.delete_memo(memo_id, db)
        if delete_cnt > 0:
            if len(target_memo.attachments) > 0:
                delete_task = [
                    s3_repo.delete_object(attachment.key)
                    for attachment in target_memo.attachments
                ]
                await asyncio.gather(*delete_task)
        return "Success"
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.bind(event="service memo").error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def get_memo(user_id: str, memo_id: str, db):
    try:
        target_memo = await memo_repo.get_memo_by_id(memo_id, db)
        if not target_memo:
            raise HTTPException(status_code=404, detail="Memo not found")
        if target_memo.user_id != user_id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return await get_response_memo(target_memo)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.bind(event="service memo").error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def modify_memo(user_id: str, memo_id: str, tags: List[str], content: str, new_attachments: List[Tuple[str, UploadFile]], keep_attachments: List[str], db):
    try:
        # Fetch and authorize
        target_memo = await memo_repo.get_memo_by_id(memo_id, db)
        if not target_memo:
            raise HTTPException(status_code=404, detail="Memo not found")
        if target_memo.user_id != user_id:
            raise HTTPException(status_code=403, detail="Forbidden")

        # Delete attachments the user didn't keep
        to_delete = [att for att in target_memo.attachments if att.id not in keep_attachments]
        delete_tasks = [s3_repo.delete_object(att.key) for att in to_delete]
        await asyncio.gather(*delete_tasks)

        # Build list of kept attachments
        updated_attachments = [att for att in target_memo.attachments if att.id in keep_attachments]

        # Process new attachments
        for key, file in new_attachments:
            attachment_type = key.split('_')[1]
            attachment_id = str(uuid.uuid4())
            ext = file.filename.rsplit('.', 1)[1]
            filename = f"{attachment_id}.{ext}"
            object_key = f"{user_id}/{filename}"
            await s3_repo.put_object(object_key=object_key, object_content=file)
            updated_attachments.append(
                MemoAttachment(
                    id=attachment_id,
                    type=attachment_type,
                    key=object_key,
                    filename=filename,
                )
            )

        # Apply update in database
        # Assumes repository has update_memo; adjust if named differently
        updated = await memo_repo.update_memo(
            memo_id,
            user_id=user_id,
            content=content,
            tags=tags,
            attachments=updated_attachments,
            db=db
        )
        return await get_response_memo(updated)
    except HTTPException:
        raise
    except Exception as e:
        logger.bind(event="service memo modify").error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def _get_attachment_response(attachment: MemoAttachment) -> MemoAttachmentResponse:
    try:
        url = await s3_repo.get_presigned_url(attachment.key)
        return MemoAttachmentResponse(
            id=attachment.id,
            type=attachment.type,
            url=url,
            filename=attachment.filename,
        )
    except Exception as e:
        logger.bind(event="service memo presigned url single").error(f"{attachment.key} - {e}")
        raise e

async def get_all_attachments_presigned_url(attachments: List[MemoAttachment]) -> List[MemoAttachmentResponse]:
    if not attachments:
        return []

    try:
        coroutines = [
            _get_attachment_response(attachment)
            for attachment in attachments
        ]
        return list(await asyncio.gather(*coroutines))
    except Exception as e:
        logger.bind(event="service memo presigned url").error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def get_response_memo(memo: Memo) -> MemoResponse:
    try:
        memo_response = MemoResponse(
            id = memo.id,
            user_id = memo.user_id,
            content = memo.content,
            tags = memo.tags,
            attachments = await get_all_attachments_presigned_url(memo.attachments),
            created_at = memo.created_at,
            updated_at = memo.updated_at,
            category = memo.category,
            category_confidence = memo.category_confidence,
            is_archived = memo.is_archived,
        )
        return memo_response
    except Exception as e:
        logger.bind(event="service memo get response").error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def get_user_memos_by_date_range(user_id:str, tz: str, start_date: str, end_date: str, db):
    try:
        zone = ZoneInfo(tz)
        local_start_time = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=zone)
        local_end_time = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=zone)
        local_end_time = local_end_time.replace(hour=23, minute=59, second=59)
        start_time = local_start_time.astimezone(ZoneInfo("UTC"))
        end_time = local_end_time.astimezone(ZoneInfo("UTC"))
        memos = await memo_repo.get_user_memos_by_range(user_id, start_time, end_time, db)
        coroutines = [get_response_memo(memo) for memo in memos]
        response_memos = await asyncio.gather(*coroutines)
        return response_memos
    except Exception as e:
        logger.bind(event="service memo").error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def get_organize_target_memos(user_id: str, tz: str, limit: int, min_age_days: int, db):
    try:
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
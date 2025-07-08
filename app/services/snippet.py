import uuid
import asyncio

from requests import delete

from app.models.snippet import Snippet, SnippetResponse
import os
from typing import List
import app.repositories.snippet as snippet_repo
import app.repositories.s3 as s3_repo
from app.utils.logging import logger
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import UploadFile
from fastapi.exceptions import HTTPException

async def get_response_snippet(snippet: Snippet) -> SnippetResponse:
    try:
        snippet_response = SnippetResponse(
            id = snippet.id,
            user_id = snippet.user_id,
            content_type = snippet.content_type,
            content = snippet.content,
            content_url = await s3_repo.get_presigned_url(snippet.content_key) if snippet.content_type != 'text' else None,
            tags = snippet.tags,
            created_at = snippet.created_at,
            updated_at = snippet.updated_at,
        )
        return snippet_response
    except Exception as e:
        logger.bind(event="service snippet get response").error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def get_user_snippets_by_date(user_id:str, tz: str, date: str, db):
    try:
        zone = ZoneInfo(tz)
        local_start_time = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=zone)
        local_end_time = local_start_time.replace(hour=23, minute=59, second=59)
        start_time = local_start_time.astimezone(ZoneInfo("UTC"))
        end_time = local_end_time.astimezone(ZoneInfo("UTC"))
        snippets = await snippet_repo.get_user_snippets_by_range(user_id, start_time, end_time, db)
        coroutines = [get_response_snippet(snippet) for snippet in snippets]
        response_snippets = await asyncio.gather(*coroutines)
        return response_snippets
    except Exception as e:
        logger.bind(event="service snippet").error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def create_snippet(user_id: str, tags: List[str], content_type: str, content: UploadFile | str, db):
    try:
        if content_type == "text":
            new_snippet = Snippet(
                user_id=user_id,
                content_type=content_type,
                content=content,
                content_key=None,
                tags=tags
            )
        else:
            date_str = datetime.utcnow().strftime("%Y-%m-%d")
            ext = os.path.splitext(content.filename)[1].lower()
            content_key = f"snippets/{user_id}/{date_str}/{str(uuid.uuid4())}{ext}"
            new_snippet = Snippet(
                user_id=user_id,
                content_type=content_type,
                content=None,
                content_key=content_key,
                tags=tags,
            )
            await s3_repo.put_object(content_key, content)
        await snippet_repo.add_snippet(new_snippet, db)
    except Exception as e:
        logger.bind(event="service snippet").error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def delete_snippet(user_id: str, snippet_id: str, db):
    try:
        target_snippet = await snippet_repo.get_snippet_by_id(snippet_id, db)
        if not target_snippet:
            raise HTTPException(status_code=404, detail="Snippet not found")
        if target_snippet.user_id != user_id:
            raise HTTPException(status_code=403, detail="Forbidden")
        delete_cnt = await snippet_repo.delete_snippet(snippet_id, db)
        if delete_cnt > 0 and target_snippet.content_type != 'text':
            await s3_repo.delete_object(target_snippet.content_key)
        return "Success"
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.bind(event="service snippet").error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
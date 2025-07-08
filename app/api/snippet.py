from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from typing import Optional, List, Any

from app.db.mongo.client import get_mongodb
from app.services.auth import get_authenticated_user_id
from app.services.snippet import (
    create_snippet,
    get_user_snippets_by_date,
    delete_snippet,
)
from app.models.snippet import (
    SnippetResponse
)

router = APIRouter()

@router.post("/", summary="Create a snippet")
async def post_snippet(
    content_type: Optional[str] = Form(None),
    content: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    tags: Optional[List[str]] = Form(None),
    user_id: str = Depends(get_authenticated_user_id),
    db: Any = Depends(get_mongodb)
):
    return await create_snippet(
        user_id=user_id,
        tags=tags,
        content_type=content_type,
        content=text if content_type == 'text' else content,
        db=db
    )

@router.delete("/{snippet_id}", summary="Delete a snippet")
async def delete_snippet_api(
    snippet_id: str,
    user_id: str = Depends(get_authenticated_user_id),
    db: Any = Depends(get_mongodb)
):
    await delete_snippet(user_id, snippet_id, db)
    return {"message": "Snippet deleted successfully"}

@router.get("/date", response_model=List[SnippetResponse], summary="Get each date's snippets with details")
async def get_today_snippets_api(
    tz: str = Query(...),
    date: str = Query(...),
    user_id: str = Depends(get_authenticated_user_id),
    db: Any = Depends(get_mongodb)
):
    return await get_user_snippets_by_date(user_id, tz, date, db)
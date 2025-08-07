from fastapi import APIRouter, Depends, Body, Query, HTTPException
from typing import Any, List
from datetime import datetime
from app.services.session import (
    create_session,
    get_user_session_by_date_range,
    get_session,
    get_current_session,
    update_session,
    delete_session
)
from app.models.session import SessionResponse, ReflectionUpdate
from app.services.auth import get_authenticated_user_id
from app.db.mongo.client import depends_get_mongodb

router = APIRouter()

@router.post("/", response_model=SessionResponse, summary="Create a session")
async def post_session_api(
    subject: str = Body(..., description="Session subject"),
    goal: str | None = Body(None, description="Session goal"),
    duration: int = Body(..., description="Focus duration in minutes"),
    break_duration: int = Body(..., description="Break duration in minutes"),
    tags: List[str] = Body(default=[], description="Tags array"),
    status: str = Body(..., description="Session status e.g., 'pending'"),
    completed: bool = Body(False, description="Completed flag"),
    created_at: str = Body(..., description="Creation timestamp, ISO format"),
    user_id: str = Depends(get_authenticated_user_id),
    db: Any = Depends(depends_get_mongodb)
):
    """
    Create a new Pomodoro session via JSON body.
    """
    session = await create_session(
        user_id=user_id,
        subject=subject,
        goal=goal,
        duration=duration,
        break_duration=break_duration,
        tags=tags,
        created_at=created_at,
        db=db
    )
    return session

@router.get("/list", response_model=List[SessionResponse], summary="Get sessions by date range")
async def get_list_of_sessions_api(
    tz: str = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...),
    user_id: str = Depends(get_authenticated_user_id),
    db: Any = Depends(depends_get_mongodb)
):
    sessions = await get_user_session_by_date_range(user_id, tz, start_date, end_date, db)
    return sessions

@router.get("/current", response_model=SessionResponse, summary="Get current session")
async def get_current_session_api(
        user_id: str = Depends(get_authenticated_user_id),
        db: Any = Depends(depends_get_mongodb)
):
    session = await get_current_session(user_id, db)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.get("/{session_id}", response_model=SessionResponse, summary="Get a session by id")
async def get_session_by_id_api(
    session_id: str,
    user_id: str = Depends(get_authenticated_user_id),
    db: Any = Depends(depends_get_mongodb)
):
    session = await get_session(user_id, session_id, db)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.put("/{session_id}/status", response_model=SessionResponse, summary="Update session status")
async def update_session_status_api(
    session_id: str,
    status: str = Body(..., description="New session status"),
    updated_at: str = Body(..., description="Update timestamp in ISO format"),
    user_id: str = Depends(get_authenticated_user_id),
    db: Any = Depends(depends_get_mongodb)
):
    updated = await update_session(
        session_id=session_id,
        user_id=user_id,
        status=status,
        updated_at=updated_at,
        db=db
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Session not found or not authorized")
    return updated

@router.put("/{session_id}", summary="Update session reflection", response_model=SessionResponse)
async def update_session_api(
    session_id: str,
    reflection: str = Body(..., description="Session reflection"),
    updated_at: str = Body(..., description="Update timestamp in ISO format"),
    user_id: str = Depends(get_authenticated_user_id),
    db: Any = Depends(depends_get_mongodb)
):
    updated = await update_session(
        session_id=session_id,
        user_id=user_id,
        reflection=reflection,
        updated_at=updated_at,
        db=db
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Session not found or not authorized")
    return updated

@router.delete("/{session_id}", summary="Delete a session")
async def delete_session_api(
    session_id: str,
    user_id: str = Depends(get_authenticated_user_id),
    db: Any = Depends(depends_get_mongodb)
):
    result = await delete_session(user_id, session_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found or not authorized")
    return {"message": "session deleted successfully"}
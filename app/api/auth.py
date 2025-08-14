from fastapi import APIRouter, Response
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.auth import create_access_token, get_authenticated_user_id
from app.services.user import create_or_update_user
from app.utils.logging import logger

router = APIRouter()

class CodePayload(BaseModel):
    code: str

@router.post("/google/callback")
async def google_callback(payload: CodePayload, response: Response, db: AsyncSession = Depends(get_db)):
    # logger.bind(event="api endpoint").info("Google callback")
    user = await create_or_update_user(
        provider="google",
        provider_code=payload.code,
        db=db
    )
    at = create_access_token(
        user_id = user.id
    )
    response.set_cookie(
        key="omood_at",
        value=at,
        httponly=True,
        max_age=3600,
        samesite="none",
        secure=True,
    )
    logger.bind(event="api endpoint").info(at)
    return {"message": "Google callback success"}


@router.get("/me")
async def me(user_id: str = Depends(get_authenticated_user_id)):
    return {"user_id": user_id}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="omood_at",
        httponly=True,
        samesite="none",
        secure=True
    )
    return {"message": "Logged out"}

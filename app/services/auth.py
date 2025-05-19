from datetime import datetime, timedelta
import jwt
from app.core.config import settings
from app.services.spotify_api.auth import get_token_with_code
from app.services.spotify_api.user import get_spotify_user_profile
from app.services.user import create_or_update_user
from fastapi import Cookie, HTTPException
from typing import Optional
from jwt.exceptions import PyJWTError
from app.utils.logging import logger

async def get_authenticated_user_id(omood_at: Optional[str] = Cookie(None)) -> str:
    if omood_at is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        payload = jwt.decode(omood_at, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        logger.bind(event="get_authenticated_user_id").info(f"user_id: {user_id}")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return user_id
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def login_with_code(code: str):
    token_dict = get_token_with_code(code)
    user_info = await get_spotify_user_profile(token_dict["access_token"])
    user = await create_or_update_user(user_info, token_dict)
    at = create_access_token(user.id)
    return at

def create_access_token(user_id: str, expires_delta: timedelta = timedelta(hours=1)):
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + expires_delta,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)